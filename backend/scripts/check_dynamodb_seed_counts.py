"""Check DynamoDB seed item counts for RSA CMS / Mini-CRM.

Batch 14 helper script.

This script is read-only. It scans each approved rsa_ table with Select=COUNT
so you can verify that Batch 13 seed data exists before switching the API to
DynamoDB mode for local regression testing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import get_aws_region, get_dynamodb_table, get_table_name  # noqa: E402

TABLES = [
    "products",
    "brands",
    "categories",
    "key_features",
    "customers",
    "bookings",
    "inquiries",
    "about",
    "project_gallery",
    "services",
    "contact_us",
    "id_counters",
]


def _count_table(logical_table: str, region: str) -> dict[str, Any]:
    table_name = get_table_name(logical_table)
    table = get_dynamodb_table(table_name, region_name=region)
    response = table.scan(Select="COUNT")
    return {
        "logical_table": logical_table,
        "table_name": table_name,
        "count": int(response.get("Count", 0)),
        "scanned_count": int(response.get("ScannedCount", 0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check RSA CMS DynamoDB seed item counts.")
    parser.add_argument("--region", default=get_aws_region(), help="AWS region. Defaults to configured project region.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    results = [_count_table(logical_table, args.region) for logical_table in TABLES]

    if args.json:
        print(json.dumps({"region": args.region, "tables": results}, indent=2))
        return 0

    print("RSA CMS / Mini-CRM DynamoDB Seed Count Check")
    print(f"Region: {args.region}")
    print("Mode: READ ONLY")
    print("")

    for result in results:
        status = "OK" if result["count"] > 0 else "EMPTY"
        print(f"{status:<7} {result['logical_table']:<16} {result['table_name']:<24} count={result['count']}")

    empty_tables = [result for result in results if result["count"] == 0]
    print("")
    if empty_tables:
        print("Some tables are empty. This can be normal for future admin-only data, but Batch 13 seed tables should usually be populated.")
        return 1

    print("All checked tables contain at least one item.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
