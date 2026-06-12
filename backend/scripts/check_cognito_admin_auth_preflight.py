#!/usr/bin/env python3
"""
RSA CMS / Mini-CRM Batch 40 Cognito Admin Auth Preflight

Read-only checks only. This script does not create Cognito resources, users,
clients, domains, IAM policies, EC2 rules, or Nginx rules.

It verifies:
- expected local admin-auth prep files exist
- current environment variables are safe/default unless explicitly testing Cognito
- optional Cognito read-only lookup when env vars and boto3 are available
- optional public URL still blocks admin/admin APIs before Batch 41
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"

EXPECTED_LOCAL_FILES = [
    "backend/app/auth/admin_auth.py",
    "backend/app/routes/admin_auth.py",
    "backend/app/main.py",
    "frontend/admin/login.html",
    "frontend/admin/assets/js/admin-auth.js",
    "frontend/admin/assets/css/admin-auth.css",
    "deploy/cognito/admin-auth.ec2.env.example",
    "docs/phase8_batch40_cognito_admin_auth_preflight.md",
    "docs/phase8_batch40_cognito_setup_checklist.md",
]

BLOCKED_PATHS = [
    "/admin/",
    "/api/admin/products",
    "/api/customers",
    "/api/bookings",
    "/api/inquiries",
    "/docs",
    "/redoc",
    "/openapi.json",
]

PUBLIC_PATHS = [
    "/",
    "/api/health",
]


def print_header(title: str) -> None:
    print(f"\n== {title} ==")


def check_files() -> int:
    print_header("Local Batch 40/admin-auth files")
    issues = 0
    for rel in EXPECTED_LOCAL_FILES:
        path = PROJECT_ROOT / rel
        if path.exists():
            print(f"OK: {rel}")
        else:
            print(f"WARN: missing {rel}")
            # Existing Batch 23 files may be named differently in older working copies;
            # warn rather than fail for this preflight.
            issues += 1
    return 0


def load_env_example() -> Dict[str, str]:
    env_path = PROJECT_ROOT / "deploy" / "cognito" / "admin-auth.ec2.env.example"
    values: Dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(key: str, example_values: Dict[str, str]) -> Optional[str]:
    return os.environ.get(key) or example_values.get(key)


def check_env() -> Tuple[int, Dict[str, Optional[str]]]:
    print_header("Admin auth environment readiness")
    example_values = load_env_example()
    keys = [
        "RSA_ADMIN_AUTH_MODE",
        "RSA_COGNITO_USER_POOL_ID",
        "RSA_COGNITO_APP_CLIENT_ID",
        "RSA_COGNITO_REGION",
        "AWS_DEFAULT_REGION",
        "AWS_REGION",
    ]
    resolved: Dict[str, Optional[str]] = {key: env_value(key, example_values) for key in keys}

    for key in keys:
        val = resolved.get(key)
        if val:
            masked = val if "CLIENT" not in key and "POOL" not in key else val[:8] + "..." if len(val) > 8 else val
            print(f"{key}={masked}")
        else:
            print(f"{key}=<not set>")

    mode = (resolved.get("RSA_ADMIN_AUTH_MODE") or "disabled").lower()
    if mode == "disabled":
        print("OK: RSA_ADMIN_AUTH_MODE is disabled/preflight-safe. Do not expose admin publicly yet.")
    elif mode == "cognito":
        missing = [
            key for key in ["RSA_COGNITO_USER_POOL_ID", "RSA_COGNITO_APP_CLIENT_ID"] if not resolved.get(key)
        ]
        if missing:
            print(f"FAIL: Cognito mode selected but missing: {', '.join(missing)}")
            return 1, resolved
        print("OK: Cognito mode variables look present for the next activation batch.")
    else:
        print(f"WARN: unexpected RSA_ADMIN_AUTH_MODE={mode}; expected disabled or cognito.")

    region = resolved.get("RSA_COGNITO_REGION") or resolved.get("AWS_REGION") or resolved.get("AWS_DEFAULT_REGION")
    if region and region != "ap-southeast-1":
        print(f"WARN: Cognito/AWS region is {region}; project deployment region is ap-southeast-1.")
    else:
        print("OK: Region is unset or ap-southeast-1.")
    return 0, resolved


def optional_cognito_lookup(resolved: Dict[str, Optional[str]]) -> int:
    print_header("Optional Cognito read-only lookup")
    user_pool_id = resolved.get("RSA_COGNITO_USER_POOL_ID")
    app_client_id = resolved.get("RSA_COGNITO_APP_CLIENT_ID")
    region = resolved.get("RSA_COGNITO_REGION") or resolved.get("AWS_REGION") or resolved.get("AWS_DEFAULT_REGION") or "ap-southeast-1"

    if not user_pool_id or not app_client_id:
        print("SKIP: Cognito IDs are not set yet. This is OK before manual Cognito setup.")
        return 0

    try:
        import boto3  # type: ignore
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on local environment
        print(f"SKIP: boto3/botocore not available for optional Cognito lookup ({exc}).")
        return 0

    try:
        client = boto3.client("cognito-idp", region_name=region)
        pool = client.describe_user_pool(UserPoolId=user_pool_id)["UserPool"]
        app = client.describe_user_pool_client(UserPoolId=user_pool_id, ClientId=app_client_id)["UserPoolClient"]
        print(f"OK: user pool visible: {pool.get('Name')} ({user_pool_id})")
        print(f"OK: app client visible: {app.get('ClientName')} ({app_client_id[:8]}...)")
        mfa = pool.get("MfaConfiguration", "UNKNOWN")
        print(f"INFO: MfaConfiguration={mfa}")
        explicit_flows = app.get("ExplicitAuthFlows", [])
        print("INFO: App client explicit auth flows:", ", ".join(explicit_flows) if explicit_flows else "<none listed>")
        return 0
    except Exception as exc:  # pragma: no cover - depends on AWS permissions
        print(f"WARN: Cognito read-only lookup failed: {exc}")
        print("This is not a blocker if you have not granted Cognito read-only permissions to the CLI user yet.")
        return 0


def http_get(base_url: str, path: str, timeout: int = 8) -> Tuple[Optional[int], str]:
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "rsa-cms-batch40-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(200).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(200).decode("utf-8", errors="replace")
    except Exception as exc:
        return None, str(exc)


def check_public_lockdown(base_url: Optional[str]) -> int:
    print_header("Optional public URL lockdown check")
    if not base_url:
        print("SKIP: no --base-url provided.")
        return 0

    issues = 0
    for path in PUBLIC_PATHS:
        status, body = http_get(base_url, path)
        if status == 200:
            print(f"OK: GET {path} -> HTTP 200")
        else:
            print(f"FAIL: GET {path} -> {status} ({body[:120]})")
            issues += 1

    for path in BLOCKED_PATHS:
        status, body = http_get(base_url, path)
        if status == 403:
            print(f"OK: GET {path} -> HTTP 403")
        else:
            print(f"FAIL: GET {path} -> {status}; expected 403 ({body[:120]})")
            issues += 1
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 40 Cognito admin auth preflight checks")
    parser.add_argument("--base-url", help="Optional public EC2 base URL, e.g. http://54.179.42.39")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 40 Cognito Admin Auth Preflight")
    print("Mode: READ ONLY")
    print("No AWS resources or EC2/Nginx resources will be created, updated, or deleted.")
    print(f"Project root: {PROJECT_ROOT}")

    issues = 0
    issues += check_files()
    env_issues, resolved = check_env()
    issues += env_issues
    issues += optional_cognito_lookup(resolved)
    issues += check_public_lockdown(args.base_url)

    print_header("Summary")
    if issues:
        print(f"Batch 40 Cognito admin auth preflight completed with {issues} issue(s).")
        return 1
    print("Batch 40 Cognito admin auth preflight PASSED/readiness checks completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
