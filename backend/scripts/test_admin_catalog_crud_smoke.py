"""Batch 20 admin catalog CRUD smoke test.

Safe by default. Execute mode calls local FastAPI admin catalog endpoints and
creates/updates one brand, category, key feature, and product record.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE = "http://127.0.0.1:8000/api"


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{API_BASE}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _print(label: str, payload: dict) -> None:
    print(f"\n{label}")
    print(json.dumps(payload, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Batch 20 admin catalog CRUD smoke test.")
    parser.add_argument("--execute", action="store_true", help="Call local API and create/update records.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 20 Admin Catalog CRUD Smoke Test")
    print(f"API base URL: {API_BASE}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if not args.execute:
        print("\nNo API writes were made.")
        print("Start backend first, then run:")
        print("  python scripts\\test_admin_catalog_crud_smoke.py --execute --confirm-write-test")
        return 0

    if not args.confirm_write_test:
        raise SystemExit("Use --confirm-write-test with --execute to confirm local API write testing.")

    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    try:
        category = _request("POST", "/admin/categories", {
            "category_name": f"Batch 20 Test Category {suffix}",
            "category_key": f"batch20-test-{suffix}",
            "category_prefix": "TSTC",
            "display_seq": 90,
            "show_flag": "Y",
            "description": "Batch 20 temporary test category.",
        })
        _print("Created category:", category)

        brand = _request("POST", "/admin/brands", {
            "brand_name": f"Batch 20 Test Brand {suffix}",
            "brand_key": f"batch20-brand-{suffix}",
            "display_seq": 90,
            "show_flag": "Y",
            "description": "Batch 20 temporary test brand.",
        })
        _print("Created brand:", brand)

        feature = _request("POST", "/admin/key-features", {
            "key_feat_name": f"Batch 20 Feature {suffix}",
        })
        _print("Created key feature:", feature)

        product = _request("POST", "/admin/products", {
            "category_key": category["category_key"],
            "product_brand_key": brand["brand_key"],
            "subcategory": "Batch 20 Test Product",
            "feature_01": "Batch 20 Feature One",
            "feature_02": "Batch 20 Feature Two",
            "feature_03": "Batch 20 Feature Three",
            "price": 1234,
            "sale_price": 999,
            "stock_quantity": 3,
            "low_stock_threshold": 2,
            "show_flag": "Y",
            "show_pack_flag": "N",
            "description": "Batch 20 temporary test product.",
            "image_path": "assets/images/products/product-placeholder.png",
        })
        _print("Created product:", product)

        updated_product = _request("PUT", f"/admin/products/{product['product_id']}", {
            "sale_price": 899,
            "stock_quantity": 4,
            "description": "Batch 20 product update passed.",
        })
        _print("Updated product:", updated_product)

        if updated_product.get("sale_price") not in (899, 899.0):
            raise SystemExit("Product update did not persist expected sale_price.")

    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Unable to reach local API at {API_BASE}: {exc}") from exc

    print("\nBatch 20 admin catalog CRUD smoke test PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
