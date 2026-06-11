from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Header, HTTPException, status

from app.auth.admin_auth import (
    get_admin_auth_config,
    get_optional_admin_user,
)


router = APIRouter(prefix="/admin/auth")


class MockLoginRequest(BaseModel):
    token: str


@router.get("/config")
def get_config():
    """Return public-safe admin auth configuration for the admin frontend."""

    return get_admin_auth_config()


@router.get("/status")
def get_status(authorization: str | None = Header(default=None)):
    """Return current admin auth status.

    In disabled mode, local preview is considered authenticated.
    In mock mode, a valid bearer token is required.
    Cognito mode will be completed in a later batch.
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
    """Local-only mock login helper for testing auth wiring.

    This does not validate Cognito. It only confirms that the frontend can store
    and send a bearer token during local testing.
    """

    config = get_admin_auth_config()
    if config["mode"] != "mock":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mock login is only available when RSA_ADMIN_AUTH_MODE=mock.",
        )

    # The actual token comparison is done by /status via Authorization header.
    # Returning the submitted token lets the local login page store it.
    return {
        "access_token": payload.token,
        "token_type": "Bearer",
        "mode": "mock",
        "message": "Mock token accepted by login page. /status will validate it against RSA_ADMIN_MOCK_TOKEN.",
    }
