"""RSA CMS / Mini-CRM Batch 30 AWS cost-safety read-only check.

This script does not create, update, or delete AWS resources.

It checks:
- AWS CLI identity
- configured/default region
- DynamoDB tables in ap-southeast-1
- whether AWS Budgets can be listed with the current IAM permissions
- whether any budget names look like they are for RSA CMS / Free-Tier protection

It is intentionally read-only and safe to run before deployment planning.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


DEFAULT_REGION = "ap-southeast-1"
APPROVED_TABLES = [
    "rsa_products",
    "rsa_brands",
    "rsa_categories",
    "rsa_key_features",
    "rsa_customers",
    "rsa_bookings",
    "rsa_inquiries",
    "rsa_about",
    "rsa_project_gallery",
    "rsa_services",
    "rsa_contact_us",
    "rsa_id_counters",
]


def run_aws(args: list[str], allow_fail: bool = False) -> tuple[int, str, str]:
    cmd = ["aws", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def load_json(text: str) -> dict:
    if not text:
        return {}
    return json.loads(text)


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 30 AWS cost-safety read-only check.")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--account-id", default="", help="Optional account ID override for Budgets API.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 30 AWS Cost-Safety Read-Only Check")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, or deleted.")

    if not shutil.which("aws"):
        raise SystemExit("AWS CLI was not found in PATH. Install/configure AWS CLI first.")

    print_section("AWS identity")
    rc, out, err = run_aws(["sts", "get-caller-identity", "--output", "json"])
    identity = load_json(out)
    account_id = args.account_id or identity.get("Account", "")
    print(f"Account: {account_id or 'UNKNOWN'}")
    print(f"ARN: {identity.get('Arn', 'UNKNOWN')}")

    print_section("AWS CLI region")
    rc, region_out, region_err = run_aws(["configure", "get", "region"], allow_fail=True)
    configured_region = region_out.strip() or "(not configured)"
    print(f"Configured default region: {configured_region}")
    print(f"Project approved app region: {args.region}")
    if configured_region != args.region:
        print("NOTE: Default CLI region differs from the project app region. Use --region explicitly in deployment scripts.")

    print_section("DynamoDB approved table check")
    rc, tables_out, tables_err = run_aws(["dynamodb", "list-tables", "--region", args.region, "--output", "json"], allow_fail=True)
    if rc != 0:
        print("WARN: Unable to list DynamoDB tables with the current IAM user.")
        print(tables_err)
    else:
        table_names = set(load_json(tables_out).get("TableNames", []))
        missing = [name for name in APPROVED_TABLES if name not in table_names]
        extra_rsa = sorted(name for name in table_names if name.startswith("rsa_") and name not in APPROVED_TABLES)
        print(f"Approved tables present: {len(APPROVED_TABLES) - len(missing)} of {len(APPROVED_TABLES)}")
        if missing:
            print("Missing approved tables:")
            for name in missing:
                print(f"  - {name}")
        else:
            print("OK: all approved rsa_ tables are present.")
        if extra_rsa:
            print("NOTE: extra rsa_ tables found:")
            for name in extra_rsa:
                print(f"  - {name}")

    print_section("AWS Budgets visibility check")
    if not account_id:
        print("WARN: Could not determine account ID; skipping budgets check.")
    else:
        rc, budgets_out, budgets_err = run_aws(
            ["budgets", "describe-budgets", "--account-id", account_id, "--output", "json"],
            allow_fail=True,
        )
        if rc != 0:
            print("WARN: Unable to list AWS Budgets with the current IAM user.")
            print("This is common if the CLI user only has DynamoDB permissions.")
            print("Use the AWS Billing and Cost Management console with the root/management account or a billing-enabled IAM user.")
            print(budgets_err)
        else:
            budgets = load_json(budgets_out).get("Budgets", [])
            print(f"Budgets visible to this user: {len(budgets)}")
            matching = []
            for budget in budgets:
                name = budget.get("BudgetName", "")
                if any(term in name.lower() for term in ["rsa", "free", "tier", "cost", "budget"]):
                    matching.append(name)
            if matching:
                print("Possible cost-safety budgets:")
                for name in matching:
                    print(f"  - {name}")
            else:
                print("No obvious RSA/Free-Tier budget name found from this IAM user's visible budgets.")

    print_section("Manual confirmation still required")
    print("Before public/external AWS testing, manually confirm:")
    print("  [ ] AWS Budget/cost alert exists and sends email to the owner.")
    print("  [ ] Free Tier usage alert is enabled/available for the account.")
    print("  [ ] Optional CloudWatch billing alarm is configured only if approved.")
    print("  [ ] No ALB, NAT Gateway, RDS, paid SMS/MFA, or unnecessary always-on resources are planned.")
    print("  [ ] Mock mode remains default locally.")
    print("\nBatch 30 read-only cost-safety check completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
