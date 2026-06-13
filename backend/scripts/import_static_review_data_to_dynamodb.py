"""Import reviewed Batch 54A static HTML data into DynamoDB.

Batch 54B is intentionally destructive for selected records, but safe by default:
- Running without --execute is a dry run only.
- DynamoDB tables are never deleted.
- Execute mode requires --confirm-wipe-reviewed-static-data.
- rsa_id_counters is never wiped and is never reset downward.
- Counters are only advanced when reviewed static IDs are higher than the
  current counter value, preventing future generated ID collisions.

Default data source:
    backend/app/data/review_import

Recommended flow:
    python scripts/import_static_review_data_to_dynamodb.py --all
    python scripts/import_static_review_data_to_dynamodb.py --all --execute --confirm-wipe-reviewed-static-data
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:  # Optional local .env support.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import (  # noqa: E402
    get_aws_region,
    get_dynamodb_table,
    get_table_definition,
    get_table_name,
    list_table_definitions,
)

DEFAULT_REVIEW_IMPORT_DIR = BACKEND_ROOT / "app" / "data" / "review_import"

IMPORT_FILE_MAP: dict[str, str] = {
    "categories": "categories.json",
    "brands": "brands.json",
    "products": "products.json",
    "key_features": "key_features.json",
    "about": "about.json",
    "project_gallery": "project_gallery.json",
    "services": "services.json",
    "contact_us": "contact_us.json",
}

WIPE_ONLY_FILE_MAP: dict[str, str] = {
    "customers": "customers.json",
    "bookings": "bookings.json",
    "inquiries": "inquiries.json",
}

# Wipe children/detail data first, then parent/reference data. DynamoDB has no
# relational constraints, but this order makes logs easier to reason about.
DEFAULT_WIPE_ORDER = [
    "products",
    "key_features",
    "about",
    "project_gallery",
    "services",
    "contact_us",
    "customers",
    "bookings",
    "inquiries",
    "brands",
    "categories",
]

DEFAULT_IMPORT_ORDER = [
    "categories",
    "brands",
    "products",
    "key_features",
    "about",
    "project_gallery",
    "services",
    "contact_us",
]

ID_PATTERN = re.compile(r"^([A-Z]{4})-(\d{7})$")


class StaticImportError(Exception):
    """Raised when reviewed static import input is invalid."""


def _json_load_with_decimal(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise StaticImportError(f"Missing review import file: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise StaticImportError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, list):
        raise StaticImportError(f"Review import file must contain a JSON array: {path}")

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise StaticImportError(f"Row {index} in {path} must be an object/dictionary.")

    return data


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, dict):
        return {key: _json_safe(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _remove_null_values(value: Any) -> Any:
    """Recursively remove None values before writing to DynamoDB.

    This keeps optional attributes sparse and avoids NULL values on index keys.
    Empty strings are left as-is because reviewed static text fields may
    intentionally be blank only if the source data contains a blank string.
    """

    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, inner in value.items():
            if inner is None:
                continue
            cleaned_inner = _remove_null_values(inner)
            if cleaned_inner == {} or cleaned_inner == []:
                continue
            cleaned[key] = cleaned_inner
        return cleaned
    if isinstance(value, list):
        cleaned_list: list[Any] = []
        for item in value:
            if item is None:
                continue
            cleaned_item = _remove_null_values(item)
            if cleaned_item == {} or cleaned_item == []:
                continue
            cleaned_list.append(cleaned_item)
        return cleaned_list
    return value


def _primary_key_field(logical_table: str) -> str:
    return get_table_definition(logical_table)["hash_key"][0]


def _select_tables(selected_table: str | None, select_all: bool, include_lead_wipe: bool) -> tuple[list[str], list[str]]:
    definitions = list_table_definitions()
    import_tables = [table for table in DEFAULT_IMPORT_ORDER if table in definitions]
    wipe_only_tables = [table for table in WIPE_ONLY_FILE_MAP if table in definitions] if include_lead_wipe else []

    if select_all or not selected_table or selected_table == "all":
        return import_tables, wipe_only_tables

    all_valid = set(IMPORT_FILE_MAP) | set(WIPE_ONLY_FILE_MAP) | {"all"}
    if selected_table not in all_valid or selected_table not in definitions:
        valid = ", ".join(sorted(all_valid))
        raise SystemExit(f"Unknown table '{selected_table}'. Valid options: {valid}")

    if selected_table in IMPORT_FILE_MAP:
        return [selected_table], []
    return [], [selected_table]


def _load_review_files(review_dir: Path, import_tables: list[str], wipe_only_tables: list[str]) -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {}
    for logical_table in import_tables:
        data[logical_table] = _json_load_with_decimal(review_dir / IMPORT_FILE_MAP[logical_table])
    for logical_table in wipe_only_tables:
        # Keep the file load in place even for wipe-only tables so a missing or
        # malformed empty JSON file is caught before execute mode.
        data[logical_table] = _json_load_with_decimal(review_dir / WIPE_ONLY_FILE_MAP[logical_table])
    return data


def _validate_primary_keys(data: dict[str, list[dict[str, Any]]], import_tables: set[str]) -> list[str]:
    errors: list[str] = []
    for logical_table, items in data.items():
        pk_field = _primary_key_field(logical_table)
        seen: set[str] = set()
        for index, item in enumerate(items, start=1):
            pk_value = item.get(pk_field)
            # Empty wipe-only files are allowed. Non-empty rows still need PKs.
            if not pk_value:
                errors.append(f"{logical_table}: row {index} missing primary key field '{pk_field}'.")
                continue
            pk_str = str(pk_value)
            if pk_str in seen:
                errors.append(f"{logical_table}: duplicate primary key '{pk_str}'.")
            seen.add(pk_str)
    return errors


def _validate_static_relationships(data: dict[str, list[dict[str, Any]]]) -> tuple[list[str], list[str]]:
    """Validate approved category/subcategory/brand references.

    Returns (errors, warnings). Missing required references are errors; small
    informational observations are warnings only.
    """

    errors: list[str] = []
    warnings: list[str] = []

    categories = data.get("categories", [])
    brands = data.get("brands", [])
    products = data.get("products", [])
    contact_us = data.get("contact_us", [])

    category_by_key: dict[str, dict[str, Any]] = {}
    subcategory_keys_by_category: dict[str, set[str]] = {}
    for category in categories:
        category_key = str(category.get("category_key") or "").strip()
        if not category_key:
            errors.append(f"categories: category_id {category.get('category_id')} missing category_key.")
            continue
        category_by_key[category_key] = category
        subcategories = category.get("subcategories") or []
        if not isinstance(subcategories, list):
            errors.append(f"categories: {category_key} subcategories must be a list.")
            continue
        seen_subkeys: set[str] = set()
        for sub_index, subcategory in enumerate(subcategories, start=1):
            if not isinstance(subcategory, dict):
                errors.append(f"categories: {category_key} subcategory row {sub_index} must be an object.")
                continue
            subkey = str(subcategory.get("subcategory_key") or "").strip()
            subname = str(subcategory.get("subcategory_name") or "").strip()
            if not subkey or not subname:
                errors.append(f"categories: {category_key} subcategory row {sub_index} missing key/name.")
            if subkey in seen_subkeys:
                errors.append(f"categories: {category_key} duplicate subcategory_key '{subkey}'.")
            seen_subkeys.add(subkey)
        subcategory_keys_by_category[category_key] = seen_subkeys

    brand_keys: set[str] = set()
    for brand in brands:
        brand_key = str(brand.get("brand_key") or "").strip()
        if brand_key:
            brand_keys.add(brand_key)
        else:
            errors.append(f"brands: brand_id {brand.get('brand_id')} missing brand_key.")

    for product in products:
        product_id = product.get("product_id")
        category_key = str(product.get("category_key") or "").strip()
        subcategory_key = str(product.get("subcategory_key") or "").strip()
        product_brand_key = str(product.get("product_brand_key") or "").strip()

        if category_key not in category_by_key:
            errors.append(f"products: {product_id} references missing category_key '{category_key}'.")
        elif subcategory_key:
            allowed_subkeys = subcategory_keys_by_category.get(category_key, set())
            if subcategory_key not in allowed_subkeys:
                errors.append(
                    f"products: {product_id} subcategory_key '{subcategory_key}' is not in category '{category_key}'."
                )

        if product_brand_key and product_brand_key not in brand_keys:
            errors.append(f"products: {product_id} references missing brand_key '{product_brand_key}'.")

        if product.get("show_pack_flag") == "Y" and category_key != "packages":
            warnings.append(f"products: {product_id} has show_pack_flag=Y but category_key is '{category_key}'.")

    company_contacts = [row for row in contact_us if row.get("contact_type") == "Company Contact"]
    if len(company_contacts) != 1:
        errors.append(f"contact_us: expected exactly one Company Contact row, found {len(company_contacts)}.")
    elif company_contacts[0].get("contact_us_id") != "CONT-0000001":
        errors.append("contact_us: Company Contact must use fixed contact_us_id CONT-0000001.")

    return errors, warnings


def _discover_max_ids(data: dict[str, list[dict[str, Any]]], import_tables: set[str]) -> dict[str, int]:
    counters: dict[str, int] = {}
    for logical_table, items in data.items():
        if logical_table not in import_tables:
            continue
        for item in items:
            for key, value in item.items():
                if not key.endswith("_id") or not isinstance(value, str):
                    continue
                match = ID_PATTERN.match(value)
                if not match:
                    continue
                prefix = match.group(1)
                number = int(match.group(2))
                counters[prefix] = max(counters.get(prefix, 0), number)
    return counters


def _scan_all_primary_keys(logical_table: str, region: str) -> list[dict[str, Any]]:
    pk_field = _primary_key_field(logical_table)
    table = get_dynamodb_table(get_table_name(logical_table), region_name=region)
    projection_names = {"#pk": pk_field}
    kwargs: dict[str, Any] = {
        "ProjectionExpression": "#pk",
        "ExpressionAttributeNames": projection_names,
    }
    keys: list[dict[str, Any]] = []
    while True:
        response = table.scan(**kwargs)
        for item in response.get("Items", []):
            if pk_field in item:
                keys.append({pk_field: item[pk_field]})
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return keys


def _wipe_table(logical_table: str, region: str) -> int:
    table = get_dynamodb_table(get_table_name(logical_table), region_name=region)
    keys = _scan_all_primary_keys(logical_table, region=region)
    if not keys:
        return 0
    with table.batch_writer() as batch:
        for key in keys:
            batch.delete_item(Key=key)
    return len(keys)


def _put_items(logical_table: str, items: list[dict[str, Any]], region: str) -> int:
    table = get_dynamodb_table(get_table_name(logical_table), region_name=region)
    written = 0
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=_remove_null_values(item))
            written += 1
    return written


def _read_existing_counters(region: str) -> dict[str, int]:
    counters: dict[str, int] = {}
    table = get_dynamodb_table(get_table_name("id_counters"), region_name=region)
    kwargs: dict[str, Any] = {}
    while True:
        response = table.scan(**kwargs)
        for item in response.get("Items", []):
            prefix = item.get("id_prefix")
            last_number = item.get("last_number")
            if prefix is None or last_number is None:
                continue
            try:
                counters[str(prefix)] = int(last_number)
            except Exception:
                continue
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return counters


def _advance_counters_only(max_ids: dict[str, int], region: str) -> dict[str, Any]:
    existing = _read_existing_counters(region=region)
    table = get_dynamodb_table(get_table_name("id_counters"), region_name=region)
    now = datetime.now(timezone.utc).isoformat()
    advanced: dict[str, dict[str, int]] = {}
    unchanged: dict[str, int] = {}

    for prefix, imported_max in sorted(max_ids.items()):
        current = existing.get(prefix, 0)
        if imported_max > current:
            table.put_item(Item={
                "id_prefix": prefix,
                "last_number": int(imported_max),
                "updated_at": now,
                "updated_by": "batch54b-static-review-import",
            })
            advanced[prefix] = {"from": current, "to": imported_max}
        else:
            unchanged[prefix] = current

    return {
        "advanced": advanced,
        "unchanged": unchanged,
        "not_reset_downward": True,
    }


def _build_summary(
    data: dict[str, list[dict[str, Any]]],
    import_tables: list[str],
    wipe_only_tables: list[str],
    review_dir: Path,
    region: str,
    warnings: list[str],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "region": region,
        "review_import_dir": str(review_dir),
        "tables_to_wipe": [table for table in DEFAULT_WIPE_ORDER if table in set(import_tables) | set(wipe_only_tables)],
        "tables_to_import": import_tables,
        "wipe_only_tables": wipe_only_tables,
        "id_counters": "preserve existing and advance only when reviewed IDs are higher",
        "warnings": warnings,
        "counts": {},
    }
    for table in [*import_tables, *wipe_only_tables]:
        pk_field = _primary_key_field(table)
        items = data.get(table, [])
        summary["counts"][table] = {
            "table_name": get_table_name(table),
            "primary_key": pk_field,
            "review_file_count": len(items),
            "sample_keys": [item.get(pk_field) for item in items[:5]],
            "mode": "wipe_then_import" if table in import_tables else "wipe_only",
        }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Wipe/reimport reviewed Batch 54A static HTML data into DynamoDB.")
    parser.add_argument("--table", default="all", help="Logical table to process, or all. Default: all.")
    parser.add_argument("--all", action="store_true", help="Process all approved Batch 54B tables.")
    parser.add_argument(
        "--review-dir",
        default=str(DEFAULT_REVIEW_IMPORT_DIR),
        help="Folder containing reviewed JSON files. Default: backend/app/data/review_import.",
    )
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument("--execute", action="store_true", help="Actually wipe/import DynamoDB records. Without this, dry-run only.")
    parser.add_argument(
        "--confirm-wipe-reviewed-static-data",
        action="store_true",
        help="Required with --execute. Confirms you intend to wipe selected table records and import reviewed static data.",
    )
    parser.add_argument(
        "--skip-lead-wipe",
        action="store_true",
        help="Do not wipe customers/bookings/inquiries when processing all tables.",
    )
    parser.add_argument(
        "--no-advance-counters",
        action="store_true",
        help="Do not advance rsa_id_counters from imported IDs. Default is advance-only, never reset downward.",
    )
    args = parser.parse_args()

    include_lead_wipe = not args.skip_lead_wipe
    import_tables, wipe_only_tables = _select_tables(args.table, args.all, include_lead_wipe=include_lead_wipe)
    review_dir = Path(args.review_dir).resolve()
    region = args.region or get_aws_region()

    if args.execute and not args.confirm_wipe_reviewed_static_data:
        print("ERROR: execute mode requires --confirm-wipe-reviewed-static-data.")
        return 1

    try:
        data = _load_review_files(review_dir, import_tables, wipe_only_tables)
        errors = []
        errors.extend(_validate_primary_keys(data, set(import_tables)))
        rel_errors, warnings = _validate_static_relationships(data)
        errors.extend(rel_errors)
    except StaticImportError as exc:
        print(f"ERROR: {exc}")
        return 1

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  ERROR: {error}")
        return 1

    summary = _build_summary(data, import_tables, wipe_only_tables, review_dir, region, warnings)

    print("RSA CMS / Mini-CRM Batch 54B Static Review Data Import")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print(f"Region: {region}")
    print(f"Review folder: {review_dir}")
    print("Tables are preserved. Records in selected tables are wiped/reseeded only in execute mode.")
    print("rsa_id_counters is preserved and advanced only when needed; it is never reset downward.")
    print("")
    print(json.dumps(_json_safe(summary), indent=2))
    print("")

    if not args.execute:
        print("Dry run only. No DynamoDB records were deleted or written.")
        print("Run with --execute --confirm-wipe-reviewed-static-data when ready.")
        return 0

    wipe_set = set(import_tables) | set(wipe_only_tables)
    wipe_results: dict[str, int] = {}
    for logical_table in DEFAULT_WIPE_ORDER:
        if logical_table not in wipe_set:
            continue
        wipe_results[logical_table] = _wipe_table(logical_table, region=region)

    import_results: dict[str, int] = {}
    for logical_table in import_tables:
        import_results[logical_table] = _put_items(logical_table, data.get(logical_table, []), region=region)

    counter_result: dict[str, Any] = {"skipped": True}
    if not args.no_advance_counters:
        max_ids = _discover_max_ids(data, set(import_tables))
        counter_result = _advance_counters_only(max_ids, region=region)

    results = {
        "wipe_results": wipe_results,
        "import_results": import_results,
        "counter_result": counter_result,
    }
    print("Batch 54B execute results:")
    print(json.dumps(_json_safe(results), indent=2))
    print("")
    print("Batch 54B static review data import completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
