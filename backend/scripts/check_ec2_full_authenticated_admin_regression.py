"""Batch 48 full authenticated admin EC2 regression.

Safe by default:
- Read-only mode checks public pages/APIs, admin UI availability, anonymous 401 protection,
  developer-surface blocking, and direct :8000 blocking.
- Execute mode logs in through Cognito, verifies authenticated admin/CRM reads, and confirms
  public form POST exceptions still work.
- Write regression requires --confirm-write-test in addition to --execute and creates small
  non-destructive hidden/test records in DynamoDB via the public EC2/Nginx endpoint.

Passwords are prompted with hidden input and are never printed or stored. Token fields are
redacted from any error output.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterable


PUBLIC_PAGES = [
    "/",
    "/products.html",
    "/promotions.html",
    "/brands.html",
    "/about.html",
    "/services.html",
    "/contact-us.html",
    "/booking.html",
]

ADMIN_PAGES = [
    "/admin/",
    "/admin/index.html",
    "/admin/login.html",
    "/admin/products.html",
    "/admin/categories.html",
    "/admin/brands.html",
    "/admin/key-features.html",
    "/admin/customers.html",
    "/admin/bookings.html",
    "/admin/inquiries.html",
    "/admin/about.html",
    "/admin/project-gallery.html",
    "/admin/services.html",
    "/admin/contact-us.html",
]

PUBLIC_API_PATHS = [
    "/api/health",
    "/api/products",
    "/api/products?sale=true",
    "/api/products?category=packages",
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

ADMIN_AUTH_PATHS = [
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


class RegressionError(Exception):
    """Raised for regression helper errors."""


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def redact_sensitive(text: str) -> str:
    """Redact token-like values from output."""
    if not text:
        return text
    text = re.sub(r'("access_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    text = re.sub(r'("id_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    text = re.sub(r'("refresh_token"\s*:\s*")([^"]+)(")', r'\1<redacted>\3', text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9_\-\.]+", "Bearer <redacted>", text)
    return text


def http_request(
    base_url: str,
    path: str,
    method: str = "GET",
    payload: dict | None = None,
    token: str | None = None,
    timeout: int = 30,
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


def parse_json(body: str, context: str) -> dict:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RegressionError(f"{context} response was not JSON: {redact_sensitive(body[:1000])}") from exc
    if not isinstance(parsed, dict):
        raise RegressionError(f"{context} response was not a JSON object: {redact_sensitive(body[:1000])}")
    return parsed


def items_count(payload: dict) -> int:
    for key in ("items", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
    return 0


def expect_status(
    base_url: str,
    method: str,
    path: str,
    expected: Iterable[int],
    payload: dict | None = None,
    token: str | None = None,
    label: str | None = None,
) -> tuple[int, str]:
    status, body = http_request(base_url, path, method=method, payload=payload, token=token)
    expected_set = set(expected)
    expected_text = ", ".join(str(item) for item in sorted(expected_set))
    display = label or f"{method} {path}"
    if status in expected_set:
        print(f"OK: {display} -> HTTP {status}")
        return 0, body
    print(f"FAIL: {display} -> HTTP {status}; expected {expected_text}")
    print(f"  Body/error preview: {redact_sensitive(body[:1000])}")
    return 1, body


def expect_json(
    base_url: str,
    method: str,
    path: str,
    expected: Iterable[int],
    payload: dict | None = None,
    token: str | None = None,
    label: str | None = None,
) -> tuple[int, dict | None]:
    issue, body = expect_status(base_url, method, path, expected, payload=payload, token=token, label=label)
    if issue:
        return issue, None
    try:
        return 0, parse_json(body, label or f"{method} {path}")
    except RegressionError as exc:
        print(f"FAIL: {exc}")
        return 1, None


def check_direct_backend_port_blocked(base_url: str) -> int:
    parsed = urllib.parse.urlparse(base_url)
    if not parsed.hostname:
        print("SKIP: could not determine hostname for direct :8000 check")
        return 0
    direct_base = f"{parsed.scheme or 'http'}://{parsed.hostname}:8000"
    status, body = http_request(direct_base, "/api/health", timeout=8)
    if status is None:
        print(f"OK: direct backend port :8000 is blocked/unreachable as expected ({body})")
        return 0
    print(f"FAIL: direct backend port :8000 returned HTTP {status}; expected blocked/unreachable")
    print(f"  Body preview: {redact_sensitive(body[:500])}")
    return 1


def cognito_login(base_url: str, email: str) -> tuple[str | None, int]:
    password = getpass.getpass("Cognito admin password: ")
    status, body = http_request(
        base_url,
        "/api/admin/auth/cognito-login",
        method="POST",
        payload={"username": email, "password": password},
        timeout=45,
    )
    if status != 200:
        print(f"FAIL: Cognito login returned HTTP {status}")
        print(f"  Body/error preview: {redact_sensitive(body[:1200])}")
        return None, 1
    try:
        result = parse_json(body, "Cognito login")
    except RegressionError as exc:
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
    issue, payload = expect_json(base_url, "GET", "/api/admin/auth/status", [200], token=token, label="authenticated status")
    if issue or payload is None:
        return 1
    if payload.get("authenticated") is not True:
        print("FAIL: authenticated status did not return authenticated=true")
        print(f"  Body preview: {redact_sensitive(json.dumps(payload)[:1000])}")
        return 1
    print("OK: authenticated status returned authenticated=true")
    return 0


def run_read_only_checks(base_url: str, skip_direct_port_check: bool) -> int:
    issues = 0

    print("\n== Public static pages ==")
    for path in PUBLIC_PAGES:
        issues += expect_status(base_url, "GET", path, [200])[0]

    print("\n== Admin static/login pages ==")
    for path in ADMIN_PAGES:
        issues += expect_status(base_url, "GET", path, [200])[0]

    print("\n== Public read APIs ==")
    for path in PUBLIC_API_PATHS:
        issues += expect_status(base_url, "GET", path, [200])[0]

    print("\n== Public auth endpoints ==")
    for path in ADMIN_AUTH_PATHS:
        issues += expect_status(base_url, "GET", path, [200])[0]
    issues += expect_status(
        base_url,
        "POST",
        "/api/admin/auth/cognito-login",
        [400, 401, 422],
        payload={"username": "batch48.invalid@example.com", "password": "DefinitelyWrong#2026"},
        label="invalid login rejected",
    )[0]

    print("\n== Anonymous protected admin/CRM APIs ==")
    for path in PROTECTED_API_PATHS:
        issues += expect_status(base_url, "GET", path, [401])[0]

    print("\n== Blocked developer surfaces ==")
    for path in DEVELOPER_SURFACES:
        issues += expect_status(base_url, "GET", path, [403])[0]

    if not skip_direct_port_check:
        print("\n== Direct backend port check ==")
        issues += check_direct_backend_port_blocked(base_url)

    return issues


def run_authenticated_read_checks(base_url: str, token: str) -> int:
    issues = 0
    print("\n== Authenticated admin session check ==")
    issues += check_authenticated_status(base_url, token)

    print("\n== Authenticated protected admin/CRM API reads ==")
    for path in PROTECTED_API_PATHS:
        issue, payload = expect_json(base_url, "GET", path, [200], token=token, label=f"authenticated GET {path}")
        issues += issue
        if payload is not None:
            print(f"    Records visible: {items_count(payload)}")
    return issues


def post_json(base_url: str, path: str, payload: dict, token: str | None, expected: Iterable[int], id_field: str, label: str) -> tuple[int, dict | None]:
    issue, result = expect_json(base_url, "POST", path, expected, payload=payload, token=token, label=f"{label} create")
    if issue or result is None:
        return 1, None
    item_id = result.get(id_field)
    if not item_id:
        print(f"FAIL: {label} create did not return {id_field}")
        print(f"  Body preview: {redact_sensitive(json.dumps(result)[:1000])}")
        return 1, None
    print(f"OK: {label} created {item_id}")
    return 0, result


def put_json(base_url: str, path: str, payload: dict, token: str | None, expected: Iterable[int], label: str) -> tuple[int, dict | None]:
    issue, result = expect_json(base_url, "PUT", path, expected, payload=payload, token=token, label=f"{label} update")
    if issue or result is None:
        return 1, None
    print(f"OK: {label} updated")
    return 0, result


def run_public_form_write_checks(base_url: str) -> tuple[int, dict[str, str]]:
    issues = 0
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    ids: dict[str, str] = {}

    print("\n== Public form POST exceptions through protected middleware ==")
    booking_payload = {
        "customer_name": f"Batch 48 Public Booking Smoke {suffix}",
        "contact_number": "+63 919 148 4800",
        "email": f"batch48.booking.{suffix}@example.com",
        "address": "Batch 48 EC2 authenticated regression address",
        "preferred_date": "2026-12-30",
        "preferred_time": "Morning",
        "service_interest": "CCTV Installation",
        "notes": "Batch 48 public form POST regression.",
    }
    issue, booking = post_json(base_url, "/api/bookings", booking_payload, None, [200, 201], "booking_id", "public booking")
    issues += issue
    if booking:
        ids["booking_id"] = str(booking["booking_id"])

    inquiry_payload = {
        "customer_name": f"Batch 48 Public Inquiry Smoke {suffix}",
        "contact_number": "0919 148 4801",
        "email": f"batch48.inquiry.{suffix}@example.com",
        "subject": "Batch 48 public inquiry regression",
        "message": "Testing public inquiry creation after protected admin API exposure.",
        "source_page": "batch48-authenticated-admin-regression",
    }
    issue, inquiry = post_json(base_url, "/api/inquiries", inquiry_payload, None, [200, 201], "inquiry_id", "public inquiry")
    issues += issue
    if inquiry:
        ids["inquiry_id"] = str(inquiry["inquiry_id"])

    return issues, ids


def run_authenticated_write_checks(base_url: str, token: str, public_ids: dict[str, str]) -> int:
    issues = 0
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    print("\n== Authenticated lead/CRM update checks ==")
    booking_id = public_ids.get("booking_id")
    if booking_id:
        issue, _ = put_json(base_url, f"/api/bookings/{booking_id}", {
            "status": "Scheduled",
            "assigned_person": "Batch 48 Admin",
            "comments": "Updated by Batch 48 authenticated EC2 regression.",
        }, token, [200], "booking")
        issues += issue
    else:
        print("SKIP: booking update because public booking create failed")

    inquiry_id = public_ids.get("inquiry_id")
    if inquiry_id:
        issue, _ = put_json(base_url, f"/api/inquiries/{inquiry_id}", {
            "status": "Replied",
            "assigned_person": "Batch 48 Admin",
        }, token, [200], "inquiry")
        issues += issue
    else:
        print("SKIP: inquiry update because public inquiry create failed")

    print("\n== Authenticated catalog create/update checks ==")
    issue, category = post_json(base_url, "/api/admin/categories", {
        "category_name": f"Batch 48 Test Category {suffix}",
        "category_key": f"batch48-test-{suffix}",
        "category_prefix": "B48T",
        "display_seq": 98,
        "show_flag": "N",
        "description": "Hidden Batch 48 authenticated EC2 regression category.",
    }, token, [200, 201], "category_id", "category")
    issues += issue

    issue, brand = post_json(base_url, "/api/admin/brands", {
        "brand_name": f"Batch 48 Test Brand {suffix}",
        "brand_key": f"batch48-brand-{suffix}",
        "display_seq": 98,
        "show_flag": "N",
        "description": "Hidden Batch 48 authenticated EC2 regression brand.",
    }, token, [200, 201], "brand_id", "brand")
    issues += issue

    issue, feature = post_json(base_url, "/api/admin/key-features", {
        "key_feat_name": f"Batch 48 Feature {suffix}",
    }, token, [200, 201], "key_feat_id", "key feature")
    issues += issue

    if category and brand and feature:
        issue, product = post_json(base_url, "/api/admin/products", {
            "category_key": category["category_key"],
            "product_brand_key": brand["brand_key"],
            "subcategory": "Batch 48 Test Product",
            "feature_01": "Batch 48 Feature One",
            "feature_02": "Batch 48 Feature Two",
            "feature_03": "Batch 48 Feature Three",
            "price": 4848,
            "sale_price": 4648,
            "stock_quantity": 4,
            "low_stock_threshold": 2,
            "show_flag": "N",
            "show_pack_flag": "N",
            "description": "Hidden Batch 48 authenticated EC2 regression product.",
            "image_path": "uploads/products/batch48-product-placeholder.png",
        }, token, [200, 201], "product_id", "product")
        issues += issue
        if product:
            issues += put_json(base_url, f"/api/admin/products/{product['product_id']}", {
                "sale_price": 4548,
                "stock_quantity": 5,
                "description": "Updated by Batch 48 authenticated EC2 regression.",
            }, token, [200], "product")[0]
    else:
        print("SKIP: product create because category/brand/key feature setup failed")

    print("\n== Authenticated CMS create/update checks ==")
    issue, service = post_json(base_url, "/api/admin/services", {
        "show_flag": "N",
        "display_seq": 98,
        "service_title": f"Batch 48 Test Service {suffix}",
        "short_description": "Hidden Batch 48 authenticated EC2 regression service.",
        "service_description": "Created by Batch 48 authenticated EC2 regression.",
        "cta_label": "Test CTA",
        "cta_url": "contact-us.html",
        "updated_by": "batch48-regression",
    }, token, [200, 201], "service_id", "service")
    issues += issue
    if service:
        issues += put_json(base_url, f"/api/admin/services/{service['service_id']}", {
            "short_description": "Updated by Batch 48 authenticated EC2 regression.",
            "updated_by": "batch48-regression",
        }, token, [200], "service")[0]

    issue, gallery = post_json(base_url, "/api/admin/project-gallery", {
        "show_flag": "N",
        "display_seq": 98,
        "project_title": f"Batch 48 Test Project {suffix}",
        "project_description": "Hidden Batch 48 authenticated EC2 regression gallery item.",
        "image_path": "uploads/project-gallery/batch48-test.jpg",
        "alt_text": "Batch 48 test project",
        "updated_by": "batch48-regression",
    }, token, [200, 201], "project_id", "project gallery item")
    issues += issue
    if gallery:
        issues += put_json(base_url, f"/api/admin/project-gallery/{gallery['project_id']}", {
            "project_description": "Updated by Batch 48 authenticated EC2 regression.",
            "updated_by": "batch48-regression",
        }, token, [200], "project gallery item")[0]

    issue, contact = post_json(base_url, "/api/admin/contact-us", {
        "show_flag": "N",
        "contact_type": "Contact Person",
        "display_seq": 98,
        "person_image_path": "uploads/contact-persons/batch48-contact.jpg",
        "person_name": f"Batch 48 Contact Person {suffix}",
        "position_title": "Regression Tester",
        "department": "QA",
        "phone_number": "+63 919 148 4802",
        "email_address": f"batch48.contact.{suffix}@example.com",
        "updated_by": "batch48-regression",
    }, token, [200, 201], "contact_us_id", "contact person")
    issues += issue
    if contact:
        issues += put_json(base_url, f"/api/admin/contact-us/{contact['contact_us_id']}", {
            "position_title": "Updated Regression Tester",
            "updated_by": "batch48-regression",
        }, token, [200], "contact person")[0]

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 48 full authenticated admin EC2 regression.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, e.g. http://13.229.227.89")
    parser.add_argument("--admin-email", default="", help="Cognito admin email for execute login tests.")
    parser.add_argument("--execute", action="store_true", help="Run real Cognito login and authenticated read checks.")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Also create/update small hidden regression records.")
    parser.add_argument("--skip-direct-port-check", action="store_true", help="Skip checking direct public :8000 reachability.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    issues = 0

    print("RSA CMS / Mini-CRM Batch 48 Full Authenticated Admin EC2 Regression")
    print(f"Base URL: {base_url}")
    if args.execute and args.confirm_write_test:
        print("Mode: EXECUTE authenticated read + write regression")
    elif args.execute:
        print("Mode: EXECUTE authenticated read regression")
    else:
        print("Mode: READ ONLY public/anonymous support checks")
    print("No password/token is printed or stored.")

    issues += run_read_only_checks(base_url, skip_direct_port_check=args.skip_direct_port_check)

    token: str | None = None
    if args.execute:
        print("\n== Cognito login ==")
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
                issues += run_authenticated_read_checks(base_url, token)
                if args.confirm_write_test:
                    public_issues, public_ids = run_public_form_write_checks(base_url)
                    issues += public_issues
                    issues += run_authenticated_write_checks(base_url, token, public_ids)
    else:
        print("\nSKIP: authenticated login/read/write checks not run.")
        print("Run again with --execute --confirm-login-test after browser login works.")
        print("Add --confirm-write-test only when you intentionally want live DynamoDB test records.")

    print("\n== Browser smoke reminders ==")
    print(f"Open: {base_url}/admin/login.html")
    print("Login with the Cognito admin email/password. Do not share the password in chat or commit it.")
    print("Verify key admin pages load data and logout returns to login.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 48 full authenticated admin EC2 regression FAILED with {issues} issue(s).")
        return 1
    print("Batch 48 full authenticated admin EC2 regression PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
