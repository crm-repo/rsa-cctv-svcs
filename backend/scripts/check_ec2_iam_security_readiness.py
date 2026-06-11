"""RSA CMS / Mini-CRM Batch 32 EC2 IAM and security readiness check.

Read-only local/AWS checks only. This script does not create, update, attach,
detach, or delete AWS resources.

It checks:
- AWS identity and default/project region
- Whether EC2/security-group read permissions are available
- Whether visible security groups contain risky public inbound rules
- Whether IAM read permissions are available for the current CLI user
- Whether the local deployment templates exist

This is a safety companion for the manual IAM/security checklist.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import shutil
import subprocess


DEFAULT_REGION = "ap-southeast-1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


RISKY_PORTS = {
    22: "SSH",
    3389: "RDP",
    8000: "Temporary FastAPI/Uvicorn",
    80: "HTTP",
    443: "HTTPS",
}


def run(cmd: list[str], allow_fail: bool = True) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def aws(args: list[str]) -> tuple[int, str, str]:
    return run(["aws", *args], allow_fail=True)


def as_json(text: str) -> dict:
    if not text:
        return {}
    return json.loads(text)


def section(title: str) -> None:
    print(f"\n== {title} ==")


def is_public_cidr(ip_range: dict) -> bool:
    return ip_range.get("CidrIp") == "0.0.0.0/0"


def is_public_ipv6(ip_range: dict) -> bool:
    return ip_range.get("CidrIpv6") == "::/0"


def permission_covers_port(permission: dict, port: int) -> bool:
    proto = permission.get("IpProtocol")
    if proto == "-1":
        return True
    from_port = permission.get("FromPort")
    to_port = permission.get("ToPort")
    if from_port is None or to_port is None:
        return False
    return int(from_port) <= port <= int(to_port)


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 32 EC2 IAM/security readiness check")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--user-name", default="rsa-cms-cli-user")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 32 EC2 IAM and Security Readiness Check")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, attached, detached, or deleted.")

    section("Local template files")
    expected = [
        "deploy/iam/rsa-cms-ec2-instance-dynamodb-policy.template.json",
        "deploy/iam/rsa-cms-ec2-deployment-readonly-policy.template.json",
        "deploy/iam/rsa-cms-ec2-instance-trust-policy.template.json",
        "deploy/ec2/security-group-rules.template.md",
        "docs/phase8_ec2_iam_security_checklist.md",
    ]
    for rel in expected:
        path = PROJECT_ROOT / rel
        print(("OK" if path.exists() else "MISSING") + f": {rel}")

    section("AWS CLI")
    if not shutil.which("aws"):
        print("WARN: AWS CLI not found.")
        return 0

    rc, out, err = aws(["sts", "get-caller-identity", "--output", "json"])
    identity = as_json(out) if rc == 0 else {}
    if rc == 0:
        print(f"Account: {identity.get('Account')}")
        print(f"ARN: {identity.get('Arn')}")
    else:
        print("WARN: unable to read caller identity")
        print(err)

    rc, out, err = aws(["configure", "get", "region"])
    configured_region = out or "(not configured)"
    print(f"Configured default region: {configured_region}")
    print(f"Project region: {args.region}")

    section("EC2/security-group read check")
    rc, out, err = aws(["ec2", "describe-instances", "--region", args.region, "--output", "json"])
    if rc == 0:
        reservations = as_json(out).get("Reservations", [])
        instance_count = sum(len(r.get("Instances", [])) for r in reservations)
        print(f"OK: can describe EC2 instances. Visible instances: {instance_count}")
    else:
        print("WARN: cannot describe EC2 instances with current IAM permissions.")
        print(err)

    rc, out, err = aws(["ec2", "describe-security-groups", "--region", args.region, "--output", "json"])
    if rc != 0:
        print("WARN: cannot describe security groups with current IAM permissions.")
        print(err)
    else:
        groups = as_json(out).get("SecurityGroups", [])
        print(f"OK: can describe security groups. Visible groups: {len(groups)}")
        risky = []
        for group in groups:
            group_name = group.get("GroupName", "")
            group_id = group.get("GroupId", "")
            for perm in group.get("IpPermissions", []):
                public_ranges = [r for r in perm.get("IpRanges", []) if is_public_cidr(r)]
                public_v6 = [r for r in perm.get("Ipv6Ranges", []) if is_public_ipv6(r)]
                if not public_ranges and not public_v6:
                    continue
                for port, label in RISKY_PORTS.items():
                    if permission_covers_port(perm, port):
                        risky.append((group_id, group_name, port, label))
        if risky:
            print("WARN: public inbound rules found:")
            for group_id, group_name, port, label in risky:
                print(f"  - {group_id} {group_name}: {port} ({label}) open to public internet")
        else:
            print("OK: no public inbound rules found for SSH/RDP/8000/80/443 in visible security groups.")

    section("IAM read check for deployment user")
    rc, out, err = aws(["iam", "list-attached-user-policies", "--user-name", args.user_name, "--output", "json"])
    if rc == 0:
        policies = as_json(out).get("AttachedPolicies", [])
        print(f"OK: can read attached policies for {args.user_name}. Count: {len(policies)}")
        for policy in policies:
            print(f"  - {policy.get('PolicyName')} ({policy.get('PolicyArn')})")
        admin_like = [p for p in policies if "AdministratorAccess" in (p.get("PolicyName") or "")]
        if admin_like:
            print("WARN: AdministratorAccess appears attached. Prefer least-privilege deployment permissions.")
    else:
        print(f"WARN: cannot read IAM policies for user {args.user_name}.")
        print("This is acceptable if the current CLI user has intentionally limited permissions.")
        print(err)

    section("Manual security confirmations")
    print("[ ] Do not store AWS access keys on EC2; use an EC2 instance role/instance profile.")
    print("[ ] EC2 instance role grants only required DynamoDB table/index access.")
    print("[ ] Deployment user does not use AdministratorAccess for normal work.")
    print("[ ] SSH inbound source is your current IP /32 only.")
    print("[ ] Port 8000 is temporary and your-IP-only, or closed behind nginx.")
    print("[ ] Admin is not exposed publicly until Cognito JWT enforcement is enabled.")
    print("[ ] No secrets or real .env files are committed.")
    print("[ ] Stop/terminate demo resources when not in use.")

    print("\nBatch 32 EC2 IAM/security readiness check completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
