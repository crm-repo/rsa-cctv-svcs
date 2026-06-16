from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.admin_auth import require_admin_group
from app.models.admin_user import (
    AdminUserActionResponse,
    AdminUserCreateRequest,
    AdminUserCreateResponse,
    AdminUserListResponse,
    AdminUserResetPasswordResponse,
    AdminUserUpdateRequest,
)
from app.services.admin_user_service import (
    create_admin_user,
    ensure_cognito_groups,
    list_admin_users,
    reset_admin_user_password,
    set_admin_user_enabled,
    update_admin_user,
)

router = APIRouter(prefix="/admin/users")


@router.get("/health")
def get_admin_users_health(_admin=Depends(require_admin_group)):
    return ensure_cognito_groups()


@router.get("", response_model=AdminUserListResponse)
def get_admin_users(_admin=Depends(require_admin_group)):
    return list_admin_users()


@router.post("", response_model=AdminUserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminUserCreateRequest, _admin=Depends(require_admin_group)):
    return create_admin_user(payload)


@router.put("/{username}", response_model=AdminUserActionResponse)
def update_user(username: str, payload: AdminUserUpdateRequest, _admin=Depends(require_admin_group)):
    return update_admin_user(username, payload)


@router.post("/{username}/reset-password", response_model=AdminUserResetPasswordResponse)
def reset_user_password(username: str, _admin=Depends(require_admin_group)):
    return reset_admin_user_password(username)


@router.post("/{username}/enable", response_model=AdminUserActionResponse)
def enable_user(username: str, _admin=Depends(require_admin_group)):
    return set_admin_user_enabled(username, True)


@router.post("/{username}/disable", response_model=AdminUserActionResponse)
def disable_user(username: str, _admin=Depends(require_admin_group)):
    return set_admin_user_enabled(username, False)
