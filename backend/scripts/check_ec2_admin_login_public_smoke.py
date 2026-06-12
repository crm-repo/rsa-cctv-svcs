"""Batch 44 public smoke check for protected admin-login exposure.

This script is read-only by default except for an optional Cognito login POST test.
It verifies that Nginx exposes the admin static login surface and admin auth
endpoints while keeping admin data APIs blocked until the protected API batch.
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


def http_status(base_url: str, path: str, method: str = "GET", payload: dict | None = None, timeout: int = 15) -> tuple[int | None, str]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(_url(base_url, path), data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(800).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(800).decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:  # noqa: BLE001 - CLI smoke output should show any network error.
        return None, str(exc)


def expect(base_url: str, method: str, path: str, expected: Iterable[int], payload: dict | None = None) -> int:
    status, body = http_status(base_url, path, method=method, payload=payload)
    expected_set = set(expected)
    expected_text = ", ".join(str(item) for item in sorted(expected_set))
    if status in expected_set:
        print(f"OK: {method} {path} -> HTTP {status}")
        return 0
    print(f"FAIL: {method} {path} -> HTTP {status}; expected {expected_text}")
    print(f"  Body/error preview: {body[:500]}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 44 public admin login exposure through EC2/Nginx.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, e.g. http://54.179.42.39")
    parser.add_argument("--admin-email", default="", help="Optional Cognito admin email for execute login test.")
    parser.add_argument("--execute", action="store_true", help="Run Cognito login POST test with entered password.")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    issues = 0
    base_url = args.base_url.rstrip("/")

    print("RSA CMS / Mini-CRM Batch 44 public admin-login smoke check")
    print(f"Base URL: {base_url}")
    print("Mode: READ ONLY" if not args.execute else "Mode: EXECUTE Cognito login POST test enabled")

    print("\n== Public website/API checks ==")
    for path in ["/", "/products.html", "/booking.html", "/api/health", "/api/products", "/api/brands"]:
        issues += expect(base_url, "GET", path, [200])

    print("\n== Admin UI/auth exposure checks ==")
    for path in ["/admin/", "/admin/login.html", "/admin/assets/js/admin-auth.js", "/api/admin/auth/config", "/api/admin/auth/status"]:
        issues += expect(base_url, "GET", path, [200])

    issues += expect(
        base_url,
        "POST",
        "/api/admin/auth/cognito-login",
        [400, 401, 422],
        payload={"username": "batch44.invalid@example.com", "password": "DefinitelyWrong#2026"},
    )

    print("\n== Still-blocked admin/management surfaces ==")
    for path in [
        "/api/admin/products",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]:
        issues += expect(base_url, "GET", path, [403])

    if args.execute:
        print("\n== Optional real Cognito login check ==")
        if not args.confirm_login_test:
            print("FAIL: --confirm-login-test is required with --execute")
            issues += 1
        elif not args.admin_email:
            print("FAIL: --admin-email is required with --execute")
            issues += 1
        else:
            password = getpass.getpass("Cognito admin password: ")
            status, body = http_status(
                base_url,
                "/api/admin/auth/cognito-login",
                method="POST",
                payload={"username": args.admin_email, "password": password},
                timeout=30,
            )
            if status == 200 and '"access_token"' in body:
                print("OK: real Cognito login returned an access token")
            elif status == 200 and "challenge_required" in body:
                print("OK: Cognito login reached backend and returned a password challenge")
            else:
                print(f"FAIL: Cognito login returned HTTP {status}")
                print(f"  Body/error preview: {body[:800]}")
                issues += 1
    else:
        print("\nSKIP: real Cognito login POST test not run. Use --execute --confirm-login-test to test it.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 44 public admin-login smoke check FAILED with {issues} issue(s).")
        return 1
    print("Batch 44 public admin-login smoke check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
