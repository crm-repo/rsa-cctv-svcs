from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from fastapi import APIRouter, Header, HTTPException, status

from app.auth.admin_auth import (
    cognito_complete_new_password,
    cognito_initiate_password_auth,
    get_admin_auth_config,
    get_optional_admin_user,
)


router = APIRouter(prefix="/admin/auth")


class MockLoginRequest(BaseModel):
    token: str


class CognitoLoginRequest(BaseModel):
    username: str
    password: str


class CognitoCompleteNewPasswordRequest(BaseModel):
    username: str
    new_password: str
    session: str


def _sanitize_auth_result(response: dict[str, Any]) -> dict[str, Any]:
    if "ChallengeName" in response:
        return {
            "challenge_required": True,
            "challenge_name": response.get("ChallengeName"),
            "session": response.get("Session"),
            "message": "Cognito requires a new permanent password before login can complete.",
        }

    auth = response.get("AuthenticationResult") or {}
    return {
        "challenge_required": False,
        "access_token": auth.get("AccessToken"),
        "id_token": auth.get("IdToken"),
        "refresh_token": auth.get("RefreshToken"),
        "expires_in": auth.get("ExpiresIn"),
        "token_type": auth.get("TokenType", "Bearer"),
        "message": "Cognito login succeeded.",
    }


@router.get("/config")
def get_config():
    """Return public-safe admin auth configuration for the admin frontend."""

    return get_admin_auth_config()


@router.get("/status")
def get_status(authorization: str | None = Header(default=None)):
    """Return current admin auth status.

    In disabled mode, local preview is considered authenticated.
    In mock mode, a valid bearer token is required.
    In cognito mode, a valid Cognito access token is required.
    """

    config = get_admin_auth_config()
    user = get_optional_admin_user(authorization=authorization)

    return {
        "authenticated": user is not None,
        "user": user,
        "auth": config,
    }


@router.post("/mock-login")
def mock_login(payload: MockLoginRequest):
    """Local-only mock login helper for testing auth wiring."""

    config = get_admin_auth_config()
    if config["mode"] != "mock":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mock login is only available when RSA_ADMIN_AUTH_MODE=mock.",
        )

    return {
        "access_token": payload.token,
        "token_type": "Bearer",
        "mode": "mock",
        "message": "Mock token accepted by login page. /status will validate it against RSA_ADMIN_MOCK_TOKEN.",
    }


@router.post("/cognito-login")
def cognito_login(payload: CognitoLoginRequest):
    """Local Cognito username/password login endpoint for Batch 42 testing.

    Public EC2 /admin and admin APIs remain blocked by Nginx until a later batch.
    """

    response = cognito_initiate_password_auth(username=payload.username, password=payload.password)
    return _sanitize_auth_result(response)


@router.post("/cognito-complete-new-password")
def cognito_complete_password_challenge(payload: CognitoCompleteNewPasswordRequest):
    """Complete the first-login NEW_PASSWORD_REQUIRED challenge."""

    response = cognito_complete_new_password(
        username=payload.username,
        new_password=payload.new_password,
        session=payload.session,
    )
    return _sanitize_auth_result(response)
