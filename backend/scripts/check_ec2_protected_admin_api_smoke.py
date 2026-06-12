"""Batch 46 public protected-admin-API smoke regression.

Read-only mode verifies public pages, login/auth endpoints, anonymous protected API
401 behavior, and blocked developer docs.

Execute mode logs in with Cognito, then verifies selected protected admin/CRM APIs
return HTTP 200 with the Cognito bearer token. The password is prompted with hidden input
and never printed or stored.
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


def http_status(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict | None = None,
    token: str | None = None,
    timeout: int = 20,
) -> tuple[int | None, str]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(_url(base_url, path), data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(1000).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(1000).decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:  # noqa: BLE001 - smoke output should show network errors.
        return None, str(exc)


def expect(base_url: str, method: str, path: str, expected: Iterable[int], payload: dict | None = None, token: str | None = None) -> int:
    status, body = http_status(base_url, path, method=method, payload=payload, token=token)
    expected_set = set(expected)
    expected_text = ", ".join(str(item) for item in sorted(expected_set))
    if status in expected_set:
        print(f"OK: {method} {path} -> HTTP {status}")
        return 0
    print(f"FAIL: {method} {path} -> HTTP {status}; expected {expected_text}")
    print(f"  Body/error preview: {body[:700]}")
    return 1


def cognito_login(base_url: str, email: str) -> tuple[str | None, int]:
    password = getpass.getpass("Cognito admin password: ")
    status, body = http_status(
        base_url,
        "/api/admin/auth/cognito-login",
        method="POST",
        payload={"username": email, "password": password},
        timeout=35,
    )
    if status != 200:
        print(f"FAIL: Cognito login returned HTTP {status}")
        print(f"  Body/error preview: {body[:900]}")
        return None, 1

    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        print("FAIL: Cognito login response was not JSON")
        print(f"  Body preview: {body[:900]}")
        return None, 1

    if result.get("challenge_required"):
        print("FAIL: Cognito login returned a password challenge. Complete the password change in the browser first, then rerun.")
        return None, 1

    token = result.get("access_token")
    if not token:
        print("FAIL: Cognito login response did not include access_token")
        print(f"  Body preview: {body[:900]}")
        return None, 1

    print("OK: Cognito login returned access token")
    return token, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 46 protected admin API exposure through EC2/Nginx.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, e.g. http://13.229.227.89")
    parser.add_argument("--admin-email", default="", help="Cognito admin email for execute login test.")
    parser.add_argument("--execute", action="store_true", help="Run real Cognito login and authenticated admin API checks.")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    issues = 0
    base_url = args.base_url.rstrip("/")

    print("RSA CMS / Mini-CRM Batch 46 protected admin API smoke check")
    print(f"Base URL: {base_url}")
    print("Mode: READ ONLY anonymous/protection checks" if not args.execute else "Mode: EXECUTE Cognito login/admin API checks enabled")

    print("\n== Public website/API checks ==")
    for path in ["/", "/products.html", "/booking.html", "/api/health", "/api/products", "/api/brands", "/api/pages/contact"]:
        issues += expect(base_url, "GET", path, [200])

    print("\n== Admin UI/auth exposure checks ==")
    for path in ["/admin/", "/admin/login.html", "/admin/assets/js/admin-auth.js", "/api/admin/auth/config", "/api/admin/auth/status"]:
        issues += expect(base_url, "GET", path, [200])

    issues += expect(
        base_url,
        "POST",
        "/api/admin/auth/cognito-login",
        [400, 401, 422],
        payload={"username": "batch46.invalid@example.com", "password": "DefinitelyWrong#2026"},
    )

    print("\n== Anonymous protected API checks ==")
    protected_paths = [
        "/api/admin/products",
        "/api/admin/categories",
        "/api/admin/brands",
        "/api/admin/key-features",
        "/api/admin/about",
        "/api/admin/project-gallery",
        "/api/admin/services",
        "/api/admin/contact-us",
        "/api/admin/media/config",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
    ]
    for path in protected_paths:
        issues += expect(base_url, "GET", path, [401])

    print("\n== Still-blocked developer surfaces ==")
    for path in ["/docs", "/redoc", "/openapi.json"]:
        issues += expect(base_url, "GET", path, [403])

    token: str | None = None
    if args.execute:
        print("\n== Real Cognito login and authenticated API checks ==")
        if not args.confirm_login_test:
            print("FAIL: --confirm-login-test is required with --execute")
            issues += 1
        elif not args.admin_email:
            print("FAIL: --admin-email is required with --execute")
            issues += 1
        else:
            token, login_issues = cognito_login(base_url, args.admin_email)
            issues += login_issues

        if token:
            for path in protected_paths:
                issues += expect(base_url, "GET", path, [200], token=token)
    else:
        print("\nSKIP: real Cognito login/admin API checks not run. Use --execute --confirm-login-test after manual browser login works.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 46 protected admin API smoke check FAILED with {issues} issue(s).")
        return 1
    print("Batch 46 protected admin API smoke check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
