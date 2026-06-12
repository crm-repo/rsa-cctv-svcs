#!/usr/bin/env python3
"""
RSA CMS / Mini-CRM Phase 8 Batch 39
Public EC2 smoke/regression check through Nginx.

Default mode is read-only: GET checks only.
Use --execute --confirm-write-test to POST public booking/inquiry smoke records.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass
class CheckResult:
    label: str
    ok: bool
    detail: str


def normalize_base_url(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    if not value:
        raise ValueError("--base-url is required")
    if not value.startswith(("http://", "https://")):
        value = f"http://{value}"
    return value.rstrip("/")


def request_http(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 8.0) -> tuple[int | None, str, str | None]:
    data = None
    headers = {"User-Agent": "rsa-cms-batch39-smoke/1.0"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            return response.getcode(), body, None
    except HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        return exc.code, body, None
    except (URLError, TimeoutError, OSError) as exc:
        return None, "", str(exc)


def preview(body: str, limit: int = 180) -> str:
    text = " ".join((body or "").split())
    return text[:limit] + ("..." if len(text) > limit else "")


def expect_status(base_url: str, method: str, path: str, expected: Iterable[int], payload: dict[str, Any] | None = None) -> CheckResult:
    expected_set = set(expected)
    status, body, err = request_http(method, f"{base_url}{path}", payload=payload)
    label = f"{method.upper()} {path}"
    if status in expected_set:
        return CheckResult(label, True, f"HTTP {status}")
    if status is None:
        return CheckResult(label, False, f"request failed: {err}")
    return CheckResult(label, False, f"HTTP {status}; body: {preview(body)}")


def expect_direct_backend_blocked(base_url: str) -> CheckResult:
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or not parsed.hostname:
        return CheckResult("Direct backend port 8000 check", True, "skipped; base URL is not plain host HTTP")
    direct_url = f"http://{parsed.hostname}:8000/api/health"
    status, body, err = request_http("GET", direct_url, timeout=4.0)
    if status is None:
        return CheckResult("GET :8000/api/health", True, f"blocked/unreachable as expected ({err})")
    if status == 200:
        return CheckResult("GET :8000/api/health", False, "HTTP 200; direct backend port is still publicly reachable")
    return CheckResult("GET :8000/api/health", True, f"HTTP {status}; not publicly usable")


def print_result(result: CheckResult) -> None:
    prefix = "OK" if result.ok else "FAIL"
    print(f"{prefix}: {result.label} -> {result.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 39 public EC2 smoke/regression check through Nginx.")
    parser.add_argument("--base-url", required=True, help="Public EC2 base URL, for example http://54.179.42.39")
    parser.add_argument("--execute", action="store_true", help="Run write checks that POST public booking/inquiry smoke records.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Required with --execute to confirm public form write tests.")
    args = parser.parse_args()

    try:
        base_url = normalize_base_url(args.base_url)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("RSA CMS / Mini-CRM Batch 39 Public EC2 Smoke Regression")
    print(f"Base URL: {base_url}")
    if args.execute:
        print("Mode: EXECUTE public write smoke tests enabled")
    else:
        print("Mode: READ ONLY GET checks only")
        print("Use --execute --confirm-write-test to test public booking/inquiry POST endpoints.")

    all_results: list[CheckResult] = []

    print("\n== Public static pages ==")
    for path in ["/", "/products.html", "/promotions.html", "/brands.html", "/about.html", "/services.html", "/contact-us.html", "/booking.html"]:
        result = expect_status(base_url, "GET", path, {200})
        print_result(result)
        all_results.append(result)

    print("\n== Public read APIs ==")
    public_api_paths = [
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
    for path in public_api_paths:
        result = expect_status(base_url, "GET", path, {200})
        print_result(result)
        all_results.append(result)

    print("\n== Blocked public admin/management surfaces ==")
    blocked_paths = [
        "/admin/",
        "/api/admin/products",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    for path in blocked_paths:
        result = expect_status(base_url, "GET", path, {403})
        print_result(result)
        all_results.append(result)

    print("\n== Direct backend port check ==")
    direct_result = expect_direct_backend_blocked(base_url)
    print_result(direct_result)
    all_results.append(direct_result)

    if args.execute and args.confirm_write_test:
        print("\n== Public form write smoke tests ==")
        stamp = int(time.time())
        future_date = (date.today() + timedelta(days=30)).isoformat()
        booking_payload = {
            "customer_name": "Batch 39 Public Booking Smoke",
            "contact_number": "+63 919 139 3900",
            "email": f"batch39.booking.{stamp}@example.com",
            "address": "Batch 39 EC2 public smoke test address",
            "preferred_date": future_date,
            "preferred_time": "Morning",
            "service_interest": "CCTV Installation",
            "notes": "Batch 39 public EC2 POST smoke test.",
        }
        inquiry_payload = {
            "customer_name": "Batch 39 Public Inquiry Smoke",
            "contact_number": "0919 139 3901",
            "email": f"batch39.inquiry.{stamp}@example.com",
            "subject": "Batch 39 public inquiry smoke test",
            "message": "Testing public inquiry creation through Nginx lockdown.",
            "source_page": "batch39-public-ec2-smoke",
        }
        for method, path, payload in [
            ("POST", "/api/bookings", booking_payload),
            ("POST", "/api/inquiries", inquiry_payload),
        ]:
            result = expect_status(base_url, method, path, {200, 201}, payload=payload)
            print_result(result)
            all_results.append(result)
    elif args.execute:
        print("\nSKIP: --execute was provided without --confirm-write-test, so public write checks were not run.")
    else:
        print("\nSKIP: public booking/inquiry POST checks not run in read-only mode.")

    failures = [result for result in all_results if not result.ok]
    print("\n== Summary ==")
    if failures:
        print(f"Batch 39 public EC2 smoke regression completed with {len(failures)} issue(s).")
        for failure in failures:
            print(f"- {failure.label}: {failure.detail}")
        return 1

    print("Batch 39 public EC2 smoke regression PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
