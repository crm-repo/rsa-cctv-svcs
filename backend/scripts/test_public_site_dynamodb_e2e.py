"""Batch 16 public-site DynamoDB regression test for RSA CMS / Mini-CRM.

This script is intentionally local-first and safe by default.

Default behavior:
- Performs read-only API checks against the locally running backend.
- Performs read-only frontend page checks against the locally running static server.
- Does not create records unless --execute --confirm-write-test are provided.

Execute behavior:
- Creates a small booking and inquiry through the public API.
- Verifies the created records exist in DynamoDB.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from typing import Any
from urllib import request, error

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:  # Optional local .env support.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import get_aws_region, get_dynamodb_table, get_table_name  # noqa: E402


class CheckFailure(Exception):
    """Raised when a required regression check fails."""


def _now_suffix() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def _http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 15) -> tuple[int, Any]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=body, headers=headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return response.status, None
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed


def _http_status(url: str, timeout: int = 15) -> int:
    req = request.Request(url, headers={"Accept": "text/html,application/json"}, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            response.read(128)
            return response.status
    except error.HTTPError as exc:
        return exc.code


def _count_items(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("items", "data", "results", "products", "brands", "categories", "services"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
        # For grouped CMS responses, any non-empty dictionary counts as one response.
        return 1 if payload else 0
    return 0


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def _print_pass(message: str) -> None:
    print(f"PASS  {message}")


def _print_warn(message: str) -> None:
    print(f"WARN  {message}")


def check_api_reads(api_base: str) -> None:
    print("\nAPI read checks")
    endpoints = [
        ("health", "/health", False),
        ("products", "/products", True),
        ("sale products", "/products?sale=true", False),
        ("package banners", "/package-banners", False),
        ("brands", "/brands", True),
        ("categories", "/categories", True),
        ("key features", "/key-features", True),
        ("about page", "/pages/about", True),
        ("services page", "/pages/services", True),
        ("contact page", "/pages/contact", True),
    ]

    for label, path, require_items in endpoints:
        status, payload = _http_json("GET", _url(api_base, path))
        _require(200 <= status < 300, f"{label} returned HTTP {status}: {payload}")
        count = _count_items(payload)
        if require_items:
            _require(count > 0, f"{label} returned no data")
            _print_pass(f"{label}: HTTP {status}, count={count}")
        else:
            if count == 0:
                _print_warn(f"{label}: HTTP {status}, count=0")
            else:
                _print_pass(f"{label}: HTTP {status}, count={count}")


def check_frontend_pages(frontend_base: str) -> None:
    print("\nFrontend page checks")
    pages = [
        "/",
        "/index.html",
        "/products.html",
        "/promotions.html",
        "/brands.html",
        "/about.html",
        "/services.html",
        "/contact-us.html",
        "/booking.html",
    ]

    for page in pages:
        status = _http_status(_url(frontend_base, page))
        _require(200 <= status < 300, f"frontend page {page} returned HTTP {status}")
        _print_pass(f"frontend page {page}: HTTP {status}")


def _verify_dynamodb_item(logical_table: str, key_name: str, key_value: str) -> dict[str, Any]:
    table = get_dynamodb_table(get_table_name(logical_table), region_name=get_aws_region())
    response = table.get_item(Key={key_name: key_value})
    item = response.get("Item")
    _require(item is not None, f"DynamoDB item not found: {logical_table}.{key_name}={key_value}")
    return item


def check_public_writes(api_base: str) -> None:
    print("\nPublic form write checks")
    suffix = _now_suffix()
    # Philippines mobile number format. Reused intentionally so duplicate customer normalization can be observed later.
    contact_number = "+63 919 123 4567"

    booking_payload = {
        "customer_name": f"Batch 16 Booking Test {suffix}",
        "contact_number": contact_number,
        "email": f"batch16.booking.{suffix}@example.com",
        "address": "Batch 16 DynamoDB E2E Test Address",
        "preferred_date": "2026-12-30",
        "preferred_time": "Morning",
        "service_interest": "CCTV Installation",
        "notes": "Batch 16 public site DynamoDB regression test",
    }
    status, booking = _http_json("POST", _url(api_base, "/bookings"), booking_payload)
    _require(status in (200, 201), f"booking create returned HTTP {status}: {booking}")
    _require(isinstance(booking, dict), f"booking response was not a JSON object: {booking}")
    booking_id = booking.get("booking_id")
    customer_id = booking.get("customer_id")
    _require(bool(booking_id), f"booking response missing booking_id: {booking}")
    _require(bool(customer_id), f"booking response missing customer_id: {booking}")
    _verify_dynamodb_item("bookings", "booking_id", booking_id)
    _verify_dynamodb_item("customers", "customer_id", customer_id)
    _print_pass(f"booking created through API and verified in DynamoDB: {booking_id}")

    inquiry_payload = {
        "customer_name": f"Batch 16 Inquiry Test {suffix}",
        "contact_number": "0919 123 4567",
        "email": f"batch16.inquiry.{suffix}@example.com",
        "subject": "Batch 16 Public Inquiry Test",
        "message": "Batch 16 public inquiry DynamoDB regression test",
        "source_page": "Contact Us",
        "product_id": "CCTV-0000001",
    }
    status, inquiry = _http_json("POST", _url(api_base, "/inquiries"), inquiry_payload)
    _require(status in (200, 201), f"inquiry create returned HTTP {status}: {inquiry}")
    _require(isinstance(inquiry, dict), f"inquiry response was not a JSON object: {inquiry}")
    inquiry_id = inquiry.get("inquiry_id")
    inquiry_customer_id = inquiry.get("customer_id")
    _require(bool(inquiry_id), f"inquiry response missing inquiry_id: {inquiry}")
    _require(bool(inquiry_customer_id), f"inquiry response missing customer_id: {inquiry}")
    _verify_dynamodb_item("inquiries", "inquiry_id", inquiry_id)
    _verify_dynamodb_item("customers", "customer_id", inquiry_customer_id)
    _print_pass(f"inquiry created through API and verified in DynamoDB: {inquiry_id}")

    if inquiry_customer_id == customer_id:
        _print_pass("Philippines contact normalization reused the same customer for +63 and 09 formats")
    else:
        _print_warn(
            "Booking and inquiry used equivalent PH numbers but returned different customer IDs; "
            "check whether existing seeded/test customer data caused this."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 16 public-site DynamoDB regression test.")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/api")
    parser.add_argument("--frontend-base", default="http://127.0.0.1:5500")
    parser.add_argument("--execute", action="store_true", help="Run write checks through public APIs.")
    parser.add_argument(
        "--confirm-write-test",
        action="store_true",
        help="Required with --execute because this creates small DynamoDB test records.",
    )
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 16 Public Site DynamoDB Regression")
    print(f"API base URL: {args.api_base}")
    print(f"Frontend base URL: {args.frontend_base}")
    print(f"AWS region: {get_aws_region()}")
    print(f"Mode: {'EXECUTE WRITE TEST' if args.execute else 'READ-ONLY'}")

    if args.execute and not args.confirm_write_test:
        print("\nRefusing to run write checks without --confirm-write-test.")
        return 2

    try:
        check_api_reads(args.api_base)
        check_frontend_pages(args.frontend_base)
        if args.execute:
            check_public_writes(args.api_base)
        else:
            print("\nWrite checks skipped. Add --execute --confirm-write-test to create API test records.")
    except CheckFailure as exc:
        print(f"\nFAILED: {exc}")
        return 1
    except Exception as exc:  # Keep unexpected errors readable for local troubleshooting.
        print(f"\nERROR: {type(exc).__name__}: {exc}")
        return 1

    print("\nBatch 16 public-site DynamoDB regression PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
