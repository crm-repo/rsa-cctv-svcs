"""
RSA CMS / Mini-CRM Phase 8 Batch 34
EC2 demo instance status checker.

READ ONLY:
- Does not create EC2 instances.
- Does not create or modify security groups.
- Does not start, stop, or terminate instances.
- Does not attach/detach IAM roles or policies.

Run from backend folder:
    python scripts/check_ec2_demo_instance_status.py
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable

PROJECT_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "ap-southeast-1"
EXPECTED_ACCOUNT_ID = "537765358118"
EXPECTED_INSTANCE_NAME = "rsa-cms-demo-backend"
EXPECTED_SECURITY_GROUP_NAME = "rsa-cms-demo-backend-sg"
EXPECTED_ROLE_NAME = "rsa-cms-ec2-backend-role"
RISKY_PORTS = {22, 80, 443, 8000, 3389}


@dataclass
class CheckResult:
    warnings: int = 0
    errors: int = 0

    def warn(self, message: str) -> None:
        self.warnings += 1
        print(f"WARN: {message}")

    def error(self, message: str) -> None:
        self.errors += 1
        print(f"ERROR: {message}")


def _load_boto3():
    try:
        import boto3  # type: ignore
        from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local env
        print("ERROR: boto3/botocore is not available in this Python environment.")
        print("Install backend requirements first, then rerun this script.")
        print(f"Details: {exc}")
        sys.exit(2)
    return boto3, ClientError, NoCredentialsError


def _tag_value(tags: list[dict[str, Any]] | None, key: str) -> str | None:
    for tag in tags or []:
        if tag.get("Key") == key:
            return tag.get("Value")
    return None


def _format_rule(rule: dict[str, Any]) -> str:
    proto = rule.get("IpProtocol", "?")
    from_port = rule.get("FromPort")
    to_port = rule.get("ToPort")
    port_text = "all" if from_port is None else str(from_port) if from_port == to_port else f"{from_port}-{to_port}"
    sources: list[str] = []
    for item in rule.get("IpRanges", []):
        sources.append(item.get("CidrIp", "?"))
    for item in rule.get("Ipv6Ranges", []):
        sources.append(item.get("CidrIpv6", "?"))
    for item in rule.get("UserIdGroupPairs", []):
        sources.append(item.get("GroupId", "security-group-source"))
    return f"protocol={proto}, ports={port_text}, sources={sources or ['none']}"


def _rule_allows_port(rule: dict[str, Any], port: int) -> bool:
    proto = rule.get("IpProtocol")
    if proto == "-1":
        return True
    if proto not in {"tcp", "6"}:
        return False
    from_port = rule.get("FromPort")
    to_port = rule.get("ToPort")
    if from_port is None or to_port is None:
        return False
    return int(from_port) <= port <= int(to_port)


def _is_public_source(rule: dict[str, Any]) -> bool:
    for item in rule.get("IpRanges", []):
        if item.get("CidrIp") == "0.0.0.0/0":
            return True
    for item in rule.get("Ipv6Ranges", []):
        if item.get("CidrIpv6") == "::/0":
            return True
    return False


def _check_security_group_rules(result: CheckResult, groups: Iterable[dict[str, Any]]) -> None:
    for group in groups:
        group_name = group.get("GroupName")
        group_id = group.get("GroupId")
        print(f"\nSecurity group: {group_name} ({group_id})")
        inbound_rules = group.get("IpPermissions", [])
        if not inbound_rules:
            print("OK: no inbound rules")
            continue

        risky_found = False
        for rule in inbound_rules:
            rule_text = _format_rule(rule)
            print(f"Inbound: {rule_text}")
            if _is_public_source(rule):
                for port in RISKY_PORTS:
                    if _rule_allows_port(rule, port):
                        risky_found = True
                        result.warn(
                            f"public inbound access found on port {port} for {group_name}. "
                            "For Batch 34, SSH/8000 must be your IP /32 only; 80/443 are not opened yet."
                        )
        if not risky_found:
            print("OK: no risky public inbound rule found for SSH/8000/80/443/RDP")


def main() -> int:
    boto3, ClientError, NoCredentialsError = _load_boto3()
    result = CheckResult()

    print("RSA CMS / Mini-CRM Batch 34 EC2 Demo Instance Status Check")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, started, stopped, or deleted.")
    print(f"Expected region: {PROJECT_REGION}")
    print(f"Expected instance name: {EXPECTED_INSTANCE_NAME}")

    session = boto3.Session(region_name=PROJECT_REGION)
    sts = session.client("sts")
    ec2 = session.client("ec2")

    print("\n== AWS CLI identity ==")
    try:
        identity = sts.get_caller_identity()
    except NoCredentialsError:
        result.error("AWS credentials were not found. Run aws configure or use the configured project profile.")
        return 2
    except Exception as exc:
        result.error(f"Could not read AWS caller identity: {exc}")
        return 2

    account = identity.get("Account")
    arn = identity.get("Arn")
    print(f"Account: {account}")
    print(f"ARN: {arn}")
    if account != EXPECTED_ACCOUNT_ID:
        result.warn(f"Expected AWS account {EXPECTED_ACCOUNT_ID}, but current account is {account}.")

    print("\n== Search for EC2 demo instance ==")
    try:
        response = ec2.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [EXPECTED_INSTANCE_NAME]},
                {"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]},
            ]
        )
    except ClientError as exc:
        result.error(f"Cannot describe EC2 instances: {exc}")
        return 2

    instances: list[dict[str, Any]] = []
    for reservation in response.get("Reservations", []):
        instances.extend(reservation.get("Instances", []))

    if not instances:
        print("No EC2 demo instance found yet.")
        print("This is OK before Batch 34 manual launch.")
        print("After launch, rerun this script to verify the instance and security group.")
        print("\nBatch 34 EC2 demo instance status check completed.")
        return 0

    if len(instances) > 1:
        result.warn(f"Found {len(instances)} demo instances with Name={EXPECTED_INSTANCE_NAME}. Expected only one.")

    group_ids: set[str] = set()
    for instance in instances:
        instance_id = instance.get("InstanceId")
        name = _tag_value(instance.get("Tags"), "Name")
        state = instance.get("State", {}).get("Name")
        instance_type = instance.get("InstanceType")
        public_ip = instance.get("PublicIpAddress")
        private_ip = instance.get("PrivateIpAddress")
        key_name = instance.get("KeyName")
        image_id = instance.get("ImageId")
        iam_profile = instance.get("IamInstanceProfile", {}).get("Arn", "")

        print(f"\nFound EC2 demo instance: {name}")
        print(f"Instance ID: {instance_id}")
        print(f"State: {state}")
        print(f"Instance type: {instance_type}")
        print(f"AMI/Image ID: {image_id}")
        print(f"Public IPv4: {public_ip or 'none'}")
        print(f"Private IPv4: {private_ip or 'none'}")
        print(f"Key pair: {key_name or 'none'}")
        print(f"IAM instance profile: {iam_profile or 'none'}")

        if state != "running":
            result.warn("Instance is not running. This is OK if intentionally stopped, but app testing needs it running.")
        if not public_ip and state == "running":
            result.warn("Running instance has no public IPv4. Public-IP demo testing will not work until enabled.")
        if EXPECTED_ROLE_NAME not in iam_profile:
            result.warn(f"IAM instance profile does not visibly include {EXPECTED_ROLE_NAME}.")

        security_groups = instance.get("SecurityGroups", [])
        if not security_groups:
            result.warn("Instance has no security groups listed.")
        for sg in security_groups:
            sg_id = sg.get("GroupId")
            sg_name = sg.get("GroupName")
            print(f"Attached security group: {sg_name} ({sg_id})")
            if sg_id:
                group_ids.add(sg_id)
            if sg_name != EXPECTED_SECURITY_GROUP_NAME:
                result.warn(
                    f"Attached security group is {sg_name}; expected {EXPECTED_SECURITY_GROUP_NAME}."
                )

    print("\n== Security group rule check ==")
    if group_ids:
        try:
            sg_response = ec2.describe_security_groups(GroupIds=sorted(group_ids))
            _check_security_group_rules(result, sg_response.get("SecurityGroups", []))
        except ClientError as exc:
            result.warn(f"Cannot describe attached security group rules: {exc}")
    else:
        result.warn("No attached security group IDs were found to inspect.")

    print("\n== Batch 34 status summary ==")
    if result.errors:
        print(f"Completed with {result.errors} error(s) and {result.warnings} warning(s).")
        return 2
    if result.warnings:
        print(f"Completed with {result.warnings} warning(s). Review warnings before app deployment.")
        return 1

    print("OK: EC2 demo instance and attached security group look ready for the next backend deployment batch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
