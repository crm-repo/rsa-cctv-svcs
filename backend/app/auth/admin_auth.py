"""Admin authentication preparation for RSA CMS / Mini-CRM.

Batch 23 is intentionally safe:
- Default auth mode is "disabled" so local development/admin testing keeps working.
- "mock" mode can be used locally to test bearer-token wiring without Cognito.
- "cognito" mode is prepared at config level, but full JWT verification is handled in a later batch.

Environment variables:
    RSA_ADMIN_AUTH_MODE=disabled|mock|cognito
    RSA_ADMIN_MOCK_TOKEN=<local test token for mock mode>
    RSA_COGNITO_REGION=ap-southeast-1
    RSA_COGNITO_USER_POOL_ID=<future user pool id>
    RSA_COGNITO_APP_CLIENT_ID=<future app client id>
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import Header, HTTPException, status


VALID_AUTH_MODES = {"disabled", "mock", "cognito"}


def _get_auth_mode() -> str:
    mode = os.getenv("RSA_ADMIN_AUTH_MODE", "disabled").strip().lower()
    if mode not in VALID_AUTH_MODES:
        return "disabled"
    return mode


def get_admin_auth_config() -> dict[str, Any]:
    """Return public-safe admin auth configuration.

    Never include access keys, secrets, or private credentials here.
    """

    mode = _get_auth_mode()
    region = os.getenv("RSA_COGNITO_REGION") or os.getenv("AWS_REGION") or "ap-southeast-1"
    user_pool_id = os.getenv("RSA_COGNITO_USER_POOL_ID", "")
    app_client_id = os.getenv("RSA_COGNITO_APP_CLIENT_ID", "")

    return {
        "enabled": mode != "disabled",
        "mode": mode,
        "provider": "cognito" if mode == "cognito" else mode,
        "aws_region": region,
        "user_pool_id": user_pool_id,
        "app_client_id": app_client_id,
        "is_cognito_configured": bool(user_pool_id and app_client_id),
        "admin_routes_protected": mode != "disabled",
        "sms_mfa_required": False,
        "phone_verification_required": False,
        "safety_note": (
            "disabled is the safe local default. Use mock for local auth wiring tests. "
            "Use cognito only after Cognito user pool/app client are configured."
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


def get_optional_admin_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    """Return admin user context when auth is valid, or None when anonymous.

    This is used by status endpoints and local UI checks.
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

    # Cognito mode is intentionally not fully validated in Batch 23.
    # A later batch will add JWKS/JWT verification.
    if mode == "cognito":
        return None

    return None


def require_admin_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """FastAPI dependency for future protected admin endpoints."""

    mode = _get_auth_mode()

    if mode == "cognito":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Cognito JWT verification is not enabled yet. Use mock/disabled for local Batch 23 testing.",
        )

    user = get_optional_admin_user(authorization=authorization)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
