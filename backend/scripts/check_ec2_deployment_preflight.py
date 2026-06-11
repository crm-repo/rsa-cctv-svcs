"""RSA CMS / Mini-CRM Batch 31 EC2 public-IP deployment preflight.

Read-only local/AWS checks only. This script does not create, update, or delete
AWS resources.

It checks:
- Local project files expected before deployment planning
- Local backend import readiness
- AWS CLI identity and region
- Basic EC2 read permissions
- Existing running EC2 instances in the project region
- Existing security groups with RSA-like names, if readable

Use this before creating any EC2 instance.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import json


DEFAULT_REGION = "ap-southeast-1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def run(cmd: list[str], cwd: Path | None = None, allow_fail: bool = False) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0 and not allow_fail:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_aws(args: list[str], allow_fail: bool = True) -> tuple[int, str, str]:
    return run(["aws", *args], allow_fail=allow_fail)


def load_json(text: str) -> dict:
    if not text:
        return {}
    return json.loads(text)


def section(title: str) -> None:
    print(f"\n== {title} ==")


def check_file(path: Path, label: str, required: bool = True) -> None:
    status = "OK" if path.exists() else ("MISSING" if required else "NOTE")
    print(f"{status}: {label} -> {path.relative_to(PROJECT_ROOT) if path.is_absolute() and PROJECT_ROOT in path.parents else path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 31 EC2 deployment preflight read-only check")
    parser.add_argument("--region", default=DEFAULT_REGION)
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 31 EC2 Public-IP Deployment Preflight")
    print("Mode: READ ONLY")
    print("No AWS resources will be created, updated, or deleted.")
    print(f"Project root: {PROJECT_ROOT}")

    section("Local project files")
    check_file(BACKEND_DIR / "app" / "main.py", "FastAPI app entry")
    check_file(BACKEND_DIR / "requirements.txt", "Backend requirements")
    check_file(BACKEND_DIR / ".env.example", "Backend .env example", required=False)
    check_file(PROJECT_ROOT / ".gitignore", "Repository .gitignore")
    check_file(FRONTEND_DIR / "index.html", "Frontend homepage")
    check_file(FRONTEND_DIR / "admin" / "index.html", "Admin dashboard shell")
    check_file(PROJECT_ROOT / "docs" / "phase8_aws_cost_safety_billing_alerts_checklist.md", "Batch 30 cost safety checklist", required=False)
    check_file(PROJECT_ROOT / "docs" / "phase8_ec2_public_ip_deployment_preflight.md", "Batch 31 preflight checklist", required=False)

    section("Local backend import check")
    rc, out, err = run(
        [sys.executable, "-c", "from app.main import app; print('OK FastAPI app import')"],
        cwd=BACKEND_DIR,
        allow_fail=True,
    )
    if rc == 0:
        print(out)
    else:
        print("WARN: FastAPI app import failed. Fix this before deployment.")
        print(err)

    section("AWS CLI identity")
    if not shutil.which("aws"):
        print("WARN: AWS CLI not found in PATH.")
        print("Install/configure AWS CLI before EC2 deployment.")
        return 0

    rc, out, err = run_aws(["sts", "get-caller-identity", "--output", "json"])
    if rc == 0:
        identity = load_json(out)
        print(f"Account: {identity.get('Account', 'UNKNOWN')}")
        print(f"ARN: {identity.get('Arn', 'UNKNOWN')}")
    else:
        print("WARN: Unable to read AWS identity.")
        print(err)

    section("AWS region")
    rc, out, err = run_aws(["configure", "get", "region"])
    configured = out or "(not configured)"
    print(f"Configured default region: {configured}")
    print(f"Project deployment/test region: {args.region}")
    if configured != args.region:
        print("NOTE: Use --region explicitly when creating deployment resources.")

    section("EC2 read permission check")
    rc, out, err = run_aws([
        "ec2",
        "describe-instances",
        "--region",
        args.region,
        "--filters",
        "Name=instance-state-name,Values=pending,running,stopping,stopped",
        "--output",
        "json",
    ])
    if rc != 0:
        print("WARN: Unable to describe EC2 instances with current IAM user.")
        print("This is expected if the CLI user only has DynamoDB permissions.")
        print("Before deployment, add/read EC2 permissions only as needed or use a deployment IAM user.")
        print(err)
    else:
        payload = load_json(out)
        instances = []
        for reservation in payload.get("Reservations", []):
            instances.extend(reservation.get("Instances", []))
        print(f"Visible non-terminated EC2 instances in {args.region}: {len(instances)}")
        for inst in instances[:20]:
            tags = {tag.get("Key"): tag.get("Value") for tag in inst.get("Tags", [])}
            print(
                f"  - {inst.get('InstanceId')} "
                f"{inst.get('InstanceType')} "
                f"{inst.get('State', {}).get('Name')} "
                f"name={tags.get('Name', '-')}"
            )

    section("Security group read check")
    rc, out, err = run_aws([
        "ec2",
        "describe-security-groups",
        "--region",
        args.region,
        "--output",
        "json",
    ])
    if rc != 0:
        print("WARN: Unable to describe security groups with current IAM user.")
        print(err)
    else:
        groups = load_json(out).get("SecurityGroups", [])
        rsa_like = [
            sg for sg in groups
            if "rsa" in (sg.get("GroupName", "") + " " + sg.get("Description", "")).lower()
        ]
        print(f"Security groups visible: {len(groups)}")
        print(f"RSA-like security groups visible: {len(rsa_like)}")
        for sg in rsa_like[:20]:
            print(f"  - {sg.get('GroupId')} {sg.get('GroupName')}")

    section("Manual go/no-go reminders")
    print("[ ] AWS Budget/cost alert manually confirmed.")
    print("[ ] Free-Tier deployment review completed.")
    print("[ ] Public IPv4 hourly charge accepted for temporary public-IP demo.")
    print("[ ] No Elastic IP unless explicitly approved.")
    print("[ ] No NAT Gateway, ALB, RDS, or paid SMS/MFA.")
    print("[ ] SSH restricted to your IP only.")
    print("[ ] Admin not exposed publicly until Cognito enforcement is enabled.")
    print("[ ] Use EC2 public IP first; Route 53/domain later.")

    print("\nBatch 31 EC2 deployment preflight read-only check completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
