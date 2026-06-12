"""Admin authentication for RSA CMS / Mini-CRM.

Batch 42 adds local Cognito login/token validation while keeping the public EC2
admin surface blocked by Nginx until a later enablement batch.

Environment variables:
    RSA_ADMIN_AUTH_MODE=disabled|mock|cognito
    RSA_ADMIN_MOCK_TOKEN=<local test token for mock mode>
    RSA_COGNITO_REGION=ap-southeast-1
    RSA_COGNITO_USER_POOL_ID=<Cognito user pool id>
    RSA_COGNITO_CLIENT_ID=<Cognito app client id>

Backwards compatibility:
    RSA_COGNITO_APP_CLIENT_ID is also accepted because Batch 23 used that name.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Header, HTTPException, status


VALID_AUTH_MODES = {"disabled", "mock", "cognito"}


def _get_auth_mode() -> str:
    mode = os.getenv("RSA_ADMIN_AUTH_MODE", "disabled").strip().lower()
    if mode not in VALID_AUTH_MODES:
        return "disabled"
    return mode


def _get_cognito_region() -> str:
    return (
        os.getenv("RSA_COGNITO_REGION")
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "ap-southeast-1"
    ).strip()


def _get_cognito_client_id() -> str:
    return (
        os.getenv("RSA_COGNITO_CLIENT_ID")
        or os.getenv("RSA_COGNITO_APP_CLIENT_ID")
        or ""
    ).strip()


def _get_cognito_user_pool_id() -> str:
    return os.getenv("RSA_COGNITO_USER_POOL_ID", "").strip()


def _get_cognito_client():
    return boto3.client("cognito-idp", region_name=_get_cognito_region())


def get_admin_auth_config() -> dict[str, Any]:
    """Return public-safe admin auth configuration.

    Never include access keys, secrets, passwords, refresh tokens, or private credentials here.
    """

    mode = _get_auth_mode()
    region = _get_cognito_region()
    user_pool_id = _get_cognito_user_pool_id()
    client_id = _get_cognito_client_id()

    return {
        "enabled": mode != "disabled",
        "mode": mode,
        "provider": "cognito" if mode == "cognito" else mode,
        "aws_region": region,
        "user_pool_id": user_pool_id,
        "client_id": client_id,
        # Keep the Batch 23 response name too so older frontend code still works.
        "app_client_id": client_id,
        "is_cognito_configured": bool(user_pool_id and client_id),
        "admin_routes_protected": mode != "disabled",
        "sms_mfa_required": False,
        "phone_verification_required": False,
        "supports_local_cognito_login": mode == "cognito" and bool(user_pool_id and client_id),
        "safety_note": (
            "disabled is the safe local default. Use mock for local auth wiring tests. "
            "Use cognito only after Cognito user pool/app client are configured. "
            "Public EC2 /admin remains blocked until the later protected admin exposure batch."
        ),
    }


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts
    if scheme.lower() != "bearer" or not token.strip():
        return None

    return token.strip()


def _decode_jwt_payload_unverified(token: str) -> dict[str, Any]:
    """Decode a JWT payload after Cognito has validated the access token.

    This helper is not used as proof by itself. It is only for extracting non-secret
    display fields and cross-checking the Cognito app client id after get_user succeeds.
    """

    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        padded = payload + "=" * (-len(payload) % 4)
        data = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(data.decode("utf-8"))
    except Exception:
        return {}


def _user_attributes_to_dict(attributes: list[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in attributes or []:
        name = item.get("Name")
        value = item.get("Value")
        if name and value is not None:
            result[name] = value
    return result


def _validate_cognito_access_token(token: str) -> dict[str, Any] | None:
    if not token:
        return None

    configured_client_id = _get_cognito_client_id()

    try:
        response = _get_cognito_client().get_user(AccessToken=token)
    except (ClientError, BotoCoreError):
        return None

    payload = _decode_jwt_payload_unverified(token)
    token_client_id = payload.get("client_id") or payload.get("aud")
    if configured_client_id and token_client_id and token_client_id != configured_client_id:
        return None

    attributes = _user_attributes_to_dict(response.get("UserAttributes", []))
    username = response.get("Username") or payload.get("username") or attributes.get("email") or "Cognito Admin"

    return {
        "user_id": username,
        "username": attributes.get("email") or username,
        "email": attributes.get("email", ""),
        "email_verified": attributes.get("email_verified") == "true",
        "role": "admin",
        "auth_mode": "cognito",
        "token_use": payload.get("token_use", "access"),
        "client_id": token_client_id or configured_client_id,
    }


def get_optional_admin_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    """Return admin user context when auth is valid, or None when anonymous.

    This is used by status endpoints and by future protected admin endpoints.
    """

    mode = _get_auth_mode()

    if mode == "disabled":
        return {
            "user_id": "local-admin-preview",
            "username": "Local Admin",
            "role": "local-preview",
            "auth_mode": mode,
        }

    token = _extract_bearer_token(authorization)

    if mode == "mock":
        expected = os.getenv("RSA_ADMIN_MOCK_TOKEN", "local-dev-admin-token")
        if token and token == expected:
            return {
                "user_id": "mock-admin",
                "username": "Mock Admin",
                "role": "admin",
                "auth_mode": mode,
            }
        return None

    if mode == "cognito":
        return _validate_cognito_access_token(token or "")

    return None


def require_admin_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """FastAPI dependency for protected admin endpoints."""

    user = get_optional_admin_user(authorization=authorization)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def cognito_initiate_password_auth(username: str, password: str) -> dict[str, Any]:
    """Start Cognito USER_PASSWORD_AUTH and return token/challenge payload."""

    config = get_admin_auth_config()
    if config["mode"] != "cognito":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cognito login is only available when RSA_ADMIN_AUTH_MODE=cognito.",
        )

    client_id = _get_cognito_client_id()
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RSA_COGNITO_CLIENT_ID is not configured.",
        )

    try:
        return _get_cognito_client().initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=client_id,
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "CognitoError")
        message = error.response.get("Error", {}).get("Message", str(error))
        if code in {"InvalidParameterException", "InvalidUserPoolConfigurationException"}:
            message = (
                f"{message} Ensure the Cognito app client enables USER_PASSWORD_AUTH "
                "for Batch 42 local login testing."
            )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{code}: {message}") from error
    except BotoCoreError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error


def cognito_complete_new_password(username: str, new_password: str, session: str) -> dict[str, Any]:
    """Complete Cognito NEW_PASSWORD_REQUIRED challenge."""

    client_id = _get_cognito_client_id()
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RSA_COGNITO_CLIENT_ID is not configured.",
        )

    try:
        return _get_cognito_client().respond_to_auth_challenge(
            ClientId=client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            Session=session,
            ChallengeResponses={
                "USERNAME": username,
                "NEW_PASSWORD": new_password,
            },
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "CognitoError")
        message = error.response.get("Error", {}).get("Message", str(error))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{code}: {message}") from error
    except BotoCoreError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
