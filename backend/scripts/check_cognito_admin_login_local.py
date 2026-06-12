"""Batch 42 local Cognito admin-login wiring check.

This script talks to a locally running RSA CMS backend. It does not create,
update, or delete AWS resources.

Read-only mode verifies:
- /api/admin/auth/config is in Cognito mode
- User pool/client values are present
- /api/admin/auth/status is anonymous without a token

Execute mode additionally prompts for Cognito admin password and tests:
- POST /api/admin/auth/cognito-login
- optional NEW_PASSWORD_REQUIRED challenge completion
- /api/admin/auth/status with the returned access token

Tokens and passwords are never printed.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class CheckResult:
    ok: bool = True

    def fail(self, message: str) -> None:
        self.ok = False
        print(f"FAIL: {message}")

    def check(self, condition: bool, ok_message: str, fail_message: str) -> None:
        if condition:
            print(f"OK: {ok_message}")
        else:
            self.fail(fail_message)


def _url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def _request_json(method: str, url: str, payload: dict[str, Any] | None = None, token: str | None = None) -> tuple[int, dict[str, Any] | str]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(body)
            except json.JSONDecodeError:
                return response.status, body
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] | str = json.loads(body)
        except json.JSONDecodeError:
            parsed = body
        return error.code, parsed


def _print_json_summary(data: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        if key in data:
            print(f"{key}: {data[key]}")


def _get_error_text(data: dict[str, Any] | str) -> str:
    if isinstance(data, dict):
        detail = data.get("detail")
        if isinstance(detail, str):
            return detail
        return json.dumps(data, ensure_ascii=False)
    return str(data)


def run() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 42 local Cognito admin login wiring.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Local backend base URL, without /api")
    parser.add_argument("--admin-email", required=True, help="Cognito admin email/user name")
    parser.add_argument("--execute", action="store_true", help="Prompt for password and run Cognito login flow")
    parser.add_argument("--confirm-login-test", action="store_true", help="Required with --execute")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 42 Cognito Admin Local Login Check")
    print("Mode:", "EXECUTE Cognito login test" if args.execute else "READ ONLY local config/status checks")
    print("Base URL:", args.base_url)
    print("Admin email:", args.admin_email)
    print("No AWS resources will be created, updated, or deleted.")

    result = CheckResult()

    print("\n== Local backend auth config ==")
    code, config_payload = _request_json("GET", _url(args.base_url, "/api/admin/auth/config"))
    result.check(code == 200, "GET /api/admin/auth/config -> HTTP 200", f"GET /api/admin/auth/config -> HTTP {code}: {_get_error_text(config_payload)}")
    if not isinstance(config_payload, dict):
        result.fail("Auth config response was not JSON.")
        return 1

    _print_json_summary(
        config_payload,
        [
            "enabled",
            "mode",
            "provider",
            "aws_region",
            "user_pool_id",
            "client_id",
            "app_client_id",
            "is_cognito_configured",
            "supports_local_cognito_login",
        ],
    )

    result.check(config_payload.get("mode") == "cognito", "Auth mode is cognito", "Auth mode is not cognito. Start backend with RSA_ADMIN_AUTH_MODE=cognito.")
    result.check(bool(config_payload.get("user_pool_id")), "User pool ID is configured", "User pool ID is missing.")
    client_id = config_payload.get("client_id") or config_payload.get("app_client_id")
    result.check(bool(client_id), "Client ID is configured", "Client ID is missing. Set RSA_COGNITO_CLIENT_ID.")
    result.check(bool(config_payload.get("is_cognito_configured")), "Cognito config is complete", "Cognito config is incomplete.")

    print("\n== Anonymous status check ==")
    code, status_payload = _request_json("GET", _url(args.base_url, "/api/admin/auth/status"))
    result.check(code == 200, "GET /api/admin/auth/status -> HTTP 200", f"GET /api/admin/auth/status -> HTTP {code}: {_get_error_text(status_payload)}")
    if isinstance(status_payload, dict):
        result.check(status_payload.get("authenticated") is False, "Anonymous request is not authenticated", "Anonymous request unexpectedly authenticated in cognito mode.")

    if not args.execute:
        print("\nSKIP: Cognito login not run in read-only mode.")
        print("Use --execute --confirm-login-test to test admin username/password login.")
        print("\n== Summary ==")
        print("Batch 42 local Cognito admin auth read-only check", "PASSED." if result.ok else "FAILED.")
        return 0 if result.ok else 1

    if not args.confirm_login_test:
        result.fail("--execute requires --confirm-login-test.")
        return 1

    print("\n== Cognito login check ==")
    password = getpass.getpass("Enter Cognito admin temporary/current password (input hidden): ")
    code, login_payload = _request_json(
        "POST",
        _url(args.base_url, "/api/admin/auth/cognito-login"),
        {"username": args.admin_email, "password": password},
    )

    if code != 200:
        result.fail(f"POST /api/admin/auth/cognito-login -> HTTP {code}: {_get_error_text(login_payload)}")
        print("Tip: ensure the Cognito app client enables USER_PASSWORD_AUTH for Batch 42 local login testing.")
        return 1

    if not isinstance(login_payload, dict):
        result.fail("Login response was not JSON.")
        return 1

    if login_payload.get("challenge_required") and login_payload.get("challenge_name") == "NEW_PASSWORD_REQUIRED":
        print("OK: Cognito returned NEW_PASSWORD_REQUIRED challenge for first login.")
        new_password = getpass.getpass("Enter new permanent password to set in Cognito (input hidden): ")
        code, complete_payload = _request_json(
            "POST",
            _url(args.base_url, "/api/admin/auth/cognito-complete-new-password"),
            {
                "username": args.admin_email,
                "new_password": new_password,
                "session": login_payload.get("session"),
            },
        )
        if code != 200:
            result.fail(f"POST /api/admin/auth/cognito-complete-new-password -> HTTP {code}: {_get_error_text(complete_payload)}")
            return 1
        login_payload = complete_payload if isinstance(complete_payload, dict) else {}
        print("OK: NEW_PASSWORD_REQUIRED challenge completed.")

    access_token = login_payload.get("access_token") if isinstance(login_payload, dict) else None
    result.check(bool(access_token), "Cognito login returned an access token", "Cognito login did not return an access token.")
    if not access_token:
        return 1

    print("\n== Authenticated status check ==")
    code, authed_status = _request_json("GET", _url(args.base_url, "/api/admin/auth/status"), token=access_token)
    result.check(code == 200, "GET /api/admin/auth/status with token -> HTTP 200", f"Authenticated status returned HTTP {code}: {_get_error_text(authed_status)}")
    if isinstance(authed_status, dict):
        result.check(authed_status.get("authenticated") is True, "Cognito access token authenticates admin status", "Cognito access token did not authenticate admin status.")
        user = authed_status.get("user") or {}
        if isinstance(user, dict):
            print("Authenticated user:", user.get("username") or user.get("email") or user.get("user_id"))
            print("Auth mode:", user.get("auth_mode"))

    print("\n== Summary ==")
    print("Batch 42 local Cognito admin login check", "PASSED." if result.ok else "FAILED.")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(run())
