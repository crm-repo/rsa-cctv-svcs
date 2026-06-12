"""Batch 45 public EC2 admin login browser smoke support check.

This script does not automate a browser. It verifies the EC2/Nginx surface that
supports the manual browser smoke test and can optionally perform the same
Cognito login POST that the browser uses.

Safe defaults:
- Read-only mode does only GET checks and one invalid-login POST.
- Execute mode asks for the Cognito admin password with hidden input.
- No credentials are printed, stored, or written to disk.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import urllib.error
import urllib.request
from typing import Iterable


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def request_status(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict | None = None,
    token: str | None = None,
    timeout: int = 20,
) -> tuple[int | None, str]:
    data = None
    headers = {"Accept": "application/json, text/html;q=0.9, */*;q=0.8"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(_url(base_url, path), data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(4000).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(4000).decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:  # noqa: BLE001 - CLI smoke output should show network errors.
        return None, str(exc)


def expect(
    base_url: str,
    method: str,
    path: str,
    expected: Iterable[int],
    payload: dict | None = None,
    token: str | None = None,
) -> int:
    status, body = request_status(base_url, path, method=method, payload=payload, token=token)
    expected_set = set(expected)
    expected_text = ", ".join(str(item) for item in sorted(expected_set))
    if status in expected_set:
        print(f"OK: {method} {path} -> HTTP {status}")
        return 0
    print(f"FAIL: {method} {path} -> HTTP {status}; expected {expected_text}")
    print(f"  Body/error preview: {body[:800]}")
    return 1


def parse_json(body: str) -> dict:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 45 EC2 admin login browser-smoke readiness.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, e.g. http://54.179.42.39")
    parser.add_argument("--admin-email", default="", help="Cognito admin email used for optional login test.")
    parser.add_argument("--execute", action="store_true", help="Run real Cognito login POST with hidden password input.")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    issues = 0

    print("RSA CMS / Mini-CRM Batch 45 Admin Login Browser Smoke Support Check")
    print(f"Base URL: {base_url}")
    print("Mode: READ ONLY support checks" if not args.execute else "Mode: EXECUTE real Cognito login POST test")
    print("No password is printed or stored.")

    print("\n== Public site and login pages ==")
    for path in ["/", "/admin/", "/admin/login.html", "/admin/assets/js/admin-auth.js", "/admin/assets/css/admin-auth.css"]:
        issues += expect(base_url, "GET", path, [200])

    print("\n== Public auth endpoints ==")
    issues += expect(base_url, "GET", "/api/admin/auth/config", [200])
    status_body_status, status_body = request_status(base_url, "/api/admin/auth/status")
    if status_body_status == 200 and '"authenticated":false' in status_body.replace(" ", ""):
        print("OK: GET /api/admin/auth/status anonymous -> HTTP 200 authenticated=false")
    else:
        print(f"FAIL: GET /api/admin/auth/status anonymous -> HTTP {status_body_status}; expected authenticated=false")
        print(f"  Body/error preview: {status_body[:800]}")
        issues += 1

    print("\n== Invalid login should reach backend but fail authentication ==")
    issues += expect(
        base_url,
        "POST",
        "/api/admin/auth/cognito-login",
        [400, 401, 422],
        payload={"username": "batch45.invalid@example.com", "password": "DefinitelyWrong#2026"},
    )

    print("\n== Management routes must still be blocked before protected API exposure batch ==")
    blocked_paths = [
        "/api/admin/products",
        "/api/admin/categories",
        "/api/admin/brands",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    for path in blocked_paths:
        issues += expect(base_url, "GET", path, [403])

    if args.execute:
        print("\n== Real Cognito login POST check ==")
        if not args.confirm_login_test:
            print("FAIL: --confirm-login-test is required with --execute")
            issues += 1
        elif not args.admin_email:
            print("FAIL: --admin-email is required with --execute")
            issues += 1
        else:
            password = getpass.getpass("Cognito admin password: ")
            status, body = request_status(
                base_url,
                "/api/admin/auth/cognito-login",
                method="POST",
                payload={"username": args.admin_email, "password": password},
                timeout=35,
            )
            body_json = parse_json(body)
            access_token = body_json.get("access_token") or body_json.get("AccessToken")
            if status == 200 and access_token:
                print("OK: real Cognito login returned an access token")

                status2, body2 = request_status(base_url, "/api/admin/auth/status", token=access_token)
                normalized = body2.replace(" ", "").lower()
                if status2 == 200 and '"authenticated":true' in normalized:
                    print("OK: Bearer token status check shows authenticated=true")
                else:
                    print(f"FAIL: Bearer token status check -> HTTP {status2}; expected authenticated=true")
                    print(f"  Body/error preview: {body2[:1000]}")
                    issues += 1

                print("\n== Confirm protected data APIs remain blocked even with token ==")
                for path in ["/api/admin/products", "/api/customers", "/api/bookings", "/api/inquiries"]:
                    issues += expect(base_url, "GET", path, [403], token=access_token)

            elif status == 200 and ("challenge" in body.lower() or body_json.get("challenge_required")):
                print("OK: Cognito login reached backend and returned a password challenge.")
                print("Manual browser login may ask you to set a permanent password first.")
            else:
                print(f"FAIL: real Cognito login returned HTTP {status}")
                print(f"  Body/error preview: {body[:1000]}")
                issues += 1
    else:
        print("\nSKIP: real Cognito login POST test not run.")
        print("Run again with --execute --confirm-login-test after the manual browser test if needed.")

    print("\n== Manual browser smoke reminder ==")
    print(f"Open: {base_url}/admin/login.html")
    print("Login with the Cognito admin email/password. Do not share the password in chat or commit it.")
    print("Expected: login succeeds and admin session status becomes authenticated; admin data APIs still remain blocked until the next protected API batch.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 45 admin login browser smoke support check FAILED with {issues} issue(s).")
        return 1
    print("Batch 45 admin login browser smoke support check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
