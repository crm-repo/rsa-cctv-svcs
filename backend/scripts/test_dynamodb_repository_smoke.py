"""Optional DynamoDB repository smoke test for RSA CMS / Mini-CRM.

Safe by default:
- Running without --execute is a dry run only.
- A write/read/delete test runs only with both --execute and --confirm-write-test.
- The default target is rsa_id_counters because it has the simplest key schema.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:  # Optional local .env support.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import get_aws_region, get_table_definition, get_table_name  # noqa: E402
from app.repositories.dynamodb_repository import DynamoDBRepository  # noqa: E402


DEFAULT_LOGICAL_TABLE = "id_counters"


def _primary_key_field(logical_table: str) -> str:
    return get_table_definition(logical_table)["hash_key"][0]


def _build_smoke_item(logical_table: str) -> dict[str, Any]:
    pk_field = _primary_key_field(logical_table)
    now = datetime.now(timezone.utc).isoformat()

    if logical_table == "id_counters":
        return {
            pk_field: f"TEST-{uuid4().hex[:8].upper()}",
            "last_number": 0,
            "updated_at": now,
            "updated_by": "batch7-smoke-test",
        }

    return {
        pk_field: f"TEST-{uuid4().hex[:12].upper()}",
        "created_at": now,
        "updated_at": now,
        "created_by": "batch7-smoke-test",
        "updated_by": "batch7-smoke-test",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an optional DynamoDB repository write/read/delete smoke test.")
    parser.add_argument("--table", default=DEFAULT_LOGICAL_TABLE, help="Logical table to test. Default: id_counters.")
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument("--execute", action="store_true", help="Allow the smoke test to run. Default is dry-run only.")
    parser.add_argument(
        "--confirm-write-test",
        action="store_true",
        help="Required together with --execute because this test writes and deletes one temporary item.",
    )
    args = parser.parse_args()

    region = args.region or get_aws_region()
    logical_table = args.table
    table_name = get_table_name(logical_table)
    pk_field = _primary_key_field(logical_table)
    item = _build_smoke_item(logical_table)
    item_id = item[pk_field]

    print("RSA CMS / Mini-CRM DynamoDB Repository Smoke Test")
    print(f"Region: {region}")
    print(f"Logical table: {logical_table}")
    print(f"DynamoDB table: {table_name}")
    print(f"Primary key field: {pk_field}")
    print(f"Temporary key: {item_id}")
    print(f"Mode: {'EXECUTE WRITE/READ/DELETE' if args.execute and args.confirm_write_test else 'DRY RUN'}")
    print("")

    if not args.execute or not args.confirm_write_test:
        print("Dry run only. No DynamoDB records were written.")
        print("To run the write/read/delete smoke test later, use:")
        print("  python scripts\\test_dynamodb_repository_smoke.py --execute --confirm-write-test")
        return 0

    try:
        repository = DynamoDBRepository(table_name=table_name, id_field=pk_field, region_name=region)
        repository.put_item(item)
        loaded_item = repository.get_by_id(item_id)

        if loaded_item is None:
            print("ERROR: Temporary item was not found after put_item.")
            return 1

        repository.delete_by_id(item_id)
        deleted_item = repository.get_by_id(item_id)

        if deleted_item is not None:
            print("ERROR: Temporary item still exists after delete_by_id.")
            return 1

    except Exception as exc:
        print("ERROR: DynamoDB repository smoke test failed.")
        print(str(exc))
        return 1

    print("Repository smoke test passed: put_item -> get_by_id -> delete_by_id.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
