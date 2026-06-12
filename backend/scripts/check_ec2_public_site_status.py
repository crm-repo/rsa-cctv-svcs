#!/usr/bin/env python3
"""RSA CMS Batch 37 public-site status check.

Read-only local script. It does not create/update/delete AWS resources.
It checks the demo instance, security group rules, and HTTP endpoints through
EC2 public IPv4 when reachable from the current network.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None

EXPECTED_REGION = "ap-southeast-1"
EXPECTED_INSTANCE_NAME = "rsa-cms-demo-backend"
EXPECTED_SECURITY_GROUP = "rsa-cms-demo-backend-sg"


def http_get(url: str, timeout: int = 10) -> tuple[int | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read(500).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(500).decode("utf-8", errors="replace")
        return exc.code, body
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def main() -> int:
    print("RSA CMS Batch 37 EC2 public-site status check")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, or deleted.")

    if boto3 is None:
        print("FAIL: boto3 is not installed in this venv.")
        return 1

    session = boto3.Session(region_name=EXPECTED_REGION)
    sts = session.client("sts")
    identity = sts.get_caller_identity()
    print("\n== AWS identity ==")
    print(f"Account: {identity.get('Account')}")
    print(f"ARN: {identity.get('Arn')}")

    ec2 = session.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [EXPECTED_INSTANCE_NAME]},
            {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
        ]
    )
    instances: list[dict[str, Any]] = []
    for reservation in response.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))

    print("\n== EC2 demo instance ==")
    if not instances:
        print("FAIL: demo instance not found. Start Batch 34/36 instance first.")
        return 1
    instance = instances[0]
    instance_id = instance.get("InstanceId")
    state = instance.get("State", {}).get("Name")
    public_ip = instance.get("PublicIpAddress")
    print(f"Instance ID: {instance_id}")
    print(f"State: {state}")
    print(f"Public IPv4: {public_ip}")
    print(f"IAM profile: {instance.get('IamInstanceProfile', {}).get('Arn', 'NONE')}")

    sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
    if sg_ids:
        groups = ec2.describe_security_groups(GroupIds=sg_ids).get("SecurityGroups", [])
    else:
        groups = []

    print("\n== Security group inbound rules ==")
    for group in groups:
        print(f"Security group: {group.get('GroupName')} ({group.get('GroupId')})")
        for perm in group.get("IpPermissions", []):
            proto = perm.get("IpProtocol")
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            ranges = [r.get("CidrIp") for r in perm.get("IpRanges", [])]
            ipv6_ranges = [r.get("CidrIpv6") for r in perm.get("Ipv6Ranges", [])]
            print(f"Inbound: protocol={proto}, ports={from_port}-{to_port}, IPv4={ranges}, IPv6={ipv6_ranges}")

    if state != "running":
        print("\nINFO: Instance is not running, so HTTP checks are skipped.")
        return 0
    if not public_ip:
        print("FAIL: Running instance has no public IPv4.")
        return 1

    print("\n== Public HTTP checks from this computer ==")
    checks = [
        (f"http://{public_ip}/", "200"),
        (f"http://{public_ip}/api/health", "200"),
        (f"http://{public_ip}/api/products", "200"),
        (f"http://{public_ip}/admin/", "403"),
    ]
    failures = 0
    for url, expected in checks:
        status, body = http_get(url)
        print(f"GET {url} -> {status} (expected {expected})")
        if status is None:
            print(f"  Error: {body}")
            failures += 1
        elif str(status) != expected:
            print(f"  Body preview: {body[:200]}")
            failures += 1

    if failures:
        print("\nBatch 37 public-site status check completed with issues.")
        return 1
    print("\nBatch 37 public-site status check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
