from __future__ import annotations

import os
import secrets
import string
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from app.models.admin_user import AdminUser, AdminUserCreateRequest, AdminUserUpdateRequest

BATCH59A_VERSION = "batch59a-cognito-groups-settings-users"
VALID_GROUPS = ("Admin", "Standard")


def _region() -> str:
    return (
        os.getenv("RSA_COGNITO_REGION")
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "ap-southeast-1"
    ).strip()


def _user_pool_id() -> str:
    return os.getenv("RSA_COGNITO_USER_POOL_ID", "").strip()


def _client():
    return boto3.client("cognito-idp", region_name=_region())


def _require_pool_id() -> str:
    user_pool_id = _user_pool_id()
    if not user_pool_id:
        raise HTTPException(status_code=500, detail="RSA_COGNITO_USER_POOL_ID is not configured.")
    return user_pool_id


def _attrs_to_dict(attrs: list[dict[str, str]] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for attr in attrs or []:
        name = attr.get("Name")
        value = attr.get("Value")
        if name:
            result[name] = value or ""
    return result


def _dt(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value or "")


def _full_name(first_name: str, last_name: str, fallback: str = "") -> str:
    full = f"{first_name or ''} {last_name or ''}".strip()
    return full or fallback


def _normalize_role(role: str | None) -> str:
    normalized = str(role or "Standard").strip()
    if normalized not in VALID_GROUPS:
        raise HTTPException(status_code=400, detail="Role must be Admin or Standard.")
    return normalized


def _generate_temp_password(length: int = 18) -> str:
    # Cognito policy-safe mix: upper, lower, digit, symbol. No ambiguous quotes/backslashes.
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    required = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+"),
    ]
    remaining = [secrets.choice(alphabet) for _ in range(max(length - len(required), 8))]
    chars = required + remaining
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def ensure_cognito_groups() -> dict[str, Any]:
    user_pool_id = _require_pool_id()
    client = _client()
    existing: set[str] = set()
    try:
        paginator = client.get_paginator("list_groups")
        for page in paginator.paginate(UserPoolId=user_pool_id):
            for group in page.get("Groups", []):
                name = group.get("GroupName")
                if name:
                    existing.add(name)
        created: list[str] = []
        for group_name in VALID_GROUPS:
            if group_name in existing:
                continue
            client.create_group(
                UserPoolId=user_pool_id,
                GroupName=group_name,
                Description=f"RSA CMS {group_name} role group",
            )
            created.append(group_name)
        return {"version": BATCH59A_VERSION, "groups": list(VALID_GROUPS), "created": created}
    except ClientError as error:
        raise _client_error(error, "Unable to verify Cognito groups") from error
    except BotoCoreError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


def _client_error(error: ClientError, prefix: str) -> HTTPException:
    err = error.response.get("Error", {})
    code = err.get("Code", "CognitoError")
    message = err.get("Message", str(error))
    return HTTPException(status_code=400, detail=f"{prefix}: {code}: {message}")


def _groups_for_user(username: str) -> list[str]:
    user_pool_id = _require_pool_id()
    client = _client()
    try:
        response = client.admin_list_groups_for_user(UserPoolId=user_pool_id, Username=username)
        return sorted(g.get("GroupName", "") for g in response.get("Groups", []) if g.get("GroupName"))
    except ClientError:
        return []


def _role_from_groups(groups: list[str]) -> str:
    if "Admin" in groups:
        return "Admin"
    return "Standard"


def _to_admin_user(raw: dict[str, Any], groups: list[str] | None = None) -> AdminUser:
    attrs = _attrs_to_dict(raw.get("Attributes") or raw.get("UserAttributes"))
    username = raw.get("Username") or attrs.get("email") or ""
    resolved_groups = groups if groups is not None else _groups_for_user(username)
    email = attrs.get("email", "")
    first_name = attrs.get("given_name", "")
    last_name = attrs.get("family_name", "")
    full_name = attrs.get("name") or _full_name(first_name, last_name, email or username)
    status_value = raw.get("UserStatus", "")
    return AdminUser(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        role=_role_from_groups(resolved_groups),
        groups=resolved_groups,
        status=status_value,
        enabled=bool(raw.get("Enabled", True)),
        password_status="Temporary password required" if status_value == "FORCE_CHANGE_PASSWORD" else "Active",
        created_at=_dt(raw.get("UserCreateDate")),
        updated_at=_dt(raw.get("UserLastModifiedDate")),
    )


def list_admin_users() -> dict[str, Any]:
    ensure_cognito_groups()
    user_pool_id = _require_pool_id()
    client = _client()
    items: list[AdminUser] = []
    try:
        paginator = client.get_paginator("list_users")
        for page in paginator.paginate(UserPoolId=user_pool_id):
            for user in page.get("Users", []):
                items.append(_to_admin_user(user))
    except ClientError as error:
        raise _client_error(error, "Unable to list Cognito users") from error
    except BotoCoreError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    items.sort(key=lambda item: (item.role != "Admin", item.full_name.lower(), item.email.lower()))
    return {"items": items, "count": len(items), "roles": list(VALID_GROUPS)}


def _set_user_group(username: str, role: str) -> None:
    user_pool_id = _require_pool_id()
    client = _client()
    role = _normalize_role(role)
    for group_name in VALID_GROUPS:
        try:
            if group_name == role:
                client.admin_add_user_to_group(UserPoolId=user_pool_id, Username=username, GroupName=group_name)
            else:
                client.admin_remove_user_from_group(UserPoolId=user_pool_id, Username=username, GroupName=group_name)
        except client.exceptions.UserNotFoundException as error:
            raise HTTPException(status_code=404, detail="Cognito user not found.") from error
        except client.exceptions.ResourceNotFoundException:
            # If a group was manually removed, recreate groups and retry target add only.
            ensure_cognito_groups()
            if group_name == role:
                client.admin_add_user_to_group(UserPoolId=user_pool_id, Username=username, GroupName=group_name)
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code", "")
            # Removing from a group the user is not in may throw; keep group sync idempotent.
            if group_name != role and code in {"InvalidParameterException", "ResourceNotFoundException"}:
                continue
            raise _client_error(error, "Unable to update Cognito group assignment") from error


def _get_user(username: str) -> AdminUser:
    user_pool_id = _require_pool_id()
    client = _client()
    try:
        raw = client.admin_get_user(UserPoolId=user_pool_id, Username=username)
        return _to_admin_user(raw)
    except client.exceptions.UserNotFoundException as error:
        raise HTTPException(status_code=404, detail="Cognito user not found.") from error
    except ClientError as error:
        raise _client_error(error, "Unable to read Cognito user") from error


def create_admin_user(payload: AdminUserCreateRequest) -> dict[str, Any]:
    ensure_cognito_groups()
    user_pool_id = _require_pool_id()
    client = _client()
    role = _normalize_role(payload.role)
    email = str(payload.email).strip().lower()
    first_name = payload.first_name.strip()
    last_name = payload.last_name.strip()
    full_name = _full_name(first_name, last_name, email)
    temp_password = _generate_temp_password()

    try:
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            TemporaryPassword=temp_password,
            MessageAction="SUPPRESS",
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name},
                {"Name": "name", "Value": full_name},
            ],
        )
        _set_user_group(email, role)
        user = _get_user(email)
        return {
            "user": user,
            "temporary_password": temp_password,
            "message": "User created. Temporary password is shown once only.",
        }
    except ClientError as error:
        raise _client_error(error, "Unable to create Cognito user") from error
    except BotoCoreError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


def update_admin_user(username: str, payload: AdminUserUpdateRequest) -> dict[str, Any]:
    ensure_cognito_groups()
    user_pool_id = _require_pool_id()
    client = _client()
    role = _normalize_role(payload.role)
    first_name = payload.first_name.strip()
    last_name = payload.last_name.strip()
    current = _get_user(username)
    full_name = _full_name(first_name, last_name, current.email or username)
    try:
        client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "given_name", "Value": first_name},
                {"Name": "family_name", "Value": last_name},
                {"Name": "name", "Value": full_name},
            ],
        )
        _set_user_group(username, role)
        if payload.enabled is True:
            client.admin_enable_user(UserPoolId=user_pool_id, Username=username)
        elif payload.enabled is False:
            client.admin_disable_user(UserPoolId=user_pool_id, Username=username)
        return {"user": _get_user(username), "message": "User updated."}
    except ClientError as error:
        raise _client_error(error, "Unable to update Cognito user") from error


def reset_admin_user_password(username: str) -> dict[str, Any]:
    user_pool_id = _require_pool_id()
    client = _client()
    temp_password = _generate_temp_password()
    try:
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password=temp_password,
            Permanent=False,
        )
        return {
            "username": username,
            "temporary_password": temp_password,
            "message": "Temporary password reset. It is shown once only.",
        }
    except client.exceptions.UserNotFoundException as error:
        raise HTTPException(status_code=404, detail="Cognito user not found.") from error
    except ClientError as error:
        raise _client_error(error, "Unable to reset Cognito user password") from error


def set_admin_user_enabled(username: str, enabled: bool) -> dict[str, Any]:
    user_pool_id = _require_pool_id()
    client = _client()
    try:
        if enabled:
            client.admin_enable_user(UserPoolId=user_pool_id, Username=username)
            message = "User enabled."
        else:
            client.admin_disable_user(UserPoolId=user_pool_id, Username=username)
            message = "User disabled."
        return {"user": _get_user(username), "message": message}
    except client.exceptions.UserNotFoundException as error:
        raise HTTPException(status_code=404, detail="Cognito user not found.") from error
    except ClientError as error:
        raise _client_error(error, "Unable to update Cognito user status") from error
