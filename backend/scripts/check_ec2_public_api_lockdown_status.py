#!/usr/bin/env python3
"""RSA CMS Batch 38 EC2 public API lockdown status check.

Read-only by default:
- Finds the EC2 demo instance by Name tag.
- Checks security-group exposure for SSH/HTTP/8000.
- Checks public website/API/admin-blocking through Nginx.
- Confirms direct public port 8000 is not reachable.

Optional write check:
- Use --execute-public-form-write --confirm-write-test to submit one booking
  and one inquiry through the public port-80 Nginx route.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import socket
import sys
from typing import Any
from urllib import error, request

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None

EXPECTED_REGION = "ap-southeast-1"
EXPECTED_INSTANCE_NAME = "rsa-cms-demo-backend"
EXPECTED_SECURITY_GROUP = "rsa-cms-demo-backend-sg"


class CheckFailure(Exception):
    """Raised when a required check fails."""


def _http_request(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 10) -> tuple[int | None, str]:
    data = None
    headers = {"Accept": "application/json,text/html"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read(800).decode("utf-8", errors="replace")
            return response.status, body
    except error.HTTPError as exc:
        body = exc.read(800).decode("utf-8", errors="replace")
        return exc.code, body
    except (error.URLError, TimeoutError, socket.timeout, ConnectionError, OSError) as exc:
        return None, str(exc)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def _print_pass(message: str) -> None:
    print(f"PASS  {message}")


def _print_warn(message: str) -> None:
    print(f"WARN  {message}")


def _port_label(permission: dict[str, Any]) -> str:
    proto = permission.get("IpProtocol")
    if proto == "-1":
        return "all"
    from_port = permission.get("FromPort")
    to_port = permission.get("ToPort")
    if from_port == to_port:
        return str(from_port)
    return f"{from_port}-{to_port}"


def _permission_includes_port(permission: dict[str, Any], port: int) -> bool:
    proto = permission.get("IpProtocol")
    if proto == "-1":
        return True
    if proto not in ("tcp", "6"):
        return False
    from_port = permission.get("FromPort")
    to_port = permission.get("ToPort")
    if from_port is None or to_port is None:
        return False
    return int(from_port) <= port <= int(to_port)


def _sources(permission: dict[str, Any]) -> list[str]:
    values = [r.get("CidrIp") for r in permission.get("IpRanges", []) if r.get("CidrIp")]
    values.extend(r.get("CidrIpv6") for r in permission.get("Ipv6Ranges", []) if r.get("CidrIpv6"))
    values.extend(pair.get("GroupId") for pair in permission.get("UserIdGroupPairs", []) if pair.get("GroupId"))
    return values


def _is_public_source(source: str) -> bool:
    return source in {"0.0.0.0/0", "::/0"}


def _check_security_group(groups: list[dict[str, Any]]) -> None:
    print("\n== Security group exposure check ==")
    found_expected = False
    port_80_ok = False
    port_8000_public = False
    risky_public = False

    for group in groups:
        group_name = group.get("GroupName")
        group_id = group.get("GroupId")
        print(f"Security group: {group_name} ({group_id})")
        if group_name == EXPECTED_SECURITY_GROUP:
            found_expected = True
        for perm in group.get("IpPermissions", []):
            ports = _port_label(perm)
            sources = _sources(perm)
            print(f"  Inbound: protocol={perm.get('IpProtocol')}, ports={ports}, sources={sources}")
            for source in sources:
                if _permission_includes_port(perm, 80) and not _is_public_source(source):
                    port_80_ok = True
                if _permission_includes_port(perm, 8000):
                    port_8000_public = True
                if _is_public_source(source) and any(_permission_includes_port(perm, p) for p in (22, 80, 443, 8000, 3389)):
                    risky_public = True

    _require(found_expected, f"expected security group not attached/found: {EXPECTED_SECURITY_GROUP}")
    _require(port_80_ok, "HTTP port 80 should be open only to your current IP /32 for this demo")
    _require(not port_8000_public, "direct public port 8000 is still open; remove it from inbound rules")
    _require(not risky_public, "risky public inbound source found for SSH/HTTP/HTTPS/8000/RDP")
    _print_pass("security group has HTTP 80 for a limited source and no direct public 8000")


def _expect(method: str, base_url: str, path: str, expected: int, timeout: int = 10) -> str:
    status, body = _http_request(method, f"{base_url}{path}", timeout=timeout)
    print(f"{method} {path} -> {status} (expected {expected})")
    if status != expected:
        preview = body[:240].replace("\n", " ")
        raise CheckFailure(f"{method} {path} expected {expected}, got {status}. Body/error: {preview}")
    return body


def _check_public_http(public_ip: str) -> None:
    print("\n== Public HTTP checks through Nginx ==")
    base = f"http://{public_ip}"
    for path in [
        "/",
        "/index.html",
        "/products.html",
        "/promotions.html",
        "/brands.html",
        "/about.html",
        "/services.html",
        "/contact-us.html",
        "/booking.html",
    ]:
        _expect("GET", base, path, 200)

    for path in [
        "/api/health",
        "/api/products",
        "/api/brands",
        "/api/categories",
        "/api/package-banners",
        "/api/pages/contact",
    ]:
        _expect("GET", base, path, 200)

    print("\n== Blocked public admin/management checks through Nginx ==")
    for path in [
        "/admin/",
        "/api/admin/products",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
        "/docs",
        "/openapi.json",
    ]:
        _expect("GET", base, path, 403)

    print("\n== Direct backend port 8000 exposure check ==")
    status, body = _http_request("GET", f"http://{public_ip}:8000/api/health", timeout=4)
    print(f"GET http://{public_ip}:8000/api/health -> {status} (expected unreachable/blocked)")
    if status is not None:
        raise CheckFailure("direct public port 8000 is reachable; remove port 8000 from security group inbound rules")
    _print_pass("direct public port 8000 is not reachable")


def _post_json(base_url: str, path: str, payload: dict[str, Any], id_field: str) -> None:
    status, body = _http_request("POST", f"{base_url}{path}", payload=payload, timeout=20)
    print(f"POST {path} -> {status} (expected 200/201)")
    _require(status in (200, 201), f"POST {path} failed: HTTP {status}, {body[:300]}")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise CheckFailure(f"POST {path} returned non-JSON body: {body[:300]}") from exc
    item_id = parsed.get(id_field)
    _require(bool(item_id), f"POST {path} response missing {id_field}: {parsed}")
    _print_pass(f"{path} public form write created {item_id}")


def _check_public_writes(public_ip: str) -> None:
    print("\n== Optional public form write checks through Nginx ==")
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    base = f"http://{public_ip}"
    _post_json(base, "/api/bookings", {
        "customer_name": f"Batch 38 EC2 Booking Test {suffix}",
        "contact_number": "+63 919 138 3800",
        "email": f"batch38.booking.{suffix}@example.com",
        "address": "Batch 38 EC2 public Nginx form test",
        "preferred_date": "2026-12-30",
        "preferred_time": "Morning",
        "service_interest": "CCTV Installation",
        "notes": "Batch 38 public Nginx booking test.",
    }, "booking_id")
    _post_json(base, "/api/inquiries", {
        "customer_name": f"Batch 38 EC2 Inquiry Test {suffix}",
        "contact_number": "0919 138 3801",
        "email": f"batch38.inquiry.{suffix}@example.com",
        "subject": "Batch 38 EC2 public inquiry test",
        "message": "Batch 38 public Nginx inquiry test.",
        "source_page": "Batch 38 EC2 Public Site",
        "product_id": "CCTV-0000001",
    }, "inquiry_id")


def _find_instance() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if boto3 is None:
        raise CheckFailure("boto3 is not installed in this venv")
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
    if not instances:
        raise CheckFailure(f"EC2 demo instance not found by Name tag: {EXPECTED_INSTANCE_NAME}")
    instance = instances[0]
    sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
    groups = ec2.describe_security_groups(GroupIds=sg_ids).get("SecurityGroups", []) if sg_ids else []
    return instance, groups


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 38 EC2 public API lockdown status.")
    parser.add_argument("--public-ip", help="Override public IP instead of reading EC2 by Name tag.")
    parser.add_argument("--skip-aws", action="store_true", help="Skip AWS/security-group lookup and only run HTTP checks.")
    parser.add_argument("--execute-public-form-write", action="store_true", help="Create one booking and one inquiry through public Nginx routes.")
    parser.add_argument("--confirm-write-test", action="store_true", help="Required with --execute-public-form-write.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 38 EC2 Public API Lockdown Check")
    print("Mode: READ ONLY" if not args.execute_public_form_write else "Mode: EXECUTE PUBLIC FORM WRITE TEST")
    print(f"Expected region: {EXPECTED_REGION}")

    if args.execute_public_form_write and not args.confirm_write_test:
        print("Refusing public form write test without --confirm-write-test.")
        return 2

    try:
        public_ip = args.public_ip
        if not args.skip_aws:
            instance, groups = _find_instance()
            state = instance.get("State", {}).get("Name")
            public_ip = public_ip or instance.get("PublicIpAddress")
            print("\n== EC2 demo instance ==")
            print(f"Instance ID: {instance.get('InstanceId')}")
            print(f"State: {state}")
            print(f"Public IPv4: {public_ip}")
            print(f"IAM profile: {instance.get('IamInstanceProfile', {}).get('Arn', 'NONE')}")
            _require(state == "running", "EC2 instance must be running for Batch 38 checks")
            _require(bool(public_ip), "running EC2 instance has no public IPv4")
            _check_security_group(groups)
        else:
            _require(bool(public_ip), "--public-ip is required when --skip-aws is used")

        assert public_ip is not None
        _check_public_http(public_ip)
        if args.execute_public_form_write:
            _check_public_writes(public_ip)
        else:
            print("\nPublic form write checks skipped. Add --execute-public-form-write --confirm-write-test when needed.")
    except CheckFailure as exc:
        print(f"\nFAILED: {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"\nERROR: {type(exc).__name__}: {exc}")
        return 1

    print("\nBatch 38 EC2 public API lockdown check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
