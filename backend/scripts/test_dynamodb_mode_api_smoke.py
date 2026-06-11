"""Run a local API smoke test while backend is in DynamoDB repository mode.

Batch 14 helper script.

This script intentionally writes a small number of test Booking/Inquiry records
through the public API, then verifies the returned IDs directly in DynamoDB.
That direct DynamoDB verification is what proves the running API server is
actually using RSA_REPOSITORY_MODE=dynamodb instead of mock mode.

Safe by default:
- Running without --execute only prints the planned test.
- To write test records, pass both --execute and --confirm-write-test.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import get_aws_region, get_dynamodb_table, get_table_name  # noqa: E402


def _url(base_url: str, path: str, query: dict[str, str] | None = None) -> str:
    normalized = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if query:
        return f"{normalized}?{urlencode(query)}"
    return normalized


def _request_json(method: str, base_url: str, path: str, payload: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(_url(base_url, path, query=query), data=data, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310 - local/dev test helper
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {method} {path}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(
            f"Could not reach API server at {base_url}. Start uvicorn first with RSA_REPOSITORY_MODE=dynamodb. Error: {exc}"
        ) from exc


def _get_dynamodb_item(logical_table: str, key_name: str, key_value: str, region: str) -> dict[str, Any] | None:
    table = get_dynamodb_table(get_table_name(logical_table), region_name=region)
    response = table.get_item(Key={key_name: key_value})
    return response.get("Item")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _find_item(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    for item in items:
        if item.get(key) == value:
            return item
    return None


def _print_plan(base_url: str, region: str) -> None:
    print("RSA CMS / Mini-CRM Batch 14 DynamoDB API Smoke Test")
    print(f"API base URL: {base_url}")
    print(f"AWS region: {region}")
    print("Mode: DRY RUN")
    print("")
    print("No API writes will be made.")
    print("To run the real local DynamoDB-mode smoke test:")
    print("  1. Start backend in a PowerShell window:")
    print('     $env:RSA_REPOSITORY_MODE="dynamodb"')
    print("     uvicorn app.main:app --reload")
    print("  2. Run this script in a second PowerShell:")
    print("     python scripts\\test_dynamodb_mode_api_smoke.py --execute --confirm-write-test")
    print("")
    print("The execute mode will create a small Booking/Inquiry test record set through the API and verify them in DynamoDB.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test RSA CMS API in DynamoDB repository mode.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api", help="Backend API base URL.")
    parser.add_argument("--region", default=get_aws_region(), help="AWS region.")
    parser.add_argument("--execute", action="store_true", help="Actually run API writes and DynamoDB verification.")
    parser.add_argument(
        "--confirm-write-test",
        action="store_true",
        help="Required with --execute because this creates small test records in DynamoDB.",
    )
    args = parser.parse_args()

    if not args.execute:
        _print_plan(args.base_url, args.region)
        return 0

    if not args.confirm_write_test:
        raise SystemExit("Refusing to write test records. Re-run with --execute --confirm-write-test.")

    print("RSA CMS / Mini-CRM Batch 14 DynamoDB API Smoke Test")
    print(f"API base URL: {args.base_url}")
    print(f"AWS region: {args.region}")
    print("Mode: EXECUTE WRITE TEST")
    print("")

    suffix = str(int(time.time()))[-6:]
    future_date = (date.today() + timedelta(days=14)).isoformat()

    health = _request_json("GET", args.base_url, "/health")
    _assert(health is not None, "Health response is empty.")
    print("OK health")

    # Public read endpoints should remain available while the backend is in DynamoDB mode.
    for path in ["/products", "/categories", "/contact", "/pages/contact"]:
        result = _request_json("GET", args.base_url, path)
        _assert(result is not None, f"{path} returned an empty response.")
        print(f"OK public read {path}")

    booking_payload = {
        "customer_name": f"Batch 14 DynamoDB Booking {suffix}",
        "contact_number": "+63 919 123 4567",
        "email": f"batch14.booking.{suffix}@example.com",
        "address": "Batch 14 DynamoDB Test Address, Metro Manila, Philippines",
        "preferred_date": future_date,
        "preferred_time": "Morning",
        "service_interest": "CCTV Installation",
        "notes": "Batch 14 local DynamoDB-mode API smoke test.",
    }
    booking = _request_json("POST", args.base_url, "/bookings", booking_payload)
    booking_id = booking["booking_id"]
    customer_id = booking["customer_id"]
    _assert(booking_id.startswith("BOOK-"), f"Unexpected booking_id: {booking_id}")
    _assert(customer_id and customer_id.startswith("CUST-"), f"Unexpected customer_id: {customer_id}")
    print(f"OK create booking {booking_id} customer={customer_id}")

    stored_booking = _get_dynamodb_item("bookings", "booking_id", booking_id, args.region)
    _assert(stored_booking is not None, "Created booking was not found directly in DynamoDB. Is uvicorn running in dynamodb mode?")
    print("OK booking exists directly in DynamoDB")

    stored_customer = _get_dynamodb_item("customers", "customer_id", customer_id, args.region)
    _assert(stored_customer is not None, "Created customer was not found directly in DynamoDB.")
    _assert(stored_customer.get("contact_number_normalized") == "639191234567", "Philippines contact normalization did not match expected value.")
    print("OK customer exists directly in DynamoDB with PH normalized contact")

    duplicate_booking_payload = {
        "customer_name": f"Batch 14 DynamoDB Booking Duplicate {suffix}",
        "contact_number": "0919 123 4567",
        "email": f"batch14.booking.duplicate.{suffix}@example.com",
        "address": "Batch 14 Duplicate Contact Test Address",
        "preferred_date": future_date,
        "preferred_time": "Afternoon",
        "service_interest": "CCTV Maintenance",
        "notes": "Batch 14 contact reuse test.",
    }
    duplicate_booking = _request_json("POST", args.base_url, "/bookings", duplicate_booking_payload)
    duplicate_booking_id = duplicate_booking["booking_id"]
    _assert(
        duplicate_booking["customer_id"] == customer_id,
        f"Expected duplicate booking to reuse {customer_id}, got {duplicate_booking['customer_id']}",
    )
    print(f"OK duplicate PH contact reused customer {customer_id}; booking={duplicate_booking_id}")

    booking_list = _request_json("GET", args.base_url, "/bookings", query={"status": "New"})
    _assert(_find_item(booking_list.get("items", []), "booking_id", booking_id) is not None, "New booking not found in status filter.")
    print("OK booking status filter")

    updated_booking = _request_json(
        "PUT",
        args.base_url,
        f"/bookings/{booking_id}",
        {"status": "Scheduled", "assigned_person": "Batch 14 Tester", "comments": "Updated through DynamoDB mode smoke test."},
    )
    _assert(updated_booking["status"] == "Scheduled", "Booking status update failed.")
    stored_updated_booking = _get_dynamodb_item("bookings", "booking_id", booking_id, args.region)
    _assert(stored_updated_booking and stored_updated_booking.get("status") == "Scheduled", "Updated booking status not found in DynamoDB.")
    print("OK booking update persisted in DynamoDB")

    inquiry_payload = {
        "customer_name": f"Batch 14 DynamoDB Inquiry {suffix}",
        "contact_number": "+63 917 654 3210",
        "email": f"batch14.inquiry.{suffix}@example.com",
        "subject": "Batch 14 DynamoDB Product Inquiry",
        "message": "Testing inquiry API while repository mode is DynamoDB.",
        "source_page": "Products",
        "product_id": "CCTV-0000001",
    }
    inquiry = _request_json("POST", args.base_url, "/inquiries", inquiry_payload)
    inquiry_id = inquiry["inquiry_id"]
    _assert(inquiry_id.startswith("INQR-"), f"Unexpected inquiry_id: {inquiry_id}")
    stored_inquiry = _get_dynamodb_item("inquiries", "inquiry_id", inquiry_id, args.region)
    _assert(stored_inquiry is not None, "Created inquiry was not found directly in DynamoDB.")
    print(f"OK create inquiry {inquiry_id} and verify DynamoDB")

    updated_inquiry = _request_json(
        "PUT",
        args.base_url,
        f"/inquiries/{inquiry_id}",
        {"status": "Replied", "assigned_person": "Batch 14 Tester"},
    )
    _assert(updated_inquiry["status"] == "Replied", "Inquiry status update failed.")
    stored_updated_inquiry = _get_dynamodb_item("inquiries", "inquiry_id", inquiry_id, args.region)
    _assert(stored_updated_inquiry and stored_updated_inquiry.get("status") == "Replied", "Updated inquiry status not found in DynamoDB.")
    print("OK inquiry update persisted in DynamoDB")

    customer_detail = _request_json("GET", args.base_url, f"/customers/{customer_id}")
    _assert(customer_detail["customer_id"] == customer_id, "Customer detail lookup failed.")
    print("OK customer detail from API")

    print("")
    print("Batch 14 DynamoDB-mode API smoke test PASSED.")
    print("Created test IDs:")
    print(json.dumps({"booking_id": booking_id, "duplicate_booking_id": duplicate_booking_id, "inquiry_id": inquiry_id, "customer_id": customer_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
