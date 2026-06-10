"""Create DynamoDB tables for RSA CMS / Mini-CRM Phase 8 Final v5.

Safe by default:
- Running without --execute prints a dry-run preview only.
- Tables are created only when --execute is provided.
- Uses PROVISIONED capacity with low 1 RCU / 1 WCU defaults unless env vars override.

Example dry run:
    python scripts/create_dynamodb_tables.py --all

Example execute:
    python scripts/create_dynamodb_tables.py --all --execute
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
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
    get_default_read_capacity_units,
    get_default_write_capacity_units,
    get_dynamodb_client,
    list_table_definitions,
)


class TableAlreadyExists(Exception):
    pass


def _unique_attribute_definitions(definition: dict[str, Any]) -> list[dict[str, str]]:
    attributes: dict[str, str] = {}

    hash_name, hash_type = definition["hash_key"]
    attributes[hash_name] = hash_type

    for gsi in definition.get("gsis", []):
        gsi_hash_name, gsi_hash_type = gsi["hash_key"]
        attributes[gsi_hash_name] = gsi_hash_type

        if "range_key" in gsi and gsi["range_key"]:
            gsi_range_name, gsi_range_type = gsi["range_key"]
            attributes[gsi_range_name] = gsi_range_type

    return [
        {"AttributeName": name, "AttributeType": attr_type}
        for name, attr_type in attributes.items()
    ]


def _key_schema(hash_key: tuple[str, str], range_key: tuple[str, str] | None = None) -> list[dict[str, str]]:
    schema = [{"AttributeName": hash_key[0], "KeyType": "HASH"}]
    if range_key:
        schema.append({"AttributeName": range_key[0], "KeyType": "RANGE"})
    return schema


def _provisioned_throughput() -> dict[str, int]:
    return {
        "ReadCapacityUnits": get_default_read_capacity_units(),
        "WriteCapacityUnits": get_default_write_capacity_units(),
    }


def build_create_table_request(definition: dict[str, Any]) -> dict[str, Any]:
    request: dict[str, Any] = {
        "TableName": definition["table_name"],
        "BillingMode": "PROVISIONED",
        "AttributeDefinitions": _unique_attribute_definitions(definition),
        "KeySchema": _key_schema(definition["hash_key"]),
        "ProvisionedThroughput": _provisioned_throughput(),
    }

    gsis = []
    for gsi in definition.get("gsis", []):
        gsis.append(
            {
                "IndexName": gsi["index_name"],
                "KeySchema": _key_schema(gsi["hash_key"], gsi.get("range_key")),
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": _provisioned_throughput(),
            }
        )

    if gsis:
        request["GlobalSecondaryIndexes"] = gsis

    return request


def table_exists(client: Any, table_name: str) -> bool:
    try:
        client.describe_table(TableName=table_name)
        return True
    except client.exceptions.ResourceNotFoundException:
        return False


def create_one_table(client: Any, logical_name: str, definition: dict[str, Any], wait: bool) -> str:
    request = build_create_table_request(definition)
    table_name = request["TableName"]

    if table_exists(client, table_name):
        raise TableAlreadyExists(f"{table_name} already exists")

    client.create_table(**request)

    if wait:
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=table_name)
        # Give GSIs a brief extra moment to appear consistently in describe_table.
        time.sleep(1)

    return f"Created {logical_name}: {table_name}"


def select_definitions(selected: str | None) -> dict[str, dict[str, Any]]:
    definitions = list_table_definitions()
    if not selected or selected == "all":
        return definitions

    if selected not in definitions:
        valid = ", ".join(["all", *sorted(definitions.keys())])
        raise SystemExit(f"Unknown table '{selected}'. Valid options: {valid}")

    return {selected: definitions[selected]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create RSA CMS DynamoDB tables safely.")
    parser.add_argument(
        "--table",
        default="all",
        help="Logical table to create, such as products, customers, bookings, or all. Default: all.",
    )
    parser.add_argument("--all", action="store_true", help="Create/preview all Phase 8 v5 launch tables.")
    parser.add_argument("--execute", action="store_true", help="Actually create tables. Without this, dry-run only.")
    parser.add_argument("--wait", action="store_true", help="Wait until each created table exists before continuing.")
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="When executing, skip tables that already exist instead of stopping with an error.",
    )
    args = parser.parse_args()

    selected_table = "all" if args.all else args.table
    definitions = select_definitions(selected_table)
    region = args.region or get_aws_region()

    print("RSA CMS / Mini-CRM DynamoDB Table Setup")
    print(f"Region: {region}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print(f"Capacity: {get_default_read_capacity_units()} RCU / {get_default_write_capacity_units()} WCU per table/GSI")
    print("")

    requests = {
        logical_name: build_create_table_request(definition)
        for logical_name, definition in definitions.items()
    }

    if not args.execute:
        print("Dry run only. No AWS resources will be created.")
        print("Use --execute when you are ready to create the tables.")
        print("")
        print(json.dumps(requests, indent=2))
        return 0

    client = get_dynamodb_client(region_name=region)

    for logical_name, definition in definitions.items():
        table_name = definition["table_name"]
        try:
            message = create_one_table(client, logical_name, definition, wait=args.wait)
            print(message)
        except TableAlreadyExists as exc:
            if args.skip_existing:
                print(f"Skipped {logical_name}: {exc}")
                continue
            print(f"ERROR: {exc}")
            print("Use --skip-existing to ignore existing tables.")
            return 1

    print("")
    print("Done. Run scripts/check_dynamodb_tables.py --all to verify table status.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
