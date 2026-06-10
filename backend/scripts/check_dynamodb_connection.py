"""Check AWS/DynamoDB connectivity for RSA CMS / Mini-CRM.

Safe by default:
- Running without --execute prints the intended checks only.
- Running with --execute performs read-only AWS calls.
- This script does not create, update, or delete resources.
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

try:  # Optional local .env support.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import (  # noqa: E402
    get_aws_region,
    get_aws_sts_client,
    get_data_backend,
    get_dynamodb_client,
    get_repository_mode_summary,
    list_table_definitions,
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(inner_value) for key, inner_value in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _describe_phase8_tables(client: Any) -> dict[str, Any]:
    results: dict[str, Any] = {}

    for logical_name, definition in list_table_definitions().items():
        table_name = definition["table_name"]
        expected_gsis = sorted(gsi["index_name"] for gsi in definition.get("gsis", []))

        try:
            table = client.describe_table(TableName=table_name)["Table"]
            actual_gsis = sorted(gsi["IndexName"] for gsi in table.get("GlobalSecondaryIndexes", []))
            results[logical_name] = {
                "table_name": table_name,
                "status": table.get("TableStatus", "UNKNOWN"),
                "billing_mode": table.get("BillingModeSummary", {}).get("BillingMode", "PROVISIONED"),
                "expected_gsis": expected_gsis,
                "actual_gsis": actual_gsis,
                "missing_gsis": sorted(set(expected_gsis) - set(actual_gsis)),
            }
        except client.exceptions.ResourceNotFoundException:
            results[logical_name] = {
                "table_name": table_name,
                "status": "MISSING",
                "expected_gsis": expected_gsis,
                "actual_gsis": [],
                "missing_gsis": expected_gsis,
            }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Check RSA CMS AWS/DynamoDB connectivity safely.")
    parser.add_argument("--execute", action="store_true", help="Run read-only AWS connectivity checks. Default is dry-run only.")
    parser.add_argument("--region", default=None, help="AWS region override. Default uses AWS_REGION or ap-southeast-1.")
    parser.add_argument("--skip-sts", action="store_true", help="Skip STS caller identity check.")
    parser.add_argument("--check-tables", action="store_true", help="Describe approved Phase 8 DynamoDB tables.")
    parser.add_argument("--strict", action="store_true", help="Exit with error if table checks find missing/non-active tables.")
    args = parser.parse_args()

    region = args.region or get_aws_region()

    print("RSA CMS / Mini-CRM DynamoDB Connection Check")
    print(f"Region: {region}")
    print(f"Mode: {'EXECUTE READ-ONLY' if args.execute else 'DRY RUN'}")
    print(f"Repository mode env: {get_data_backend()}")
    print("")

    if not args.execute:
        print("Dry run only. No AWS calls were made.")
        print("Use --execute to perform read-only AWS/DynamoDB checks.")
        print("")
        print(json.dumps(_json_safe(get_repository_mode_summary()), indent=2))
        print("")
        print("Suggested later checks:")
        print("  python scripts\\check_dynamodb_connection.py --execute")
        print("  python scripts\\check_dynamodb_connection.py --execute --check-tables")
        return 0

    try:
        if not args.skip_sts:
            sts_client = get_aws_sts_client(region_name=region)
            identity = sts_client.get_caller_identity()
            print("AWS credentials: OK")
            print(f"Account: {identity.get('Account')}")
            print(f"Arn: {identity.get('Arn')}")
            print("")

        dynamodb_client = get_dynamodb_client(region_name=region)
        tables_response = dynamodb_client.list_tables(Limit=10)
        print("DynamoDB list_tables: OK")
        print(f"Visible table sample: {tables_response.get('TableNames', [])}")
        print("")

        has_error = False
        if args.check_tables:
            results = _describe_phase8_tables(dynamodb_client)
            print("Phase 8 table check:")
            for logical_name, result in results.items():
                status = result["status"]
                table_name = result["table_name"]
                missing_gsis = result.get("missing_gsis", [])
                label = "OK" if status == "ACTIVE" and not missing_gsis else "CHECK"
                print(f"{label:<6} {logical_name:<16} {table_name} | status={status}")
                if missing_gsis:
                    print(f"       missing GSIs: {', '.join(missing_gsis)}")
                if status != "ACTIVE" or missing_gsis:
                    has_error = True

            print("")

        if args.strict and has_error:
            return 1

    except Exception as exc:
        print("ERROR: AWS/DynamoDB connection check failed.")
        print(str(exc))
        return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
