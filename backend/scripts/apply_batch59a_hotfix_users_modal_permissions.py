from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ADMIN = ROOT / "frontend" / "admin"
ADMIN_JS = FRONTEND_ADMIN / "assets" / "js" / "admin-users-59a.js"
ADMIN_CSS = FRONTEND_ADMIN / "assets" / "css" / "admin.css"
SETTINGS_HTML = FRONTEND_ADMIN / "settings.html"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_users_modal_permissions.md"
MARKER = "batch59a-hotfix-users-modal-permissions"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace('\\', '/')


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='')
    print(f"[ok] Wrote {rel(path)}")


ADD_MODAL_HTML = r'''        <div class="user-add-modal" data-user-add-modal hidden data-admin-requires-admin>
          <div class="user-add-card">
            <button class="modal-close" type="button" data-user-add-close aria-label="Close">&times;</button>
            <p class="eyebrow">Add user</p>
            <h2>Create Cognito User</h2>
            <p class="settings-note">The temporary password is shown once only after create/reset.</p>
            <form data-user-create-form>
              <label>First Name <input name="first_name" type="text" required maxlength="80" /></label>
              <label>Last Name <input name="last_name" type="text" required maxlength="80" /></label>
              <label>Email <input name="email" type="email" required autocomplete="off" /></label>
              <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
              <div class="settings-actions"><button class="admin-button" type="submit">Create User</button><button class="admin-button secondary" type="button" data-user-add-close>Cancel</button></div>
            </form>
          </div>
        </div>'''

EDIT_MODAL_HTML = r'''        <div class="user-edit-modal" data-user-edit-modal hidden data-admin-requires-admin>
          <div class="user-edit-card">
            <button class="modal-close" type="button" data-user-edit-close aria-label="Close">&times;</button>
            <p class="eyebrow">Edit user</p>
            <h2 data-edit-user-email>User</h2>
            <form data-user-edit-form>
              <label>Full Name <input name="full_name" type="text" required maxlength="160" /></label>
              <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
              <label class="users-checkbox"><input name="enabled" type="checkbox" /> Enabled</label>
              <div class="settings-actions"><button class="admin-button" type="submit">Save User</button><button class="admin-button secondary" type="button" data-user-edit-close>Cancel</button></div>
            </form>
          </div>
        </div>'''

ADMIN_USERS_JS = r'''(function () {
  'use strict';

  const VERSION = 'batch59a-hotfix-users-modal-permissions';
  window.RSA_BATCH59A_ADMIN_USERS_VERSION = VERSION;

  const state = { users: [], editingUsername: '' };

  function qs(selector, root) { return (root || document).querySelector(selector); }
  function qsa(selector, root) { return Array.from((root || document).querySelectorAll(selector)); }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function splitFullName(fullName) {
    const clean = String(fullName || '').trim().replace(/\s+/g, ' ');
    if (!clean) return { first_name: '', last_name: '' };
    const parts = clean.split(' ');
    if (parts.length === 1) return { first_name: parts[0], last_name: '-' };
    return { first_name: parts.slice(0, -1).join(' '), last_name: parts.slice(-1)[0] };
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

  async function request(path, options) { return api().request(path, options || {}); }
  function getItems(payload) { return api().getItems(payload); }

  function rolePill(role) {
    const isAdmin = role === 'Admin';
    return `<span class="users-role-pill ${isAdmin ? 'is-admin' : 'is-standard'}">${escapeHtml(role || 'Standard')}</span>`;
  }

  function statusPill(user) {
    const enabled = user.enabled !== false;
    return `<span class="users-status-pill ${enabled ? 'is-enabled' : 'is-disabled'}">${enabled ? 'Enabled' : 'Disabled'}</span>`;
  }

  function displayName(user) {
    return user.full_name || user.name || user.email || user.username || 'User';
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
        <td class="users-name-cell"><strong>${escapeHtml(displayName(user))}</strong><small>${escapeHtml(user.username || '')}</small></td>
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

  function describePermissionError(message) {
    const text = String(message || '');
    if (text.includes('AccessDenied') && text.includes('cognito-idp:')) {
      return 'The backend AWS identity can reach Cognito but is missing Cognito IDP permissions. Update the IAM policy for the local AWS user/role, then refresh users.';
    }
    return text || 'Check Cognito groups, backend auth, and IAM permissions.';
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
      setText('[data-users-count]', '0');
      setStatus('is-warning', 'Unable to load users.', describePermissionError(error.message));
    }
  }

  function openAddModal() {
    const modal = qs('[data-user-add-modal]');
    const form = qs('[data-user-create-form]', modal);
    if (!modal || !form) return;
    form.reset();
    if (form.elements.role) form.elements.role.value = 'Standard';
    modal.hidden = false;
    setTimeout(() => form.elements.first_name && form.elements.first_name.focus(), 0);
  }

  function closeAddModal() {
    const modal = qs('[data-user-add-modal]');
    if (modal) modal.hidden = true;
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
      closeAddModal();
      form.reset();
      showTempPassword(result);
      await loadUsers();
      setStatus('is-success', 'User created.', 'Copy the temporary password and send it securely to the user.');
    } catch (error) {
      setStatus('is-warning', 'Unable to create user.', describePermissionError(error.message));
    }
  }

  function openEdit(username) {
    const user = state.users.find((item) => item.username === username || item.email === username);
    const form = qs('[data-user-edit-form]');
    const modal = qs('[data-user-edit-modal]');
    if (!user || !form || !modal) return;
    state.editingUsername = user.username;
    form.elements.full_name.value = displayName(user);
    form.elements.role.value = user.role || 'Standard';
    form.elements.enabled.checked = user.enabled !== false;
    setText('[data-edit-user-email]', user.email || user.username || 'User');
    modal.hidden = false;
  }

  function closeEdit() {
    state.editingUsername = '';
    const modal = qs('[data-user-edit-modal]');
    if (modal) modal.hidden = true;
  }

  async function saveEdit(event) {
    event.preventDefault();
    if (!state.editingUsername) return;
    const form = event.currentTarget;
    const nameParts = splitFullName(form.elements.full_name.value);
    const payload = {
      first_name: nameParts.first_name,
      last_name: nameParts.last_name,
      role: String(form.elements.role.value || 'Standard'),
      enabled: !!form.elements.enabled.checked,
    };
    setStatus('', 'Saving user…', 'Updating Cognito attributes and group assignment.');
    try {
      await request(`/admin/users/${encodeURIComponent(state.editingUsername)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      closeEdit();
      await loadUsers();
      setStatus('is-success', 'User saved.', 'Cognito user attributes and role were updated.');
    } catch (error) {
      setStatus('is-warning', 'Unable to save user.', describePermissionError(error.message));
    }
  }

  async function resetPassword(username) {
    if (!confirm('Generate a new temporary password for this user? The password is shown once only.')) return;
    setStatus('', 'Resetting password…', 'Generating a one-time visible temporary password.');
    try {
      const result = await request(`/admin/users/${encodeURIComponent(username)}/reset-password`, { method: 'POST' });
      showTempPassword(result);
      await loadUsers();
      setStatus('is-success', 'Temporary password generated.', 'Copy it now. It cannot be viewed again later.');
    } catch (error) {
      setStatus('is-warning', 'Unable to reset password.', describePermissionError(error.message));
    }
  }

  async function setEnabled(username, enabled) {
    setStatus('', enabled ? 'Enabling user…' : 'Disabling user…', 'Updating Cognito user status.');
    try {
      await request(`/admin/users/${encodeURIComponent(username)}/${enabled ? 'enable' : 'disable'}`, { method: 'POST' });
      await loadUsers();
      setStatus('is-success', enabled ? 'User enabled.' : 'User disabled.', 'Cognito user status was updated.');
    } catch (error) {
      setStatus('is-warning', 'Unable to update user status.', describePermissionError(error.message));
    }
  }

  function handleTableClick(event) {
    const button = event.target.closest('[data-user-action]');
    if (!button) return;
    const username = button.dataset.username || '';
    const action = button.dataset.userAction;
    if (action === 'edit') openEdit(username);
    if (action === 'reset') resetPassword(username);
    if (action === 'enable') setEnabled(username, true);
    if (action === 'disable') setEnabled(username, false);
  }

  function bind() {
    const refresh = qs('[data-users-refresh]');
    if (refresh) refresh.addEventListener('click', loadUsers);
    const addOpen = qs('[data-user-add-open]');
    if (addOpen) addOpen.addEventListener('click', openAddModal);
    qsa('[data-user-add-close]').forEach((button) => button.addEventListener('click', closeAddModal));
    const createForm = qs('[data-user-create-form]');
    if (createForm) createForm.addEventListener('submit', createUser);
    const editForm = qs('[data-user-edit-form]');
    if (editForm) editForm.addEventListener('submit', saveEdit);
    qsa('[data-user-edit-close]').forEach((button) => button.addEventListener('click', closeEdit));
    const table = qs('[data-users-table-body]');
    if (table) table.addEventListener('click', handleTableClick);
    document.addEventListener('click', (event) => {
      const copy = event.target.closest('[data-copy-temp-password]');
      if (!copy) return;
      const code = qs('[data-temp-password-panel] code');
      if (code && navigator.clipboard) navigator.clipboard.writeText(code.textContent || '');
    });
    qsa('[data-user-add-modal], [data-user-edit-modal]').forEach((modal) => {
      modal.addEventListener('click', (event) => {
        if (event.target === modal) {
          if (modal.matches('[data-user-add-modal]')) closeAddModal();
          if (modal.matches('[data-user-edit-modal]')) closeEdit();
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const usersCard = qs('[data-settings-users]');
    if (!usersCard) return;
    bind();
    loadUsers();
  });
})();
'''

CSS_APPEND = r'''

/* batch59a-hotfix-users-modal-permissions */
.users-toolbar-actions { display: flex; align-items: center; justify-content: flex-end; gap: 10px; flex-wrap: wrap; }
.users-add-actions { display: none; }
.user-add-modal { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 22px; background: rgba(15, 23, 42, 0.55); }
.user-add-modal[hidden] { display: none !important; }
.user-add-card { position: relative; width: min(560px, 100%); display: grid; gap: 14px; background: #fff; border-radius: 18px; padding: 24px; box-shadow: 0 24px 70px rgba(15, 23, 42, 0.24); }
.user-add-card .modal-close { position: absolute; top: 14px; right: 16px; border: 0; background: #f1f5f9; width: 34px; height: 34px; border-radius: 999px; cursor: pointer; font-size: 1.4rem; }
.user-add-card label,
.user-edit-card label { display: grid; gap: 6px; font-size: 0.82rem; font-weight: 800; color: #334155; }
.user-add-card input,
.user-add-card select,
.user-edit-card input,
.user-edit-card select { width: 100%; border: 1px solid #d1d5db; border-radius: 10px; padding: 10px 11px; color: #111827; background: #fff; }
.users-name-cell strong { display: block; }
.users-name-cell small { color: #64748b; }
@media (max-width: 640px) { .users-toolbar-actions { width: 100%; justify-content: stretch; } .users-toolbar-actions .admin-button { flex: 1 1 auto; } }
'''

DOC_TEXT = r'''# Phase 8 Batch 59A Hotfix — Users Modal and Cognito Permissions

Status: hotfix for Batch 59A local testing

## Purpose

Corrects two Batch 59A issues found during local browser testing:

1. The Settings > Users add form was incorrectly displayed inline. It is now opened through an Add User modal.
2. The Users table remains a Full Name table. First Name and Last Name are only used by the Add User modal to populate Cognito `given_name`, `family_name`, and `name` attributes.

The backend error shown in the browser is not a UI bug. It means the AWS identity used by local backend credentials is missing Cognito IDP permissions, especially `cognito-idp:ListGroups`. The IAM policy must be updated outside this script.

## Files affected

- `frontend/admin/settings.html`
- `frontend/admin/assets/js/admin-users-59a.js`
- `frontend/admin/assets/css/admin.css`

## Not changed

- No DynamoDB users table.
- No SMS/MFA.
- No email invitation workflow.
- No EC2, Route 53, CloudFront, or paid notification change.
'''


def patch_settings_html() -> None:
    text = read(SETTINGS_HTML)

    old_toolbar = '''          <div class="users-toolbar">
            <strong><span data-users-count>0</span> users</strong>
            <button class="admin-button secondary" type="button" data-users-refresh>Refresh Users</button>
          </div>'''
    new_toolbar = '''          <div class="users-toolbar">
            <strong><span data-users-count>0</span> users</strong>
            <div class="users-toolbar-actions">
              <button class="admin-button secondary" type="button" data-users-refresh>Refresh Users</button>
              <button class="admin-button" type="button" data-user-add-open>Add User</button>
            </div>
          </div>'''
    if old_toolbar in text:
        text = text.replace(old_toolbar, new_toolbar, 1)
        print(f"[ok] Patched Users toolbar in {rel(SETTINGS_HTML)}")
    elif 'data-user-add-open' in text:
        print(f"[skip] Users Add button already present in {rel(SETTINGS_HTML)}")
    else:
        print(f"[warn] Users toolbar block not found in {rel(SETTINGS_HTML)}")

    form_pattern = re.compile(r'\n\s*<form class="users-create-form" data-user-create-form>.*?</form>', re.DOTALL)
    if form_pattern.search(text):
        text = form_pattern.sub('', text, count=1)
        print(f"[ok] Removed inline Add User form from {rel(SETTINGS_HTML)}")
    else:
        print(f"[skip] Inline Add User form not found in {rel(SETTINGS_HTML)}")

    edit_pattern = re.compile(r'\n\s*<div class="user-edit-modal" data-user-edit-modal hidden data-admin-requires-admin>.*?</div>\s*</div>', re.DOTALL)
    if edit_pattern.search(text):
        text = edit_pattern.sub('\n' + EDIT_MODAL_HTML, text, count=1)
        print(f"[ok] Patched Edit User modal to Full Name in {rel(SETTINGS_HTML)}")
    else:
        print(f"[skip] Edit User modal replacement skipped; expected modal block not found.")

    if 'data-user-add-modal' not in text:
        insert_before = '<div class="user-edit-modal" data-user-edit-modal'
        idx = text.find(insert_before)
        if idx != -1:
            text = text[:idx] + ADD_MODAL_HTML + '\n\n        ' + text[idx:]
            print(f"[ok] Added Add User modal in {rel(SETTINGS_HTML)}")
        else:
            text = text.replace('</body>', ADD_MODAL_HTML + '\n</body>', 1)
            print(f"[ok] Added Add User modal before body close in {rel(SETTINGS_HTML)}")
    else:
        print(f"[skip] Add User modal already present in {rel(SETTINGS_HTML)}")

    write(SETTINGS_HTML, text)


def patch_css() -> None:
    text = read(ADMIN_CSS)
    if MARKER in text:
        print(f"[skip] CSS hotfix already present in {rel(ADMIN_CSS)}")
        return
    write(ADMIN_CSS, text.rstrip() + CSS_APPEND)


def main() -> None:
    print(f"[start] Applying {MARKER}")
    if not SETTINGS_HTML.exists():
        raise SystemExit(f"[fail] Missing {rel(SETTINGS_HTML)}")
    if not ADMIN_JS.parent.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_JS.parent)}")
    patch_settings_html()
    write(ADMIN_JS, ADMIN_USERS_JS)
    patch_css()
    write(DOC, DOC_TEXT)
    print(f"[done] {MARKER} applied.")
    print("[done] Add User is now modal-based; Users table remains Full Name based.")
    print("[note] If users still do not load, update IAM permissions for the AWS identity used by the local backend.")


if __name__ == '__main__':
    main()
