"""Check DynamoDB table status for RSA CMS / Mini-CRM Phase 8 Final v5.

This script does not create or modify resources. It only describes existing
DynamoDB tables and confirms the approved launch GSIs are present.
"""

from __future__ import annotations

import argparse
from pathlib import Path
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

from app.database import get_aws_region, get_dynamodb_client, list_table_definitions  # noqa: E402


def select_definitions(selected: str | None) -> dict[str, dict[str, Any]]:
    definitions = list_table_definitions()
    if not selected or selected == "all":
        return definitions

    if selected not in definitions:
        valid = ", ".join(["all", *sorted(definitions.keys())])
        raise SystemExit(f"Unknown table '{selected}'. Valid options: {valid}")

    return {selected: definitions[selected]}


def describe_table(client: Any, table_name: str) -> dict[str, Any] | None:
    try:
        return client.describe_table(TableName=table_name)["Table"]
    except client.exceptions.ResourceNotFoundException:
        return None


def expected_gsi_names(definition: dict[str, Any]) -> set[str]:
    return {gsi["index_name"] for gsi in definition.get("gsis", [])}


def actual_gsi_names(table_description: dict[str, Any]) -> set[str]:
    return {gsi["IndexName"] for gsi in table_description.get("GlobalSecondaryIndexes", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check RSA CMS DynamoDB table status.")
    parser.add_argument(
        "--table",
        default="all",
        help="Logical table to check, such as products, customers, bookings, or all. Default: all.",
    )
    parser.add_argument("--all", action="store_true", help="Check all Phase 8 v5 launch tables.")
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument("--strict", action="store_true", help="Exit with error if any table/GSI is missing or not ACTIVE.")
    args = parser.parse_args()

    selected_table = "all" if args.all else args.table
    definitions = select_definitions(selected_table)
    region = args.region or get_aws_region()
    client = get_dynamodb_client(region_name=region)

    print("RSA CMS / Mini-CRM DynamoDB Table Check")
    print(f"Region: {region}")
    print("")

    has_error = False

    for logical_name, definition in definitions.items():
        table_name = definition["table_name"]
        description = describe_table(client, table_name)

        if description is None:
            print(f"MISSING  {logical_name:<16} {table_name}")
            has_error = True
            continue

        status = description.get("TableStatus", "UNKNOWN")
        billing_mode = description.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED")
        gsi_expected = expected_gsi_names(definition)
        gsi_actual = actual_gsi_names(description)
        missing_gsis = sorted(gsi_expected - gsi_actual)

        status_label = "OK" if status == "ACTIVE" and not missing_gsis else "CHECK"
        print(f"{status_label:<8} {logical_name:<16} {table_name} | status={status} | billing={billing_mode}")

        if gsi_expected:
            print(f"         expected GSIs: {', '.join(sorted(gsi_expected))}")
            print(f"         actual GSIs:   {', '.join(sorted(gsi_actual)) or '(none)'}")

        if status != "ACTIVE" or missing_gsis:
            has_error = True
            if missing_gsis:
                print(f"         missing GSIs:  {', '.join(missing_gsis)}")

    if args.strict and has_error:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
