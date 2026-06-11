"""Phase 8 Batch 28 full public/admin API regression.

Safe by default:
- Dry run only prints the test plan.
- Execute mode requires --confirm-write-test and writes small non-destructive
  test records through the local API.

Run against whichever backend mode you are testing:
- mock mode: normal `uvicorn app.main:app --reload`
- DynamoDB mode: set `$env:RSA_REPOSITORY_MODE="dynamodb"` before uvicorn
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError


DEFAULT_API_BASE = "http://127.0.0.1:8000/api"


def _request(api_base: str, path: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urlrequest.Request(f"{api_base}{path}", data=data, headers=headers, method=method)
    with urlrequest.urlopen(req, timeout=25) as response:
        text = response.read().decode("utf-8")
        if not text:
            return {}
        return json.loads(text)


def _items(payload: dict | list) -> list:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    for key in ("items", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def _check_get(api_base: str, path: str, label: str, expect_items: bool = False) -> dict | list:
    payload = _request(api_base, path)
    if expect_items:
        items = _items(payload)
        print(f"OK {label}: {path} ({len(items)} records)")
    else:
        print(f"OK {label}: {path}")
    return payload


def _create_update(
    api_base: str,
    path: str,
    id_field: str,
    create_payload: dict,
    update_payload: dict,
    label: str,
) -> dict:
    created = _request(api_base, path, method="POST", payload=create_payload)
    item_id = created.get(id_field) if isinstance(created, dict) else None
    if not item_id:
        raise AssertionError(f"{label} create did not return {id_field}: {created}")

    updated = _request(api_base, f"{path}/{item_id}", method="PUT", payload=update_payload)
    if not isinstance(updated, dict) or updated.get(id_field) != item_id:
        raise AssertionError(f"{label} update returned unexpected result: {updated}")

    print(f"OK {label}: created/updated {item_id}")
    return updated


def _post(api_base: str, path: str, payload: dict, id_field: str, label: str) -> dict:
    created = _request(api_base, path, method="POST", payload=payload)
    item_id = created.get(id_field) if isinstance(created, dict) else None
    if not item_id:
        raise AssertionError(f"{label} create did not return {id_field}: {created}")
    print(f"OK {label}: created {item_id}")
    return created


def _print_dry_run(api_base: str) -> None:
    print("\nDry run only. No API writes were made.")
    print("\nStart backend first, then run execute mode:")
    print("  python scripts\\test_phase8_full_regression.py --execute --confirm-write-test")
    print("\nRecommended test sequence:")
    print("  1. Run once in mock mode.")
    print("  2. Run once in DynamoDB mode.")
    print("\nAPI base URL:")
    print(f"  {api_base}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 8 full public/admin API regression.")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--execute", action="store_true", help="Run API checks and create small test records.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    api_base = args.api_base.rstrip("/")

    print("RSA CMS / Mini-CRM Phase 8 Full Regression")
    print(f"API base URL: {api_base}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if not args.execute:
        _print_dry_run(api_base)
        return 0

    if not args.confirm_write_test:
        raise SystemExit("Refusing write regression without --confirm-write-test.")

    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    try:
        print("\n== Core/public read checks ==")
        _check_get(api_base, "/health", "health")
        _check_get(api_base, "/admin/auth/config", "admin auth config")
        _check_get(api_base, "/admin/auth/status", "admin auth status")

        for path, label in [
            ("/products", "public products"),
            ("/products?sale=true", "public sale products"),
            ("/products?category=packages", "public package products"),
            ("/brands", "public brands"),
            ("/categories", "public categories"),
            ("/key-features", "public key features"),
            ("/package-banners", "public package banners"),
            ("/about", "public about"),
            ("/project-gallery", "public project gallery"),
            ("/services", "public services"),
            ("/contact", "public contact"),
            ("/pages/about", "page about"),
            ("/pages/services", "page services"),
            ("/pages/contact", "page contact"),
        ]:
            _check_get(api_base, path, label, expect_items=True)

        print("\n== Admin read checks ==")
        for path, label in [
            ("/bookings", "bookings"),
            ("/inquiries", "inquiries"),
            ("/customers", "customers"),
            ("/admin/products", "admin products"),
            ("/admin/categories", "admin categories"),
            ("/admin/brands", "admin brands"),
            ("/admin/key-features", "admin key features"),
            ("/admin/about", "admin about"),
            ("/admin/project-gallery", "admin project gallery"),
            ("/admin/services", "admin services"),
            ("/admin/contact-us", "admin contact us"),
        ]:
            _check_get(api_base, path, label, expect_items=True)

        print("\n== Public write checks ==")
        booking = _post(api_base, "/bookings", {
            "customer_name": f"Batch 28 Booking Test {suffix}",
            "contact_number": "+63 919 128 2800",
            "email": f"batch28.booking.{suffix}@example.com",
            "address": "Batch 28 regression address",
            "preferred_date": "2026-12-30",
            "preferred_time": "Morning",
            "service_interest": "CCTV Installation",
            "notes": "Phase 8 full regression booking test.",
        }, "booking_id", "booking")

        inquiry = _post(api_base, "/inquiries", {
            "customer_name": f"Batch 28 Inquiry Test {suffix}",
            "contact_number": "0919 128 2801",
            "email": f"batch28.inquiry.{suffix}@example.com",
            "subject": "Batch 28 regression inquiry",
            "message": "Phase 8 full regression inquiry test.",
            "source_page": "Batch 28 Regression",
            "product_id": "CCTV-0000001",
        }, "inquiry_id", "inquiry")

        _request(api_base, f"/bookings/{booking['booking_id']}", method="PUT", payload={
            "status": "Scheduled",
            "assigned_person": "Batch 28 Admin",
            "comments": "Updated by Phase 8 full regression.",
        })
        print(f"OK booking update: {booking['booking_id']}")

        _request(api_base, f"/inquiries/{inquiry['inquiry_id']}", method="PUT", payload={
            "status": "Replied",
            "assigned_person": "Batch 28 Admin",
        })
        print(f"OK inquiry update: {inquiry['inquiry_id']}")

        print("\n== Admin catalog CRUD checks ==")
        category = _request(api_base, "/admin/categories", method="POST", payload={
            "category_name": f"Batch 28 Test Category {suffix}",
            "category_key": f"batch28-test-{suffix}",
            "category_prefix": "TSTC",
            "display_seq": 99,
            "show_flag": "Y",
            "description": "Temporary Phase 8 full regression category.",
        })
        print(f"OK category create: {category.get('category_id')}")

        brand = _request(api_base, "/admin/brands", method="POST", payload={
            "brand_name": f"Batch 28 Test Brand {suffix}",
            "brand_key": f"batch28-brand-{suffix}",
            "display_seq": 99,
            "show_flag": "Y",
            "description": "Temporary Phase 8 full regression brand.",
        })
        print(f"OK brand create: {brand.get('brand_id')}")

        feature = _request(api_base, "/admin/key-features", method="POST", payload={
            "key_feat_name": f"Batch 28 Feature {suffix}",
        })
        print(f"OK key feature create: {feature.get('key_feat_id')}")

        product = _request(api_base, "/admin/products", method="POST", payload={
            "category_key": category["category_key"],
            "product_brand_key": brand["brand_key"],
            "subcategory": "Batch 28 Test Product",
            "feature_01": "Batch 28 Feature One",
            "feature_02": "Batch 28 Feature Two",
            "feature_03": "Batch 28 Feature Three",
            "price": 2228,
            "sale_price": 2028,
            "stock_quantity": 5,
            "low_stock_threshold": 2,
            "show_flag": "Y",
            "show_pack_flag": "N",
            "description": "Temporary Phase 8 full regression product.",
            "image_path": "uploads/products/batch28-product-placeholder.png",
        })
        product_id = product.get("product_id")
        print(f"OK product create: {product_id}")

        updated_product = _request(api_base, f"/admin/products/{product_id}", method="PUT", payload={
            "sale_price": 1928,
            "stock_quantity": 6,
            "description": "Updated by Phase 8 full regression.",
        })
        if updated_product.get("sale_price") not in (1928, 1928.0):
            raise AssertionError("Product update did not persist sale_price.")
        print(f"OK product update: {product_id}")

        print("\n== Admin CMS CRUD checks ==")
        _create_update(
            api_base,
            "/admin/services",
            "service_id",
            {
                "show_flag": "N",
                "display_seq": 99,
                "service_title": f"Batch 28 Test Service {suffix}",
                "short_description": "Temporary Phase 8 full regression service.",
                "service_description": "Created by Phase 8 full regression.",
                "cta_label": "Test CTA",
                "cta_url": "contact-us.html",
                "updated_by": "batch28-regression",
            },
            {"short_description": "Updated by Phase 8 full regression.", "updated_by": "batch28-regression"},
            "service",
        )

        _create_update(
            api_base,
            "/admin/project-gallery",
            "project_id",
            {
                "show_flag": "N",
                "display_seq": 99,
                "project_title": f"Batch 28 Test Project {suffix}",
                "project_description": "Temporary Phase 8 full regression gallery item.",
                "image_path": "uploads/project-gallery/batch28-test.jpg",
                "alt_text": "Batch 28 test project",
                "updated_by": "batch28-regression",
            },
            {"project_description": "Updated by Phase 8 full regression.", "updated_by": "batch28-regression"},
            "project gallery item",
        )

        _create_update(
            api_base,
            "/admin/contact-us",
            "contact_us_id",
            {
                "show_flag": "N",
                "contact_type": "Contact Person",
                "display_seq": 99,
                "person_name": f"Batch 28 Contact Person {suffix}",
                "position_title": "Regression Tester",
                "contact_number": "+63 919 128 2802",
                "email_address": f"batch28.contact.{suffix}@example.com",
                "photo_path": "uploads/contact-persons/batch28-contact.jpg",
                "updated_by": "batch28-regression",
            },
            {"position_title": "Updated Regression Tester", "updated_by": "batch28-regression"},
            "contact person",
        )

    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Unable to reach local API at {api_base}: {exc}") from exc

    print("\nPhase 8 full public/admin API regression PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
