#!/usr/bin/env python3
"""RSA CMS Batch 41 - Cognito admin user pool configuration check.

Read-only checker. It does not create, update, or delete Cognito resources.
Use after creating the Cognito user pool/app client manually.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, List, Optional


def _load_boto3():
    try:
        import boto3  # type: ignore
        from botocore.exceptions import ClientError, BotoCoreError  # type: ignore
        return boto3, ClientError, BotoCoreError
    except Exception as exc:  # pragma: no cover
        print("ERROR: boto3/botocore is required for this check.")
        print(f"Details: {exc}")
        return None, None, None


def _ok(message: str) -> None:
    print(f"OK: {message}")


def _warn(message: str) -> None:
    print(f"WARN: {message}")


def _fail(message: str, issues: List[str]) -> None:
    print(f"FAIL: {message}")
    issues.append(message)


def _get(dct: Dict[str, Any], key: str, default: Any = None) -> Any:
    value = dct.get(key)
    return default if value is None else value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Cognito admin user pool check for RSA CMS Batch 41."
    )
    parser.add_argument("--region", default=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-southeast-1")
    parser.add_argument("--user-pool-id", default=os.getenv("RSA_COGNITO_USER_POOL_ID") or os.getenv("COGNITO_USER_POOL_ID"))
    parser.add_argument("--client-id", default=os.getenv("RSA_COGNITO_CLIENT_ID") or os.getenv("COGNITO_CLIENT_ID"))
    parser.add_argument("--admin-email", default=os.getenv("RSA_COGNITO_ADMIN_EMAIL") or os.getenv("ADMIN_EMAIL"))
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 41 Cognito Admin User Pool Check")
    print("Mode: READ ONLY")
    print("No Cognito resources will be created, updated, or deleted.")
    print(f"Region: {args.region}")

    issues: List[str] = []
    if not args.user_pool_id:
        _fail("Missing --user-pool-id or RSA_COGNITO_USER_POOL_ID/COGNITO_USER_POOL_ID env var.", issues)
    if not args.client_id:
        _fail("Missing --client-id or RSA_COGNITO_CLIENT_ID/COGNITO_CLIENT_ID env var.", issues)
    if issues:
        print("\nExample:")
        print("python scripts\\check_cognito_admin_user_pool.py --user-pool-id ap-southeast-1_XXXXXXX --client-id abc123 --admin-email you@example.com")
        return 2

    boto3, ClientError, BotoCoreError = _load_boto3()
    if not boto3:
        return 2

    client = boto3.client("cognito-idp", region_name=args.region)

    print("\n== AWS/Cognito read check ==")
    try:
        pool_resp = client.describe_user_pool(UserPoolId=args.user_pool_id)
        pool = pool_resp["UserPool"]
        _ok(f"User pool found: {pool.get('Name')} ({pool.get('Id')})")
    except Exception as exc:
        _fail(f"Could not describe user pool {args.user_pool_id}: {exc}", issues)
        print("\nBatch 41 Cognito admin user pool check FAILED.")
        return 1

    try:
        client_resp = client.describe_user_pool_client(
            UserPoolId=args.user_pool_id,
            ClientId=args.client_id,
        )
        pool_client = client_resp["UserPoolClient"]
        _ok(f"App client found: {pool_client.get('ClientName')} ({pool_client.get('ClientId')})")
    except Exception as exc:
        _fail(f"Could not describe app client {args.client_id}: {exc}", issues)
        print("\nBatch 41 Cognito admin user pool check FAILED.")
        return 1

    print("\n== Free-Tier-safe / project safety checks ==")
    mfa = pool.get("MfaConfiguration", "OFF")
    if mfa == "OFF":
        _ok("MFA is OFF for launch/preflight.")
    else:
        _fail(f"MFA is {mfa}. For this project launch/preflight, keep MFA OFF to avoid SMS/MFA cost/drift.", issues)

    if pool.get("SmsConfiguration"):
        _fail("SmsConfiguration is present. Remove SMS configuration for Free-Tier-safe launch.", issues)
    else:
        _ok("No SMS configuration found.")

    auto_verified = set(pool.get("AutoVerifiedAttributes") or [])
    if "phone_number" in auto_verified:
        _fail("phone_number is auto-verified. Use email-only verification; do not use phone/SMS.", issues)
    else:
        _ok("Phone number is not auto-verified.")
    if "email" in auto_verified:
        _ok("Email auto-verification is enabled.")
    else:
        _warn("Email auto-verification not shown. This may be acceptable if admin-created temporary passwords are used, but email is preferred.")

    username_attrs = set(pool.get("UsernameAttributes") or [])
    alias_attrs = set(pool.get("AliasAttributes") or [])
    schema_attrs = {a.get("Name"): a for a in pool.get("SchemaAttributes", [])}
    if "email" in username_attrs or "email" in alias_attrs or schema_attrs.get("email", {}).get("Required"):
        _ok("Email is configured as a sign-in/alias/required user attribute.")
    else:
        _warn("Email was not detected as username/alias/required attribute. Verify admin login can use email.")

    admin_cfg = pool.get("AdminCreateUserConfig") or {}
    if admin_cfg.get("AllowAdminCreateUserOnly") is True:
        _ok("Self sign-up is disabled/admin-created users only.")
    else:
        _warn("AdminCreateUserOnly is not true. Confirm public self-registration is disabled for admin-only access.")

    account_recovery = pool.get("AccountRecoverySetting", {}).get("RecoveryMechanisms", [])
    recovery_names = [r.get("Name") for r in account_recovery]
    if "verified_phone_number" in recovery_names:
        _fail("Account recovery includes verified_phone_number. Use email-only recovery.", issues)
    elif "verified_email" in recovery_names:
        _ok("Account recovery uses verified_email.")
    else:
        _warn("Email account recovery not detected. Verify admin password reset flow manually.")

    print("\n== App client checks ==")
    if pool_client.get("ClientSecret"):
        _fail("App client has a client secret. Browser/admin frontend should use a public app client with no secret.", issues)
    else:
        _ok("App client has no client secret.")

    explicit_flows = set(pool_client.get("ExplicitAuthFlows") or [])
    useful_flows = {"ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"}
    if explicit_flows & useful_flows:
        _ok(f"App client auth flows configured: {', '.join(sorted(explicit_flows))}")
    else:
        _warn(f"App client auth flows may be incomplete: {', '.join(sorted(explicit_flows)) or '(none)'}")

    if args.admin_email:
        print("\n== Admin user check ==")
        try:
            user_resp = client.admin_get_user(UserPoolId=args.user_pool_id, Username=args.admin_email)
            enabled = user_resp.get("Enabled")
            status = user_resp.get("UserStatus")
            if enabled:
                _ok(f"Admin user exists and is enabled: {args.admin_email} ({status})")
            else:
                _fail(f"Admin user exists but is disabled: {args.admin_email} ({status})", issues)
        except Exception as exc:
            _fail(f"Could not find/read admin user {args.admin_email}: {exc}", issues)
    else:
        _warn("No --admin-email supplied; admin user existence was not checked.")

    print("\n== Environment values to carry forward ==")
    print(f"RSA_ADMIN_AUTH_MODE=cognito")
    print(f"RSA_COGNITO_REGION={args.region}")
    print(f"RSA_COGNITO_USER_POOL_ID={args.user_pool_id}")
    print(f"RSA_COGNITO_CLIENT_ID={args.client_id}")

    if issues:
        print("\nBatch 41 Cognito admin user pool check FAILED.")
        return 1

    print("\nBatch 41 Cognito admin user pool check PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
