"""Batch 47 authenticated admin API/browser smoke check for EC2.

Read-only mode verifies that public pages and admin login assets are reachable, anonymous
admin/CRM API calls are rejected, and developer surfaces are blocked.

Execute mode performs a real Cognito login through the public Nginx endpoint, then verifies
that authenticated admin/CRM API requests return HTTP 200 with the bearer token. The password
is prompted using hidden input and is never printed or stored.
"""

from __future__ import annotations

import argparse
import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterable


PUBLIC_PATHS = [
    "/",
    "/products.html",
    "/promotions.html",
    "/brands.html",
    "/about.html",
    "/services.html",
    "/contact-us.html",
    "/booking.html",
]

PUBLIC_API_PATHS = [
    "/api/health",
    "/api/products",
    "/api/brands",
    "/api/categories",
    "/api/key-features",
    "/api/package-banners",
    "/api/pages/about",
    "/api/pages/contact",
    "/api/pages/services",
    "/api/contact",
    "/api/contact-persons",
    "/api/social-media",
]

ADMIN_UI_AUTH_PATHS = [
    "/admin/",
    "/admin/index.html",
    "/admin/login.html",
    "/admin/assets/js/admin-auth.js",
    "/admin/assets/js/admin-api.js",
    "/admin/assets/css/admin-auth.css",
    "/api/admin/auth/config",
    "/api/admin/auth/status",
]

PROTECTED_API_PATHS = [
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

DEVELOPER_SURFACES = [
    "/docs",
    "/redoc",
    "/openapi.json",
]


class SmokeError(Exception):
    """Raised for local smoke helper errors."""


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def redact_sensitive(text: str) -> str:
    """Redact bearer/JWT-style tokens from smoke-test output."""
    if not text:
        return text
    text = re.sub(r'("access_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    text = re.sub(r'("id_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    text = re.sub(r'("refresh_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    return text


def http_status(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict | None = None,
    token: str | None = None,
    timeout: int = 25,
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
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
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
    print(f"  Body/error preview: {redact_sensitive(body[:900])}")
    return 1


def parse_json(body: str, context: str) -> dict:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"{context} response was not JSON: {redact_sensitive(body[:900])}") from exc
    if not isinstance(parsed, dict):
        raise SmokeError(f"{context} response was not a JSON object: {redact_sensitive(body[:900])}")
    return parsed


def cognito_login(base_url: str, email: str) -> tuple[str | None, int]:
    password = getpass.getpass("Cognito admin password: ")
    status, body = http_status(
        base_url,
        "/api/admin/auth/cognito-login",
        method="POST",
        payload={"username": email, "password": password},
        timeout=40,
    )
    if status != 200:
        print(f"FAIL: Cognito login returned HTTP {status}")
        print(f"  Body/error preview: {redact_sensitive(body[:1200])}")
        return None, 1

    try:
        result = parse_json(body, "Cognito login")
    except SmokeError as exc:
        print(f"FAIL: {exc}")
        return None, 1

    if result.get("challenge_required"):
        print("FAIL: Cognito login returned a password challenge.")
        print("Complete the temporary-password change in the browser first, then rerun this check.")
        return None, 1

    token = result.get("access_token")
    if not token:
        print("FAIL: Cognito login response did not include access_token")
        print(f"  Body preview: {redact_sensitive(body[:1200])}")
        return None, 1

    print("OK: Cognito login returned access token")
    return str(token), 0


def check_authenticated_status(base_url: str, token: str) -> int:
    status, body = http_status(base_url, "/api/admin/auth/status", token=token)
    if status != 200:
        print(f"FAIL: GET /api/admin/auth/status with token -> HTTP {status}; expected 200")
        print(f"  Body/error preview: {redact_sensitive(body[:900])}")
        return 1
    try:
        result = parse_json(body, "Authenticated status")
    except SmokeError as exc:
        print(f"FAIL: {exc}")
        return 1
    if result.get("authenticated") is not True:
        print("FAIL: authenticated status did not return authenticated=true")
        print(f"  Body preview: {redact_sensitive(body[:900])}")
        return 1
    print("OK: GET /api/admin/auth/status with token -> authenticated=true")
    return 0


def check_direct_backend_port_blocked(base_url: str) -> int:
    parsed = urllib.parse.urlparse(base_url)
    if not parsed.hostname:
        print("SKIP: could not determine hostname for direct :8000 check")
        return 0
    direct_base = f"{parsed.scheme or 'http'}://{parsed.hostname}:8000"
    status, body = http_status(direct_base, "/api/health", timeout=8)
    if status is None:
        print(f"OK: direct backend port :8000 is blocked/unreachable as expected ({body})")
        return 0
    print(f"FAIL: direct backend port :8000 returned HTTP {status}; expected blocked/unreachable")
    print(f"  Body preview: {redact_sensitive(body[:500])}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 47 authenticated admin API/browser smoke check for EC2.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, e.g. http://13.229.227.89")
    parser.add_argument("--admin-email", default="", help="Cognito admin email for execute login test.")
    parser.add_argument("--execute", action="store_true", help="Run real Cognito login and authenticated admin API checks.")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute.")
    parser.add_argument("--skip-direct-port-check", action="store_true", help="Skip checking direct public :8000 reachability.")
    args = parser.parse_args()

    issues = 0
    base_url = args.base_url.rstrip("/")

    print("RSA CMS / Mini-CRM Batch 47 Authenticated Admin API Browser Smoke Check")
    print(f"Base URL: {base_url}")
    print("Mode: READ ONLY support/anonymous checks" if not args.execute else "Mode: EXECUTE real Cognito login/authenticated admin API checks")
    print("No password is printed or stored.")

    print("\n== Public static pages ==")
    for path in PUBLIC_PATHS:
        issues += expect(base_url, "GET", path, [200])

    print("\n== Public read APIs ==")
    for path in PUBLIC_API_PATHS:
        issues += expect(base_url, "GET", path, [200])

    print("\n== Admin UI/auth pages and endpoints ==")
    for path in ADMIN_UI_AUTH_PATHS:
        issues += expect(base_url, "GET", path, [200])
    issues += expect(
        base_url,
        "POST",
        "/api/admin/auth/cognito-login",
        [400, 401, 422],
        payload={"username": "batch47.invalid@example.com", "password": "DefinitelyWrong#2026"},
    )

    print("\n== Anonymous protected admin/CRM APIs ==")
    for path in PROTECTED_API_PATHS:
        issues += expect(base_url, "GET", path, [401])

    print("\n== Blocked developer surfaces ==")
    for path in DEVELOPER_SURFACES:
        issues += expect(base_url, "GET", path, [403])

    if not args.skip_direct_port_check:
        print("\n== Direct backend port check ==")
        issues += check_direct_backend_port_blocked(base_url)

    if args.execute:
        print("\n== Real Cognito login and authenticated protected API checks ==")
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
                issues += check_authenticated_status(base_url, token)
                for path in PROTECTED_API_PATHS:
                    issues += expect(base_url, "GET", path, [200], token=token)
    else:
        print("\nSKIP: real Cognito login/authenticated admin API checks not run.")
        print("Run again with --execute --confirm-login-test after manual browser login works.")

    print("\n== Manual browser smoke reminders ==")
    print(f"Open: {base_url}/admin/login.html")
    print("Login with the Cognito admin email/password. Do not share the password in chat or commit it.")
    print("Expected: admin session authenticated; admin pages can load data; logout returns to login.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 47 authenticated admin API/browser smoke check FAILED with {issues} issue(s).")
        return 1
    print("Batch 47 authenticated admin API/browser smoke check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
