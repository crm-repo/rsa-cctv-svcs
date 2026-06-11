"""Batch 22 admin DynamoDB regression smoke test.

Safe by default. Execute mode calls the local FastAPI admin endpoints and then
verifies the created/updated records directly in DynamoDB.

Important:
- Start the backend in DynamoDB mode before running execute mode:
    $env:RSA_REPOSITORY_MODE="dynamodb"
    uvicorn app.main:app --reload
- This script intentionally creates small hidden/low-display test records.
- It does not delete records.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

try:
    import boto3  # type: ignore
except Exception as exc:  # pragma: no cover - local dependency guard
    boto3 = None  # type: ignore
    BOTO3_IMPORT_ERROR = exc
else:
    BOTO3_IMPORT_ERROR = None

API_BASE = os.getenv("RSA_API_BASE_URL", "http://127.0.0.1:8000/api")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION") or "ap-southeast-1"

TABLES = {
    "products": "rsa_products",
    "brands": "rsa_brands",
    "categories": "rsa_categories",
    "key_features": "rsa_key_features",
    "about": "rsa_about",
    "project_gallery": "rsa_project_gallery",
    "services": "rsa_services",
    "contact_us": "rsa_contact_us",
}


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return str(value)


def _request(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urlrequest.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    with urlrequest.urlopen(req, timeout=20) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _health() -> None:
    try:
        _request("/health")
    except (URLError, HTTPError) as exc:
        raise SystemExit(
            f"Unable to reach local API at {API_BASE}. Start backend first. Details: {exc}"
        ) from exc


def _table(table_name: str):
    if boto3 is None:
        raise SystemExit(f"boto3 import failed: {BOTO3_IMPORT_ERROR}")
    return boto3.resource("dynamodb", region_name=AWS_REGION).Table(table_name)


def _get_item(logical_table: str, pk_field: str, pk_value: str) -> dict[str, Any]:
    table_name = TABLES[logical_table]
    response = _table(table_name).get_item(Key={pk_field: pk_value})
    item = response.get("Item")
    if not item:
        raise AssertionError(
            f"Could not find {logical_table} item {pk_field}={pk_value} in DynamoDB table {table_name}. "
            "Make sure backend is running with RSA_REPOSITORY_MODE=dynamodb."
        )
    return item


def _assert_field(item: dict[str, Any], field: str, expected: Any) -> None:
    actual = item.get(field)
    if isinstance(actual, Decimal) and isinstance(expected, (int, float)):
        actual = float(actual) if actual != actual.to_integral_value() else int(actual)
    if actual != expected:
        raise AssertionError(f"Expected {field}={expected!r}, got {actual!r}. Item: {json.dumps(item, default=_json_default)}")


def _print_ok(message: str) -> None:
    print(f"OK {message}")


def _assert_public_reads() -> None:
    checks = [
        ("/products", "public products"),
        ("/brands", "public brands"),
        ("/categories", "public categories"),
        ("/key-features", "public key features"),
        ("/package-banners", "public package banners"),
        ("/about", "public about"),
        ("/project-gallery", "public project gallery"),
        ("/services", "public services"),
        ("/contact", "public contact"),
        ("/pages/about", "public grouped about page"),
        ("/pages/contact", "public grouped contact page"),
        ("/pages/services", "public grouped services page"),
    ]
    for path, label in checks:
        payload = _request(path)
        if payload is None:
            raise AssertionError(f"{label} returned no payload")
        _print_ok(f"{label} read")


def _run_admin_catalog_regression(suffix: str) -> None:
    category = _request(
        "/admin/categories",
        method="POST",
        payload={
            "category_name": f"Batch 22 Test Category {suffix}",
            "category_key": f"batch22-test-{suffix}",
            "category_prefix": "TADN",
            "display_seq": 990,
            "show_flag": "N",
            "description": "Batch 22 DynamoDB regression category.",
        },
    )
    category_id = category["category_id"]
    _get_item("categories", "category_id", category_id)
    _print_ok(f"category created in DynamoDB: {category_id}")

    brand = _request(
        "/admin/brands",
        method="POST",
        payload={
            "brand_name": f"Batch 22 Test Brand {suffix}",
            "brand_key": f"batch22-brand-{suffix}",
            "display_seq": 990,
            "show_flag": "N",
            "description": "Batch 22 DynamoDB regression brand.",
        },
    )
    brand_id = brand["brand_id"]
    _get_item("brands", "brand_id", brand_id)
    _print_ok(f"brand created in DynamoDB: {brand_id}")

    key_feature = _request(
        "/admin/key-features",
        method="POST",
        payload={"key_feat_name": f"Batch 22 Key Feature {suffix}"},
    )
    key_feat_id = key_feature["key_feat_id"]
    _get_item("key_features", "key_feat_id", key_feat_id)
    _print_ok(f"key feature created in DynamoDB: {key_feat_id}")

    product = _request(
        "/admin/products",
        method="POST",
        payload={
            "category_key": category["category_key"],
            "product_brand_key": brand["brand_key"],
            "subcategory": "Batch 22 Regression Product",
            "feature_01": "Batch 22 Feature One",
            "feature_02": "Batch 22 Feature Two",
            "feature_03": "Batch 22 Feature Three",
            "price": 2222,
            "sale_price": 1999,
            "stock_quantity": 8,
            "low_stock_threshold": 2,
            "show_flag": "N",
            "show_pack_flag": "N",
            "description": "Batch 22 DynamoDB regression product.",
            "image_path": "assets/images/products/product-placeholder.png",
        },
    )
    product_id = product["product_id"]
    _get_item("products", "product_id", product_id)
    _print_ok(f"product created in DynamoDB: {product_id}")

    updated_product = _request(
        f"/admin/products/{product_id}",
        method="PUT",
        payload={"sale_price": 1888, "description": "Batch 22 product update verified."},
    )
    if updated_product.get("product_id") != product_id:
        raise AssertionError("Product update returned unexpected ID")
    product_item = _get_item("products", "product_id", product_id)
    _assert_field(product_item, "description", "Batch 22 product update verified.")
    _assert_field(product_item, "sale_price", 1888)
    _print_ok(f"product updated in DynamoDB: {product_id}")


def _run_admin_cms_regression(suffix: str) -> None:
    about = _request(
        "/admin/about",
        method="POST",
        payload={
            "show_flag": "N",
            "hero_title": f"Batch 22 Test About {suffix}",
            "hero_subtitle": "Created by Batch 22 DynamoDB regression.",
            "company_story_title": "Batch 22 Story",
            "company_story_body": "Temporary hidden about record for DynamoDB regression.",
            "mission_title": "Batch 22 Mission",
            "mission_body": "Verify admin About CRUD against DynamoDB.",
            "updated_by": "batch22-regression",
        },
    )
    about_id = about["about_id"]
    _get_item("about", "about_id", about_id)
    _print_ok(f"about record created in DynamoDB: {about_id}")

    updated_about = _request(
        f"/admin/about/{about_id}",
        method="PUT",
        payload={"hero_subtitle": "Batch 22 about update verified.", "updated_by": "batch22-regression"},
    )
    if updated_about.get("about_id") != about_id:
        raise AssertionError("About update returned unexpected ID")
    about_item = _get_item("about", "about_id", about_id)
    _assert_field(about_item, "hero_subtitle", "Batch 22 about update verified.")
    _print_ok(f"about record updated in DynamoDB: {about_id}")

    service = _request(
        "/admin/services",
        method="POST",
        payload={
            "show_flag": "N",
            "display_seq": 990,
            "service_title": f"Batch 22 Test Service {suffix}",
            "short_description": "Temporary admin DynamoDB regression service.",
            "service_description": "Created by Batch 22 regression test.",
            "cta_label": "Test CTA",
            "cta_url": "contact-us.html",
            "updated_by": "batch22-regression",
        },
    )
    service_id = service["service_id"]
    _get_item("services", "service_id", service_id)
    _print_ok(f"service created in DynamoDB: {service_id}")

    updated_service = _request(
        f"/admin/services/{service_id}",
        method="PUT",
        payload={"short_description": "Batch 22 service update verified.", "updated_by": "batch22-regression"},
    )
    if updated_service.get("service_id") != service_id:
        raise AssertionError("Service update returned unexpected ID")
    service_item = _get_item("services", "service_id", service_id)
    _assert_field(service_item, "short_description", "Batch 22 service update verified.")
    _print_ok(f"service updated in DynamoDB: {service_id}")

    project = _request(
        "/admin/project-gallery",
        method="POST",
        payload={
            "show_flag": "N",
            "display_seq": 990,
            "project_title": f"Batch 22 Test Project {suffix}",
            "project_description": "Temporary hidden project gallery record.",
            "image_path": "/assets/images/projects/batch22-test.jpg",
            "alt_text": "Batch 22 test project",
            "updated_by": "batch22-regression",
        },
    )
    project_id = project["project_id"]
    _get_item("project_gallery", "project_id", project_id)
    _print_ok(f"project gallery item created in DynamoDB: {project_id}")

    updated_project = _request(
        f"/admin/project-gallery/{project_id}",
        method="PUT",
        payload={"project_description": "Batch 22 project update verified.", "updated_by": "batch22-regression"},
    )
    if updated_project.get("project_id") != project_id:
        raise AssertionError("Project update returned unexpected ID")
    project_item = _get_item("project_gallery", "project_id", project_id)
    _assert_field(project_item, "project_description", "Batch 22 project update verified.")
    _print_ok(f"project gallery item updated in DynamoDB: {project_id}")

    contact = _request(
        "/admin/contact-us",
        method="POST",
        payload={
            "show_flag": "N",
            "contact_type": "Social Media",
            "display_seq": 990,
            "platform_name": f"Batch 22 Test Social {suffix}",
            "platform_key": f"batch22-test-{suffix}",
            "profile_url": "https://example.com/batch22-test",
            "icon_code": "fa-solid fa-flask",
            "updated_by": "batch22-regression",
        },
    )
    contact_us_id = contact["contact_us_id"]
    _get_item("contact_us", "contact_us_id", contact_us_id)
    _print_ok(f"contact/social record created in DynamoDB: {contact_us_id}")

    updated_contact = _request(
        f"/admin/contact-us/{contact_us_id}",
        method="PUT",
        payload={"profile_url": "https://example.com/batch22-test-updated", "updated_by": "batch22-regression"},
    )
    if updated_contact.get("contact_us_id") != contact_us_id:
        raise AssertionError("Contact update returned unexpected ID")
    contact_item = _get_item("contact_us", "contact_us_id", contact_us_id)
    _assert_field(contact_item, "profile_url", "https://example.com/batch22-test-updated")
    _print_ok(f"contact/social record updated in DynamoDB: {contact_us_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Batch 22 admin DynamoDB regression test.")
    parser.add_argument("--execute", action="store_true", help="Call local API and write test records.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Required with --execute.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 22 Admin DynamoDB Regression Test")
    print(f"API base URL: {API_BASE}")
    print(f"AWS region: {AWS_REGION}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if not args.execute:
        print("\nNo API writes were made.")
        print("Start backend in DynamoDB mode first, then run:")
        print("  $env:RSA_REPOSITORY_MODE=\"dynamodb\"")
        print("  uvicorn app.main:app --reload")
        print("  python scripts\\test_admin_dynamodb_regression.py --execute --confirm-write-test")
        return 0

    if not args.confirm_write_test:
        raise SystemExit("Refusing to write test records without --confirm-write-test")

    _health()
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    try:
        _run_admin_catalog_regression(suffix)
        _run_admin_cms_regression(suffix)
        _assert_public_reads()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP error {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Unable to reach local API at {API_BASE}: {exc}") from exc

    print("\nBatch 22 admin DynamoDB regression test PASSED.")
    print("Stop Uvicorn after testing and reset with: Remove-Item Env:RSA_REPOSITORY_MODE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
