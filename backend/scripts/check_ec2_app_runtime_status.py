#!/usr/bin/env python3
"""RSA CMS Batch 36 EC2 app runtime status check.

Read-only checks:
- Finds the Batch 34 EC2 demo instance by Name tag.
- Shows state, public IPv4, IAM profile, and security groups.
- Optionally checks the public backend /api/health endpoint on port 8000.

No AWS resources are created, updated, started, stopped, or deleted.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

EXPECTED_REGION = "ap-southeast-1"
EXPECTED_NAME = "rsa-cms-demo-backend"
EXPECTED_ROLE_NAME = "rsa-cms-ec2-backend-role"
EXPECTED_SECURITY_GROUP = "rsa-cms-demo-backend-sg"


def run_aws(args: list[str]) -> tuple[int, str, str]:
    cmd = ["aws", *args, "--output", "json"]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def load_json(text: str) -> Any:
    try:
        return json.loads(text) if text else None
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse AWS CLI JSON output: {exc}") from exc


def get_identity() -> dict[str, Any]:
    code, out, err = run_aws(["sts", "get-caller-identity"])
    if code != 0:
        raise RuntimeError(err or "aws sts get-caller-identity failed")
    return load_json(out)


def find_instances() -> list[dict[str, Any]]:
    code, out, err = run_aws(
        [
            "ec2",
            "describe-instances",
            "--region",
            EXPECTED_REGION,
            "--filters",
            f"Name=tag:Name,Values={EXPECTED_NAME}",
            "Name=instance-state-name,Values=pending,running,stopping,stopped",
        ]
    )
    if code != 0:
        raise RuntimeError(err or "aws ec2 describe-instances failed")
    data = load_json(out)
    instances: list[dict[str, Any]] = []
    for reservation in data.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))
    return instances


def check_http(url: str, timeout: int = 8) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rsa-cms-batch36-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(800).decode("utf-8", errors="replace")
            return True, f"HTTP {response.status}: {body}"
    except urllib.error.HTTPError as exc:
        body = exc.read(800).decode("utf-8", errors="replace")
        return False, f"HTTP {exc.code}: {body}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="RSA CMS Batch 36 EC2 app runtime status check")
    parser.add_argument("--check-public-health", action="store_true", help="Also call http://<public-ip>:8000/api/health")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 36 EC2 App Runtime Status Check")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, started, stopped, or deleted.")
    print(f"Expected region: {EXPECTED_REGION}")
    print(f"Expected instance name: {EXPECTED_NAME}")
    print()

    print("== AWS CLI identity ==")
    identity = get_identity()
    print(f"Account: {identity.get('Account')}")
    print(f"ARN: {identity.get('Arn')}")
    print()

    print("== Search for EC2 demo instance ==")
    instances = find_instances()
    if not instances:
        print("No EC2 demo instance found. Start/create Batch 34 instance first.")
        return 1
    if len(instances) > 1:
        print(f"WARN: found {len(instances)} instances named {EXPECTED_NAME}. Use the running one intentionally.")

    instance = instances[0]
    tags = {tag.get("Key"): tag.get("Value") for tag in instance.get("Tags", [])}
    state = instance.get("State", {}).get("Name", "unknown")
    public_ip = instance.get("PublicIpAddress")
    private_ip = instance.get("PrivateIpAddress")
    profile_arn = instance.get("IamInstanceProfile", {}).get("Arn", "")
    security_groups = instance.get("SecurityGroups", [])

    print(f"Name: {tags.get('Name')}")
    print(f"Instance ID: {instance.get('InstanceId')}")
    print(f"State: {state}")
    print(f"Instance type: {instance.get('InstanceType')}")
    print(f"Public IPv4: {public_ip or '(none)'}")
    print(f"Private IPv4: {private_ip or '(none)'}")
    print(f"Key pair: {instance.get('KeyName') or '(none)'}")
    print(f"IAM instance profile: {profile_arn or '(none)'}")
    for sg in security_groups:
        print(f"Attached security group: {sg.get('GroupName')} ({sg.get('GroupId')})")
    print()

    if state != "running":
        print("WARN: instance is not running. Start it before deploying or checking public /api/health.")
        return 0

    if EXPECTED_ROLE_NAME not in profile_arn:
        print(f"WARN: expected IAM profile containing {EXPECTED_ROLE_NAME}.")
    if not any(sg.get("GroupName") == EXPECTED_SECURITY_GROUP for sg in security_groups):
        print(f"WARN: expected security group {EXPECTED_SECURITY_GROUP}.")

    if args.check_public_health:
        print("== Public backend health check ==")
        if not public_ip:
            print("ERROR: no public IP found.")
            return 1
        url = f"http://{public_ip}:8000/api/health"
        print(f"URL: {url}")
        ok, message = check_http(url)
        if ok:
            print(f"OK: {message}")
        else:
            print(f"WARN: public health check failed: {message}")
            print("This is expected before the backend service is installed/started, or if your current IP is not allowed on port 8000.")
    else:
        print("Tip: after deployment, run with --check-public-health to test http://<public-ip>:8000/api/health")

    print()
    print("Batch 36 EC2 app runtime status check completed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
