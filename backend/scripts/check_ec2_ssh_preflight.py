#!/usr/bin/env python3
"""RSA CMS Batch 35 local SSH preflight.

Read-only checks:
- Finds the Batch 34 EC2 demo instance by Name tag.
- Shows public IPv4, key pair, IAM profile, and security groups.
- Prints SSH/SCP commands for Batch 35.

No AWS resources are created, updated, started, stopped, or deleted.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_REGION = "ap-southeast-1"
EXPECTED_NAME = "rsa-cms-demo-backend"
EXPECTED_KEY_NAME = "rsa-cms-demo-key"
EXPECTED_ROLE_NAME = "rsa-cms-ec2-backend-role"


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


def main() -> int:
    parser = argparse.ArgumentParser(description="RSA CMS Batch 35 EC2 SSH preflight")
    parser.add_argument("--key-path", help="Path to rsa-cms-demo-key.pem")
    parser.add_argument("--ssh-user", default="ec2-user", help="SSH username, usually ec2-user for Amazon Linux")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 35 EC2 SSH Preflight")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, started, stopped, or deleted.")
    print(f"Expected region: {EXPECTED_REGION}")
    print(f"Expected instance name: {EXPECTED_NAME}")
    print()

    try:
        identity = get_identity()
        print("== AWS CLI identity ==")
        print(f"Account: {identity.get('Account')}")
        print(f"ARN: {identity.get('Arn')}")
        print()

        instances = find_instances()
        print("== EC2 demo instance ==")
        if not instances:
            print("No EC2 demo instance found yet. Batch 34 must be completed first.")
            return 1
        if len(instances) > 1:
            print(f"WARN: found {len(instances)} matching instances. Use the running one intentionally.")

        instance = instances[0]
        instance_id = instance.get("InstanceId", "")
        state = instance.get("State", {}).get("Name", "unknown")
        public_ip = instance.get("PublicIpAddress")
        private_ip = instance.get("PrivateIpAddress")
        key_name = instance.get("KeyName")
        instance_type = instance.get("InstanceType")
        image_id = instance.get("ImageId")
        iam_profile = instance.get("IamInstanceProfile", {}).get("Arn", "")

        print(f"Instance ID: {instance_id}")
        print(f"State: {state}")
        print(f"Instance type: {instance_type}")
        print(f"AMI/Image ID: {image_id}")
        print(f"Public IPv4: {public_ip or 'MISSING'}")
        print(f"Private IPv4: {private_ip or 'MISSING'}")
        print(f"Key pair: {key_name or 'MISSING'}")
        print(f"IAM instance profile: {iam_profile or 'MISSING'}")
        for sg in instance.get("SecurityGroups", []):
            print(f"Security group: {sg.get('GroupName')} ({sg.get('GroupId')})")
        print()

        warnings = []
        if state != "running":
            warnings.append("Instance is not running; SSH will not work until it is running.")
        if not public_ip:
            warnings.append("Public IPv4 is missing; SSH command cannot be built.")
        if key_name != EXPECTED_KEY_NAME:
            warnings.append(f"Expected key pair {EXPECTED_KEY_NAME}, found {key_name}.")
        if EXPECTED_ROLE_NAME not in iam_profile:
            warnings.append(f"Expected IAM profile containing {EXPECTED_ROLE_NAME}.")

        key_path = args.key_path
        if key_path:
            key = Path(key_path)
            print("== Local key file ==")
            if key.exists():
                print(f"OK: key file exists: {key}")
            else:
                warnings.append(f"Key file not found: {key}")
            print()
        else:
            key_path = r"C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem"
            print("INFO: --key-path not supplied; printing command with the expected project key path.")
            print()

        if warnings:
            print("== Warnings ==")
            for warning in warnings:
                print(f"WARN: {warning}")
            print()

        print("== SSH command ==")
        if public_ip:
            print(f'ssh -i "{key_path}" {args.ssh_user}@{public_ip}')
            print()
            print("If that fails due to AMI username, try:")
            print(f'ssh -i "{key_path}" ubuntu@{public_ip}')
            print()
            print("== SCP helper commands ==")
            print(f'scp -i "{key_path}" deploy\\ec2\\bootstrap_rsa_cms_server.sh {args.ssh_user}@{public_ip}:/tmp/bootstrap_rsa_cms_server.sh')
            print(f'scp -i "{key_path}" deploy\\ec2\\check_server_environment.sh {args.ssh_user}@{public_ip}:/tmp/check_server_environment.sh')
        else:
            print("Cannot print SSH command because Public IPv4 is missing.")

        print()
        print("Batch 35 EC2 SSH preflight completed.")
        return 0 if not warnings else 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
