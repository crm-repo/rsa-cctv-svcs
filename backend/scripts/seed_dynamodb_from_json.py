"""Seed RSA CMS / Mini-CRM DynamoDB tables from JSON files.

Batch 6 is development/testing focused.

Safe by default:
- Running without --execute is a dry run only.
- DynamoDB is written only when --execute is provided.
- Existing records are skipped by default unless --overwrite is provided.

Example dry run:
    python scripts/seed_dynamodb_from_json.py --all

Example execute later, after tables exist and AWS credentials are configured:
    python scripts/seed_dynamodb_from_json.py --all --execute
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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

DEFAULT_SEED_DIR = BACKEND_ROOT / "app" / "data" / "seed"

# Use the logical table names from app.database.py so this stays aligned with
# Phase 8 Final v5 table configuration.
SEED_FILE_MAP: dict[str, str] = {
    "products": "products.json",
    "brands": "brands.json",
    "categories": "categories.json",
    "key_features": "key_features.json",
    "customers": "customers.json",
    "bookings": "bookings.json",
    "inquiries": "inquiries.json",
    "about": "about.json",
    "project_gallery": "project_gallery.json",
    "services": "services.json",
    "contact_us": "contact_us.json",
    "id_counters": "id_counters.json",
}

ID_PATTERN = re.compile(r"^([A-Z]{4})-(\d{7})$")


class SeedFileError(Exception):
    """Raised when seed input files are missing or invalid."""


def _json_load_with_decimal(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SeedFileError(f"Missing seed file: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    except json.JSONDecodeError as exc:
        raise SeedFileError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, list):
        raise SeedFileError(f"Seed file must contain a JSON array: {path}")

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise SeedFileError(f"Seed row {index} in {path} must be an object/dictionary.")

    return data


def _json_safe(value: Any) -> Any:
    """Convert values to JSON-printable objects for dry-run output."""

    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    if isinstance(value, dict):
        return {key: _json_safe(inner_value) for key, inner_value in value.items()}

    if isinstance(value, list):
        return [_json_safe(item) for item in value]

    return value


def _primary_key_field(logical_table: str) -> str:
    definition = get_table_definition(logical_table)
    return definition["hash_key"][0]


def _validate_required_primary_keys(logical_table: str, items: list[dict[str, Any]]) -> None:
    pk_field = _primary_key_field(logical_table)

    for index, item in enumerate(items, start=1):
        if pk_field not in item or item[pk_field] in (None, ""):
            raise SeedFileError(
                f"Seed row {index} for table '{logical_table}' is missing primary key field '{pk_field}'."
            )


def _select_tables(selected_table: str | None, select_all: bool) -> list[str]:
    definitions = list_table_definitions()

    if select_all or not selected_table or selected_table == "all":
        return [logical_name for logical_name in SEED_FILE_MAP.keys() if logical_name in definitions]

    if selected_table not in definitions or selected_table not in SEED_FILE_MAP:
        valid = ", ".join(["all", *sorted(SEED_FILE_MAP.keys())])
        raise SystemExit(f"Unknown table '{selected_table}'. Valid options: {valid}")

    return [selected_table]


def _load_seed_files(seed_dir: Path, selected_tables: list[str]) -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {}

    for logical_table in selected_tables:
        path = seed_dir / SEED_FILE_MAP[logical_table]
        items = _json_load_with_decimal(path)
        _validate_required_primary_keys(logical_table, items)
        data[logical_table] = items

    return data


def _discover_id_counters(seed_data: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    """Compute max ID suffix per prefix from loaded seed records.

    Example:
        CCTV-0000002 -> {"CCTV": 2}

    This lets the seed script keep rsa_id_counters aligned with the imported
    development data, reducing the chance of duplicate IDs later.
    """

    counters: dict[str, int] = {}

    for logical_table, items in seed_data.items():
        if logical_table == "id_counters":
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


def _build_counter_items(counters: dict[str, int]) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id_prefix": prefix,
            "last_number": number,
            "updated_at": now,
            "updated_by": "seed-script",
        }
        for prefix, number in sorted(counters.items())
    ]


def _merge_synced_counters(seed_data: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    merged = deepcopy(seed_data)
    counters = _discover_id_counters(seed_data)

    if not counters:
        return merged

    existing_counter_items = {
        item.get("id_prefix"): item
        for item in merged.get("id_counters", [])
        if item.get("id_prefix")
    }

    for counter_item in _build_counter_items(counters):
        existing_counter_items[counter_item["id_prefix"]] = counter_item

    merged["id_counters"] = list(existing_counter_items.values())
    return merged


def _print_dry_run(seed_data: dict[str, list[dict[str, Any]]], seed_dir: Path, region: str, sync_counters: bool) -> None:
    print("RSA CMS / Mini-CRM JSON Seed Loader")
    print(f"Region: {region}")
    print("Mode: DRY RUN")
    print(f"Seed folder: {seed_dir}")
    print(f"Sync id counters: {'YES' if sync_counters else 'NO'}")
    print("")
    print("Dry run only. No DynamoDB records will be written.")
    print("Use --execute when DynamoDB tables exist and you are ready to seed data.")
    print("")

    summary: dict[str, Any] = {}
    for logical_table, items in seed_data.items():
        summary[logical_table] = {
            "table_name": get_table_name(logical_table),
            "seed_file": SEED_FILE_MAP[logical_table],
            "primary_key": _primary_key_field(logical_table),
            "item_count": len(items),
            "sample_keys": [item.get(_primary_key_field(logical_table)) for item in items[:5]],
        }

    print(json.dumps(_json_safe(summary), indent=2))


def _put_seed_items(
    seed_data: dict[str, list[dict[str, Any]]],
    region: str,
    overwrite: bool,
) -> dict[str, dict[str, int]]:
    results: dict[str, dict[str, int]] = {}

    for logical_table, items in seed_data.items():
        table_name = get_table_name(logical_table)
        pk_field = _primary_key_field(logical_table)
        table = get_dynamodb_table(table_name, region_name=region)

        written = 0
        skipped = 0

        for item in items:
            key = {pk_field: item[pk_field]}

            if not overwrite:
                existing = table.get_item(Key=key).get("Item")
                if existing is not None:
                    skipped += 1
                    continue

            table.put_item(Item=item)
            written += 1

        results[logical_table] = {
            "written": written,
            "skipped_existing": skipped,
            "total_input": len(items),
        }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed RSA CMS DynamoDB tables from JSON files safely.")
    parser.add_argument(
        "--table",
        default="all",
        help="Logical table to seed, such as products, contact_us, id_counters, or all. Default: all.",
    )
    parser.add_argument("--all", action="store_true", help="Seed/preview all available Batch 6 JSON files.")
    parser.add_argument(
        "--seed-dir",
        default=str(DEFAULT_SEED_DIR),
        help="Folder containing seed JSON files. Default: backend/app/data/seed.",
    )
    parser.add_argument("--execute", action="store_true", help="Actually write records to DynamoDB. Without this, dry-run only.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing records. Default execution behavior skips existing records.")
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument(
        "--no-sync-counters",
        action="store_true",
        help="Do not auto-sync id_counters from the imported ID values.",
    )
    args = parser.parse_args()

    selected_tables = _select_tables(args.table, args.all)
    seed_dir = Path(args.seed_dir).resolve()
    region = args.region or get_aws_region()
    sync_counters = not args.no_sync_counters

    try:
        seed_data = _load_seed_files(seed_dir, selected_tables)
    except SeedFileError as exc:
        print(f"ERROR: {exc}")
        return 1

    # When seeding all tables, keep id_counters aligned with the loaded seed IDs.
    # For a single-table seed, do not unexpectedly add id_counters unless the user
    # selected id_counters directly or selected all.
    if sync_counters and (args.all or args.table in (None, "all")):
        seed_data = _merge_synced_counters(seed_data)

    if not args.execute:
        _print_dry_run(seed_data, seed_dir, region, sync_counters)
        return 0

    print("RSA CMS / Mini-CRM JSON Seed Loader")
    print(f"Region: {region}")
    print("Mode: EXECUTE")
    print(f"Seed folder: {seed_dir}")
    print(f"Existing records: {'OVERWRITE' if args.overwrite else 'SKIP'}")
    print(f"Sync id counters: {'YES' if sync_counters else 'NO'}")
    print("")

    results = _put_seed_items(seed_data, region=region, overwrite=args.overwrite)
    print(json.dumps(_json_safe(results), indent=2))
    print("")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
