from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_APP = ROOT / "backend" / "app"
FRONTEND_ADMIN = ROOT / "frontend" / "admin"
ADMIN_JS = FRONTEND_ADMIN / "assets" / "js"
ADMIN_CSS = FRONTEND_ADMIN / "assets" / "css" / "admin.css"
DOCS_README = ROOT / "docs" / "phase8"

MARKER = "batch59a-cognito-groups-settings-users"
ROLE_GUARD_SCRIPT = '<script src="./assets/js/admin-role-guard-59a.js"></script>'
USERS_SCRIPT = '<script src="./assets/js/admin-users-59a.js"></script>'


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def replace_or_append(path: Path, old: str, new: str, label: str) -> None:
    text = read(path)
    if new in text:
        print(f"[skip] {label} already applied in {rel(path)}")
        return
    if old not in text:
        raise SystemExit(f"[fail] Expected block not found while patching {label}: {rel(path)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
    print(f"[ok] Patched {label} in {rel(path)}")


ADMIN_USER_MODELS = r'''from __future__ import annotations

from pydantic import BaseModel, Field


class AdminUser(BaseModel):
    username: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    role: str = "Standard"
    groups: list[str] = Field(default_factory=list)
    status: str = ""
    enabled: bool = True
    password_status: str = ""
    created_at: str = ""
    updated_at: str = ""


class AdminUserListResponse(BaseModel):
    items: list[AdminUser]
    count: int
    roles: list[str] = Field(default_factory=lambda: ["Admin", "Standard"])


class AdminUserCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    email: str = Field(..., min_length=3, max_length=160)
    role: str = Field(default="Standard", pattern="^(Admin|Standard)$")


class AdminUserUpdateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    role: str = Field(default="Standard", pattern="^(Admin|Standard)$")
    enabled: bool | None = None


class AdminUserCreateResponse(BaseModel):
    user: AdminUser
    temporary_password: str
    message: str


class AdminUserResetPasswordResponse(BaseModel):
    username: str
    temporary_password: str
    message: str


class AdminUserActionResponse(BaseModel):
    user: AdminUser
    message: str
'''


ADMIN_USER_SERVICE = r'''from __future__ import annotations

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
'''


ADMIN_USERS_ROUTE = r'''from __future__ import annotations

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
'''


ROLE_GUARD_JS = r'''(function () {
  'use strict';

  const VERSION = 'batch59a-cognito-groups-settings-users';
  window.RSA_BATCH59A_ROLE_GUARD_VERSION = VERSION;

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function getUserFromStatus(status) {
    return status && status.user ? status.user : {};
  }

  function getGroups(user) {
    return Array.isArray(user.groups) ? user.groups : [];
  }

  function isAdminUser(user) {
    const groups = getGroups(user);
    const role = String(user.role || '').toLowerCase();
    const mode = String(user.auth_mode || '').toLowerCase();
    return groups.includes('Admin') || role === 'admin' || mode === 'disabled' || mode === 'mock' || role === 'local-preview';
  }

  function hideSettingsForStandard() {
    qsa('a[href="./settings.html"], a[href="settings.html"], [data-admin-requires-admin]').forEach((el) => {
      el.hidden = true;
      el.setAttribute('aria-hidden', 'true');
    });
  }

  function showRestrictedSettingsMessage(user) {
    const app = qs('[data-admin-app]');
    if (!app || app.getAttribute('data-admin-page') !== 'settings') return;
    const main = qs('.admin-main');
    if (!main) return;
    main.innerHTML = `
      <header class="admin-topbar">
        <div><p class="eyebrow">System</p><h1>Settings</h1></div>
      </header>
      <section class="status-banner is-warning">
        <strong>Settings is restricted.</strong>
        <span>Your account is signed in as ${escapeHtml(user.role || 'Standard')}. Only Admin users can manage Settings and Users.</span>
      </section>
      <section class="admin-page-heading">
        <div class="page-icon"><i class="fa-solid fa-lock"></i></div>
        <div><p class="eyebrow">Access restricted</p><h2>Admin access required</h2><p>Please use an Admin account for Settings > Users.</p></div>
      </section>`;
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  async function applyRoleGuard() {
    if (!window.RSAAdminAuth || typeof window.RSAAdminAuth.checkStatus !== 'function') return;
    let status = window.RSAAdminAuth.status;
    if (!status || !status.authenticated) {
      status = await window.RSAAdminAuth.checkStatus().catch(() => null);
    }
    const user = getUserFromStatus(status);
    const role = isAdminUser(user) ? 'Admin' : 'Standard';
    document.body.setAttribute('data-admin-role', role);
    window.RSAAdminRole = { role, user, isAdmin: role === 'Admin', version: VERSION };
    if (role !== 'Admin') {
      hideSettingsForStandard();
      showRestrictedSettingsMessage(user);
    }
    document.dispatchEvent(new CustomEvent('rsa-admin-role-ready', { detail: window.RSAAdminRole }));
  }

  document.addEventListener('DOMContentLoaded', () => {
    window.setTimeout(() => {
      applyRoleGuard().catch((error) => console.warn('Batch 59A role guard failed:', error));
    }, 250);
  });
}());
'''


ADMIN_USERS_JS = r'''(function () {
  'use strict';

  const VERSION = 'batch59a-cognito-groups-settings-users';
  window.RSA_BATCH59A_ADMIN_USERS_VERSION = VERSION;

  const state = {
    users: [],
    editingUsername: '',
  };

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function setText(selector, value, root) {
    const el = qs(selector, root);
    if (el) el.textContent = value;
  }

  function setStatus(kind, title, detail) {
    const card = qs('[data-users-status]');
    if (!card) return;
    card.className = `users-inline-status ${kind || ''}`.trim();
    card.innerHTML = `<strong>${escapeHtml(title)}</strong>${detail ? `<span>${escapeHtml(detail)}</span>` : ''}`;
  }

  function api() {
    if (!window.RSAAdminApi) throw new Error('Admin API client is not loaded.');
    return window.RSAAdminApi;
  }

  async function request(path, options) {
    return api().request(path, options || {});
  }

  function getItems(payload) {
    return api().getItems(payload);
  }

  function rolePill(role) {
    const isAdmin = role === 'Admin';
    return `<span class="users-role-pill ${isAdmin ? 'is-admin' : 'is-standard'}">${escapeHtml(role || 'Standard')}</span>`;
  }

  function statusPill(user) {
    const enabled = user.enabled !== false;
    const cls = enabled ? 'is-enabled' : 'is-disabled';
    const text = enabled ? 'Enabled' : 'Disabled';
    return `<span class="users-status-pill ${cls}">${text}</span>`;
  }

  function renderUsers() {
    const tbody = qs('[data-users-table-body]');
    if (!tbody) return;
    if (!state.users.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="users-empty">No Cognito users found.</td></tr>';
      return;
    }
    tbody.innerHTML = state.users.map((user) => {
      const username = escapeHtml(user.username || user.email || '');
      const disabledAction = user.enabled === false ? 'enable' : 'disable';
      const disabledLabel = user.enabled === false ? 'Enable' : 'Disable';
      return `<tr data-users-row data-username="${username}">
        <td><strong>${escapeHtml(user.full_name || user.email || user.username)}</strong><small>${escapeHtml(user.username || '')}</small></td>
        <td>${escapeHtml(user.email || '')}</td>
        <td>${rolePill(user.role)}</td>
        <td>${statusPill(user)}</td>
        <td>${escapeHtml(user.password_status || user.status || '')}</td>
        <td>${escapeHtml((user.created_at || '').slice(0, 10))}</td>
        <td>${escapeHtml((user.updated_at || '').slice(0, 10))}</td>
        <td class="users-actions">
          <button type="button" data-user-action="edit" data-username="${username}">Edit</button>
          <button type="button" data-user-action="reset" data-username="${username}">Reset password</button>
          <button type="button" data-user-action="${disabledAction}" data-username="${username}">${disabledLabel}</button>
        </td>
      </tr>`;
    }).join('');
  }

  async function loadUsers() {
    setStatus('', 'Loading users…', 'Reading Cognito users through protected backend routes.');
    try {
      const payload = await request('/admin/users');
      state.users = getItems(payload);
      renderUsers();
      setText('[data-users-count]', String(state.users.length));
      setStatus('is-success', 'Users loaded.', `${state.users.length} Cognito user record(s) loaded.`);
    } catch (error) {
      console.error(error);
      state.users = [];
      renderUsers();
      setStatus('is-warning', 'Unable to load users.', error.message || 'Check Cognito groups, backend auth, and IAM permissions.');
    }
  }

  function showTempPassword(result) {
    const panel = qs('[data-temp-password-panel]');
    if (!panel) return;
    const password = result.temporary_password || '';
    panel.hidden = false;
    panel.innerHTML = `<strong>Temporary password shown once</strong>
      <p>Copy this password now. It is not stored and cannot be viewed again later.</p>
      <code>${escapeHtml(password)}</code>
      <button type="button" data-copy-temp-password>Copy temporary password</button>`;
  }

  async function createUser(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = {
      first_name: String(form.elements.first_name.value || '').trim(),
      last_name: String(form.elements.last_name.value || '').trim(),
      email: String(form.elements.email.value || '').trim(),
      role: String(form.elements.role.value || 'Standard'),
    };
    setStatus('', 'Creating user…', 'Cognito invitation email is suppressed. Temporary password will show once.');
    try {
      const result = await request('/admin/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      form.reset();
      form.elements.role.value = 'Standard';
      showTempPassword(result);
      await loadUsers();
      setStatus('is-success', 'User created.', 'Copy the temporary password and send it securely to the user.');
    } catch (error) {
      setStatus('is-warning', 'Unable to create user.', error.message || 'Check form values and Cognito permissions.');
    }
  }

  function openEdit(username) {
    const user = state.users.find((item) => item.username === username || item.email === username);
    const form = qs('[data-user-edit-form]');
    const modal = qs('[data-user-edit-modal]');
    if (!user || !form || !modal) return;
    state.editingUsername = user.username;
    form.elements.first_name.value = user.first_name || '';
    form.elements.last_name.value = user.last_name || '';
    form.elements.role.value = user.role || 'Standard';
    form.elements.enabled.checked = user.enabled !== false;
    setText('[data-edit-user-email]', user.email || user.username, modal);
    modal.hidden = false;
  }

  function closeEdit() {
    const modal = qs('[data-user-edit-modal]');
    if (modal) modal.hidden = true;
    state.editingUsername = '';
  }

  async function saveEdit(event) {
    event.preventDefault();
    if (!state.editingUsername) return;
    const form = event.currentTarget;
    const payload = {
      first_name: String(form.elements.first_name.value || '').trim(),
      last_name: String(form.elements.last_name.value || '').trim(),
      role: String(form.elements.role.value || 'Standard'),
      enabled: !!form.elements.enabled.checked,
    };
    try {
      await request(`/admin/users/${encodeURIComponent(state.editingUsername)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      closeEdit();
      await loadUsers();
      setStatus('is-success', 'User updated.', 'Cognito user attributes and group role were updated.');
    } catch (error) {
      setStatus('is-warning', 'Unable to update user.', error.message || 'Check Cognito permissions.');
    }
  }

  async function resetPassword(username) {
    if (!window.confirm('Generate a new temporary password for this user? The password will be shown once only.')) return;
    try {
      const result = await request(`/admin/users/${encodeURIComponent(username)}/reset-password`, { method: 'POST' });
      showTempPassword(result);
      await loadUsers();
      setStatus('is-success', 'Temporary password reset.', 'Copy the temporary password now.');
    } catch (error) {
      setStatus('is-warning', 'Unable to reset password.', error.message || 'Check Cognito permissions.');
    }
  }

  async function setEnabled(username, enabled) {
    try {
      await request(`/admin/users/${encodeURIComponent(username)}/${enabled ? 'enable' : 'disable'}`, { method: 'POST' });
      await loadUsers();
      setStatus('is-success', enabled ? 'User enabled.' : 'User disabled.', 'Cognito user status updated.');
    } catch (error) {
      setStatus('is-warning', 'Unable to update status.', error.message || 'Check Cognito permissions.');
    }
  }

  function bindEvents() {
    const createForm = qs('[data-user-create-form]');
    if (createForm) createForm.addEventListener('submit', createUser);
    const editForm = qs('[data-user-edit-form]');
    if (editForm) editForm.addEventListener('submit', saveEdit);
    document.addEventListener('click', (event) => {
      if (event.target.closest('[data-users-refresh]')) loadUsers();
      if (event.target.closest('[data-user-edit-close]')) closeEdit();
      if (event.target.closest('[data-copy-temp-password]')) {
        const code = qs('[data-temp-password-panel] code');
        if (code && navigator.clipboard) navigator.clipboard.writeText(code.textContent || '');
      }
      const actionButton = event.target.closest('[data-user-action]');
      if (!actionButton) return;
      const username = actionButton.getAttribute('data-username') || '';
      const action = actionButton.getAttribute('data-user-action');
      if (action === 'edit') openEdit(username);
      if (action === 'reset') resetPassword(username);
      if (action === 'enable') setEnabled(username, true);
      if (action === 'disable') setEnabled(username, false);
    });
  }

  function init() {
    const section = qs('[data-settings-users]');
    if (!section) return;
    bindEvents();
    loadUsers();
  }

  document.addEventListener('rsa-admin-role-ready', (event) => {
    if (event.detail && event.detail.isAdmin) init();
  });

  document.addEventListener('DOMContentLoaded', () => {
    window.setTimeout(() => {
      if (!window.RSAAdminRole || window.RSAAdminRole.isAdmin) init();
    }, 450);
  });
}());
'''


USERS_SECTION_HTML = r'''        <article class="settings-card settings-card-wide" data-settings-users data-admin-requires-admin>
          <div class="settings-card-heading">
            <span><i class="fa-solid fa-users-gear"></i></span>
            <div><p class="eyebrow">Cognito Users</p><h2>Settings &gt; Users</h2></div>
          </div>
          <p class="settings-note">Manage Cognito admin users through protected FastAPI routes. Roles come from Cognito Groups only: Admin and Standard.</p>
          <div class="users-inline-status" data-users-status><strong>Users ready.</strong><span>Use Refresh to load Cognito users.</span></div>
          <div class="users-toolbar">
            <strong><span data-users-count>0</span> users</strong>
            <button class="admin-button secondary" type="button" data-users-refresh>Refresh Users</button>
          </div>
          <form class="users-create-form" data-user-create-form>
            <label>First Name <input name="first_name" type="text" required maxlength="80" /></label>
            <label>Last Name <input name="last_name" type="text" required maxlength="80" /></label>
            <label>Email <input name="email" type="email" required autocomplete="off" /></label>
            <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
            <button class="admin-button" type="submit">Add User</button>
          </form>
          <div class="users-temp-password" data-temp-password-panel hidden></div>
          <div class="users-table-wrap">
            <table class="users-table">
              <thead><tr><th>Full Name</th><th>Email</th><th>Role</th><th>Status</th><th>Password Status</th><th>Created</th><th>Last Updated</th><th>Actions</th></tr></thead>
              <tbody data-users-table-body><tr><td colspan="8" class="users-empty">Users not loaded yet.</td></tr></tbody>
            </table>
          </div>
        </article>

        <div class="user-edit-modal" data-user-edit-modal hidden data-admin-requires-admin>
          <div class="user-edit-card">
            <button class="modal-close" type="button" data-user-edit-close aria-label="Close">&times;</button>
            <p class="eyebrow">Edit user</p>
            <h2 data-edit-user-email>User</h2>
            <form data-user-edit-form>
              <label>First Name <input name="first_name" type="text" required maxlength="80" /></label>
              <label>Last Name <input name="last_name" type="text" required maxlength="80" /></label>
              <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
              <label class="users-checkbox"><input name="enabled" type="checkbox" /> Enabled</label>
              <div class="settings-actions"><button class="admin-button" type="submit">Save User</button><button class="admin-button secondary" type="button" data-user-edit-close>Cancel</button></div>
            </form>
          </div>
        </div>'''


BATCH59A_CSS = r'''

/* batch59a-cognito-groups-settings-users */
.settings-card-wide { grid-column: 1 / -1; }
.users-inline-status { display: grid; gap: 4px; padding: 12px 14px; border: 1px solid rgba(148, 163, 184, 0.25); border-radius: 12px; background: #f8fafc; color: #334155; margin: 14px 0; }
.users-inline-status strong { color: #0f172a; }
.users-inline-status span { font-size: 0.88rem; }
.users-inline-status.is-success { background: #f0fdf4; border-color: rgba(21, 128, 61, 0.24); color: #166534; }
.users-inline-status.is-warning { background: #fff7ed; border-color: rgba(194, 65, 12, 0.24); color: #9a3412; }
.users-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 14px 0; }
.users-create-form { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)) auto; gap: 12px; align-items: end; padding: 14px; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 14px; background: #ffffff; }
.users-create-form label,
.user-edit-card label { display: grid; gap: 6px; font-size: 0.82rem; font-weight: 800; color: #334155; }
.users-create-form input,
.users-create-form select,
.user-edit-card input,
.user-edit-card select { width: 100%; border: 1px solid #d1d5db; border-radius: 10px; padding: 10px 11px; color: #111827; background: #fff; }
.users-temp-password { margin: 14px 0; padding: 14px; border-radius: 14px; border: 1px solid rgba(185, 28, 28, 0.25); background: #fff7f7; display: grid; gap: 8px; }
.users-temp-password code { display: block; padding: 12px; border-radius: 10px; background: #111827; color: #f8fafc; font-size: 1rem; overflow-wrap: anywhere; }
.users-table-wrap { overflow-x: auto; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 14px; }
.users-table { width: 100%; min-width: 1040px; border-collapse: collapse; background: #fff; }
.users-table th,
.users-table td { text-align: left; vertical-align: top; padding: 12px 14px; border-bottom: 1px solid rgba(226, 232, 240, 0.9); font-size: 0.86rem; }
.users-table th { color: #475569; background: #f8fafc; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; }
.users-table td strong { display: block; color: #111827; }
.users-table td small { display: block; color: #64748b; margin-top: 3px; overflow-wrap: anywhere; }
.users-role-pill,
.users-status-pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 5px 9px; font-size: 0.76rem; font-weight: 900; }
.users-role-pill.is-admin { color: #991b1b; background: #fee2e2; }
.users-role-pill.is-standard { color: #334155; background: #e2e8f0; }
.users-status-pill.is-enabled { color: #166534; background: #dcfce7; }
.users-status-pill.is-disabled { color: #9a3412; background: #ffedd5; }
.users-actions { display: flex; flex-wrap: wrap; gap: 7px; min-width: 230px; }
.users-actions button,
.users-temp-password button { border: 0; border-radius: 9px; padding: 8px 10px; background: #f1f5f9; color: #0f172a; font-size: 0.78rem; font-weight: 800; cursor: pointer; }
.users-actions button:hover,
.users-temp-password button:hover { background: #fee2e2; color: #991b1b; }
.users-empty { text-align: center !important; color: #64748b; padding: 24px !important; }
.user-edit-modal { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 22px; background: rgba(15, 23, 42, 0.55); }
.user-edit-modal[hidden] { display: none !important; }
.user-edit-card { position: relative; width: min(520px, 100%); display: grid; gap: 14px; background: #fff; border-radius: 18px; padding: 24px; box-shadow: 0 24px 70px rgba(15, 23, 42, 0.24); }
.user-edit-card .modal-close { position: absolute; top: 14px; right: 16px; border: 0; background: #f1f5f9; width: 34px; height: 34px; border-radius: 999px; cursor: pointer; font-size: 1.4rem; }
.users-checkbox { display: flex !important; grid-template-columns: auto 1fr; align-items: center; gap: 9px !important; }
.users-checkbox input { width: auto !important; }
@media (max-width: 980px) { .users-create-form { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .users-create-form { grid-template-columns: 1fr; } .users-toolbar { align-items: stretch; flex-direction: column; } }
'''


def patch_admin_auth() -> None:
    path = BACKEND_APP / "auth" / "admin_auth.py"
    if not path.exists():
        raise SystemExit(f"[fail] Missing {rel(path)}")
    text = read(path)
    original = text

    if "# batch59a-cognito-groups-settings-users" in text:
        print(f"[skip] {rel(path)} already has Batch 59A auth patch")
        return

    # Add groups/role from Cognito access token payload.
    old_return = '''    return {
        "user_id": username,
        "username": attributes.get("email") or username,
        "email": attributes.get("email", ""),
        "email_verified": attributes.get("email_verified") == "true",
        "role": "admin",
        "auth_mode": "cognito",
        "token_use": payload.get("token_use", "access"),
        "client_id": token_client_id or configured_client_id,
    }
'''
    new_return = '''    groups = payload.get("cognito:groups") or []
    if isinstance(groups, str):
        groups = [groups]
    groups = [str(group) for group in groups if group]
    role = "Admin" if "Admin" in groups else "Standard"

    return {
        "user_id": username,
        "username": attributes.get("email") or username,
        "email": attributes.get("email", ""),
        "email_verified": attributes.get("email_verified") == "true",
        "first_name": attributes.get("given_name", ""),
        "last_name": attributes.get("family_name", ""),
        "full_name": attributes.get("name", ""),
        "role": role,
        "groups": groups,
        "auth_mode": "cognito",
        "token_use": payload.get("token_use", "access"),
        "client_id": token_client_id or configured_client_id,
    }
'''
    if old_return in text:
        text = text.replace(old_return, new_return, 1)
    else:
        print(f"[warn] Cognito return block not found in {rel(path)}; dependency helpers will still be appended.")

    text = text.replace('''            "role": "local-preview",
            "auth_mode": mode,
''', '''            "role": "Admin",
            "groups": ["Admin"],
            "auth_mode": mode,
''')
    text = text.replace('''                "role": "admin",
                "auth_mode": mode,
''', '''                "role": "Admin",
                "groups": ["Admin"],
                "auth_mode": mode,
''')

    helpers = r'''

# batch59a-cognito-groups-settings-users

def is_admin_group_user(user: dict[str, Any] | None) -> bool:
    if not user:
        return False
    groups = user.get("groups") or []
    if isinstance(groups, str):
        groups = [groups]
    role = str(user.get("role") or "").lower()
    auth_mode = str(user.get("auth_mode") or "").lower()
    return "Admin" in groups or role == "admin" or auth_mode in {"disabled", "mock"}


def require_admin_group(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """FastAPI dependency for Admin-group-only endpoints."""

    user = require_admin_user(authorization=authorization)
    if not is_admin_group_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )
    return user
'''
    if "def require_admin_group" not in text:
        text = text.rstrip() + helpers + "\n"

    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Patched {rel(path)}")


def patch_main_router() -> None:
    path = BACKEND_APP / "main.py"
    if not path.exists():
        raise SystemExit(f"[fail] Missing {rel(path)}")
    text = read(path)
    original = text
    if "admin_users" not in text:
        # Patch grouped import list.
        marker = "    admin_media,\n"
        if marker in text:
            text = text.replace(marker, marker + "    admin_users,\n", 1)
        else:
            raise SystemExit(f"[fail] Could not find admin_media import marker in {rel(path)}")
    include_line = 'app.include_router(admin_users.router, prefix=settings.API_PREFIX, tags=["Admin Users"])'
    if include_line not in text:
        after = 'app.include_router(admin_media.router, prefix=settings.API_PREFIX, tags=["Admin Media"])\n'
        if after in text:
            text = text.replace(after, after + include_line + "\n", 1)
        else:
            raise SystemExit(f"[fail] Could not find admin_media router marker in {rel(path)}")
    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Patched {rel(path)}")
    else:
        print(f"[skip] {rel(path)} already includes Batch 59A router")


def patch_admin_api() -> None:
    path = FRONTEND_ADMIN / "assets" / "js" / "admin-api.js"
    if not path.exists():
        default_admin_api = """(function () {
  'use strict';

  const DEFAULT_API_BASE = 'http://127.0.0.1:8000/api';

  function normalizeBaseUrl(value) {
    return String(value || DEFAULT_API_BASE).replace(/\\/$/, '');
  }

  function getApiBaseUrl() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('apiBase');
    if (fromQuery) return normalizeBaseUrl(fromQuery);
    if (window.RSA_ADMIN_API_BASE_URL) return normalizeBaseUrl(window.RSA_ADMIN_API_BASE_URL);
    const host = window.location.hostname;
    if (host === '127.0.0.1' || host === 'localhost') return DEFAULT_API_BASE;
    return normalizeBaseUrl(`${window.location.origin}/api`);
  }

  function getAuthHeaders() {
    if (window.RSAAdminAuth && typeof window.RSAAdminAuth.getAuthHeader === 'function') {
      return window.RSAAdminAuth.getAuthHeader();
    }
    const token = window.localStorage.getItem('rsa_admin_access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function request(path, options = {}) {
    const base = getApiBaseUrl();
    const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
    const response = await fetch(url, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {})
      },
      ...options
    });
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`${response.status} ${response.statusText}${text ? ` - ${text}` : ''}`);
    }
    return response.json();
  }

  function getItems(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== 'object') return [];
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload.results)) return payload.results;
    return [];
  }

  function getCount(payload) {
    if (Array.isArray(payload)) return payload.length;
    if (!payload || typeof payload !== 'object') return 0;
    if (typeof payload.total === 'number') return payload.total;
    if (typeof payload.count === 'number') return payload.count;
    return getItems(payload).length;
  }

  async function postJson(path, payload) { return request(path, { method: 'POST', body: JSON.stringify(payload || {}) }); }
  async function putJson(path, payload) { return request(path, { method: 'PUT', body: JSON.stringify(payload || {}) }); }

  window.RSAAdminApi = {
    getApiBaseUrl,
    request,
    postJson,
    putJson,
    getItems,
    getCount,
    getAuthHeaders,
    endpoints: {
      products: '/products',
      brands: '/brands',
      bookings: '/bookings',
      inquiries: '/inquiries',
      customers: '/customers',
      categories: '/categories',
      keyFeatures: '/key-features',
      adminUsers: '/admin/users',
      adminMediaConfig: '/admin/media/config',
      adminMediaPrepareUpload: '/admin/media/prepare-upload'
    }
  };
}());
"""
        write(path, default_admin_api)
        return
    text = read(path)
    if "adminUsers" in text:
        print(f"[skip] {rel(path)} already has adminUsers endpoint")
        return
    old = "      adminMediaPrepareUpload: '/admin/media/prepare-upload'"
    new = "      adminMediaPrepareUpload: '/admin/media/prepare-upload',\n      adminUsers: '/admin/users'"
    replace_or_append(path, old, new, "admin users endpoint")


def patch_settings_html() -> None:
    path = FRONTEND_ADMIN / "settings.html"
    if not path.exists():
        raise SystemExit(f"[fail] Missing {rel(path)}")
    text = read(path)
    original = text
    if "data-settings-users" not in text:
        # Insert inside the settings grid before the final closing section of data-settings-content.
        marker = "      </section>\n\n      <footer"
        if marker in text:
            text = text.replace(marker, USERS_SECTION_HTML + "\n      </section>\n\n      <footer", 1)
        else:
            marker = "      </section>\n"
            idx = text.rfind(marker)
            if idx == -1:
                raise SystemExit(f"[fail] Could not find settings content insertion point in {rel(path)}")
            text = text[:idx] + USERS_SECTION_HTML + "\n" + text[idx:]
    if USERS_SCRIPT not in text:
        if "admin-header-utilities-55d.js" in text:
            text = text.replace('  <script src="./assets/js/admin-header-utilities-55d.js"></script>', f'  {ROLE_GUARD_SCRIPT}\n  <script src="./assets/js/admin-header-utilities-55d.js"></script>\n  {USERS_SCRIPT}', 1)
        else:
            text = text.replace("</body>", f"  {ROLE_GUARD_SCRIPT}\n  {USERS_SCRIPT}\n</body>", 1)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Patched {rel(path)}")
    else:
        print(f"[skip] {rel(path)} already patched")


def patch_all_admin_html_role_guard() -> None:
    for path in sorted(FRONTEND_ADMIN.glob("*.html")):
        if path.name == "login.html":
            continue
        text = read(path)
        if "admin-role-guard-59a.js" in text:
            continue
        if "</body>" not in text:
            continue
        # Settings page gets role guard plus users script in patch_settings_html.
        if path.name == "settings.html":
            continue
        text = text.replace("</body>", f"  {ROLE_GUARD_SCRIPT}\n</body>", 1)
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Added role guard to {rel(path)}")


def patch_css() -> None:
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")
    text = read(ADMIN_CSS)
    if MARKER in text:
        print(f"[skip] {rel(ADMIN_CSS)} already has Batch 59A CSS")
        return
    ADMIN_CSS.write_text(text.rstrip() + BATCH59A_CSS + "\n", encoding="utf-8", newline="")
    print(f"[ok] Appended Batch 59A CSS to {rel(ADMIN_CSS)}")


def write_readme_copy() -> None:
    DOCS_README.mkdir(parents=True, exist_ok=True)
    readme = DOCS_README / "README_BATCH59A_COGNITO_GROUPS_SETTINGS_USERS.md"
    content = """# Batch 59A — Cognito Groups + Settings > Users\n\nStatus: implementation package prepared.\n\n## Scope\n\n- Use Cognito Groups for roles: `Admin` and `Standard`.\n- Settings > Users reads and manages Cognito users through protected FastAPI routes.\n- No DynamoDB users table is added.\n- The browser never calls Cognito admin APIs directly.\n- Admin-created users use suppressed invitation email and a backend-generated temporary password shown once only.\n- First Name and Last Name map to Cognito `given_name` and `family_name`.\n- The Users table displays generated Full Name.\n- Standard users do not see Settings and backend user-management routes require Admin.\n\n## Files patched or created\n\n```text\nbackend/app/auth/admin_auth.py\nbackend/app/main.py\nbackend/app/models/admin_user.py\nbackend/app/routes/admin_users.py\nbackend/app/services/admin_user_service.py\nfrontend/admin/settings.html\nfrontend/admin/assets/js/admin-api.js\nfrontend/admin/assets/js/admin-role-guard-59a.js\nfrontend/admin/assets/js/admin-users-59a.js\nfrontend/admin/assets/css/admin.css\ndocs/phase8/README_BATCH59A_COGNITO_GROUPS_SETTINGS_USERS.md\n```\n\n## Local verification markers\n\nExpected backend route markers after local start:\n\n```text\nGET /api/admin/users/health -> version: batch59a-cognito-groups-settings-users\nGET /api/admin/users -> items/count/roles\n```\n\nExpected browser markers:\n\n```text\nwindow.RSA_BATCH59A_ROLE_GUARD_VERSION\nwindow.RSA_BATCH59A_ADMIN_USERS_VERSION\nSettings > Users panel visible for Admin\nSettings hidden/restricted for Standard\n```\n\n## Notes\n\nAWS Console setup instructions are intentionally not duplicated here. Follow the chat instructions for creating/verifying Cognito groups and assigning the current admin user to the Admin group.\n"""
    write(readme, content)


def main() -> None:
    print(f"[start] Applying {MARKER}")
    if not BACKEND_APP.exists():
        raise SystemExit(f"[fail] Backend app folder not found: {rel(BACKEND_APP) if BACKEND_APP.exists() else BACKEND_APP}")
    if not FRONTEND_ADMIN.exists():
        raise SystemExit(f"[fail] Frontend admin folder not found: {FRONTEND_ADMIN}")

    write(BACKEND_APP / "models" / "admin_user.py", ADMIN_USER_MODELS)
    write(BACKEND_APP / "services" / "admin_user_service.py", ADMIN_USER_SERVICE)
    write(BACKEND_APP / "routes" / "admin_users.py", ADMIN_USERS_ROUTE)
    patch_admin_auth()
    patch_main_router()
    write(ADMIN_JS / "admin-role-guard-59a.js", ROLE_GUARD_JS)
    write(ADMIN_JS / "admin-users-59a.js", ADMIN_USERS_JS)
    patch_admin_api()
    patch_settings_html()
    patch_all_admin_html_role_guard()
    patch_css()
    write_readme_copy()
    print(f"[done] {MARKER} applied.")
    print("[done] No DynamoDB users table, SMS/MFA, email invitation workflow, Route 53, CloudFront, or paid notification feature added.")


if __name__ == "__main__":
    main()
