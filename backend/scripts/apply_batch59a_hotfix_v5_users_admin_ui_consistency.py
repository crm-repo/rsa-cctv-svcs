from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_HTML = ROOT / "frontend" / "admin" / "settings.html"
ADMIN_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-users-59a.js"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_v5_users_admin_ui_consistency.md"
MARKER = "batch59a-hotfix-v5-users-admin-ui-consistency"
FA_LINK = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />'

NAV_ICON_MAP = {
    "Dashboard": "fa-solid fa-gauge-high",
    "Products": "fa-solid fa-box-open",
    "Categories": "fa-solid fa-table-list",
    "Brands": "fa-solid fa-certificate",
    "Key Features": "fa-solid fa-star",
    "Customers": "fa-solid fa-users",
    "Bookings": "fa-solid fa-calendar-check",
    "Inquiries": "fa-solid fa-file-circle-question",
    "About Us": "fa-solid fa-address-card",
    "Project Gallery": "fa-solid fa-images",
    "Services": "fa-solid fa-screwdriver-wrench",
    "Contact Us": "fa-solid fa-address-book",
    "Settings": "fa-solid fa-gear",
    "Logout": "fa-solid fa-right-from-bracket",
}

ADD_MODAL_HTML = '''        <div class="user-add-modal admin-modal-overlay" data-user-add-modal hidden data-admin-requires-admin>
          <div class="user-add-card admin-modal-card" role="dialog" aria-modal="true" aria-labelledby="user-add-title">
            <button class="modal-close" type="button" data-user-add-close aria-label="Close">&times;</button>
            <p class="eyebrow">Add User</p>
            <h2 id="user-add-title">Create Cognito User</h2>
            <p class="settings-note">A temporary password is shown once after the user is created or reset.</p>
            <div class="users-modal-status" data-user-add-status hidden></div>
            <form data-user-create-form>
              <label>First Name <input name="first_name" type="text" required maxlength="80" autocomplete="given-name" /></label>
              <label>Last Name <input name="last_name" type="text" required maxlength="80" autocomplete="family-name" /></label>
              <label>Email <input name="email" type="email" required autocomplete="off" /></label>
              <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
              <div class="settings-actions"><button class="admin-button" type="submit" data-user-create-submit>Create User</button><button class="admin-button secondary" type="button" data-user-add-close>Cancel</button></div>
            </form>
          </div>
        </div>'''

EDIT_MODAL_HTML = '''        <div class="user-edit-modal admin-modal-overlay" data-user-edit-modal hidden data-admin-requires-admin>
          <div class="user-edit-card admin-modal-card" role="dialog" aria-modal="true" aria-labelledby="user-edit-title">
            <button class="modal-close" type="button" data-user-edit-close aria-label="Close">&times;</button>
            <p class="eyebrow">Edit User</p>
            <h2 id="user-edit-title" data-edit-user-email>User</h2>
            <div class="users-modal-status" data-user-edit-status hidden></div>
            <form data-user-edit-form>
              <label>Full Name <input name="full_name" type="text" required maxlength="160" /></label>
              <label>Role <select name="role"><option value="Standard">Standard</option><option value="Admin">Admin</option></select></label>
              <label class="users-checkbox"><input name="enabled" type="checkbox" /> Enabled</label>
              <div class="settings-actions"><button class="admin-button" type="submit" data-user-edit-submit>Save User</button><button class="admin-button secondary" type="button" data-user-edit-close>Cancel</button></div>
            </form>
          </div>
        </div>'''

ADMIN_USERS_JS = r'''(function () {
  'use strict';

  const VERSION = 'batch59a-hotfix-v5-users-admin-ui-consistency';
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

  function setText(selector, value, root) {
    const el = qs(selector, root);
    if (el) el.textContent = value;
  }

  function normalizeUsersToolbar() {
    const card = qs('[data-settings-users]');
    if (!card) return;

    let toolbar = qs('.users-toolbar', card);
    if (!toolbar) {
      const tableWrap = qs('.users-table-wrap', card) || qs('table', card);
      toolbar = document.createElement('div');
      toolbar.className = 'users-toolbar';
      if (tableWrap && tableWrap.parentNode) tableWrap.parentNode.insertBefore(toolbar, tableWrap);
      else card.appendChild(toolbar);
    }

    let status = qs('[data-users-status]', card);
    if (!status) {
      status = document.createElement('div');
      status.className = 'users-inline-status';
      status.setAttribute('data-users-status', '');
      status.hidden = true;
    }

    let statusWrap = qs('.users-toolbar-status-left', toolbar);
    if (!statusWrap) {
      statusWrap = document.createElement('div');
      statusWrap.className = 'users-toolbar-status-left';
      toolbar.insertBefore(statusWrap, toolbar.firstChild);
    }
    if (status.parentNode !== statusWrap) statusWrap.appendChild(status);

    let actions = qs('.users-toolbar-actions', toolbar);
    if (!actions) {
      actions = document.createElement('div');
      actions.className = 'users-toolbar-actions';
      const refresh = qs('[data-users-refresh]', toolbar) || qs('[data-users-refresh]', card);
      const add = qs('[data-user-add-open]', toolbar) || qs('[data-user-add-open]', card);
      if (refresh) actions.appendChild(refresh);
      if (add) actions.appendChild(add);
      toolbar.appendChild(actions);
    }

    const countStrong = qs('.users-toolbar > strong', toolbar);
    if (countStrong) countStrong.hidden = true;
  }

  function parseErrorMessage(error) {
    const raw = String(error && error.message ? error.message : error || '').trim();
    if (!raw) return 'Request failed. Check backend logs.';
    if (raw.includes('401') || raw.toLowerCase().includes('unauthorized')) {
      return '401 Unauthorized. Log out, log back in, then retry. If you recently added your user to the Admin group, the old token must be refreshed.';
    }
    if (raw.includes('AccessDenied') && raw.includes('cognito-idp:')) {
      return 'Missing Cognito IDP permission for the backend AWS identity. Update IAM, restart backend, then retry.';
    }
    if (raw.includes('UsernameExistsException') || raw.toLowerCase().includes('already exists')) {
      return 'This email/user already exists in Cognito. Use another email or reset the existing user password.';
    }
    if (raw.length > 220) return raw.slice(0, 220) + '…';
    return raw;
  }

  function setPageStatus(kind, title, detail) {
    normalizeUsersToolbar();
    const card = qs('[data-users-status]');
    if (!card) return;
    if (!title && !detail) {
      card.hidden = true;
      card.innerHTML = '';
      return;
    }
    card.hidden = false;
    card.className = `users-inline-status ${kind || ''}`.trim();
    card.innerHTML = `<strong>${escapeHtml(title || '')}</strong>${detail ? `<span>${escapeHtml(detail)}</span>` : ''}`;
  }

  function setModalStatus(selector, kind, title, detail) {
    const card = qs(selector);
    if (!card) return;
    card.hidden = false;
    card.className = `users-modal-status ${kind || ''}`.trim();
    card.innerHTML = `<strong>${escapeHtml(title || '')}</strong>${detail ? `<span>${escapeHtml(detail)}</span>` : ''}`;
  }

  function clearModalStatus(selector) {
    const card = qs(selector);
    if (!card) return;
    card.hidden = true;
    card.innerHTML = '';
    card.className = 'users-modal-status';
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
    const full = String(user.full_name || user.name || '').trim();
    return full || user.email || user.username || 'User';
  }

  function splitFullName(fullName) {
    const clean = String(fullName || '').trim().replace(/\s+/g, ' ');
    if (!clean) return { first_name: '', last_name: '' };
    const parts = clean.split(' ');
    if (parts.length === 1) return { first_name: parts[0], last_name: '-' };
    return { first_name: parts.slice(0, -1).join(' '), last_name: parts.slice(-1)[0] };
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

  async function loadUsers() {
    setPageStatus('', 'Loading users…', '');
    try {
      const payload = await request('/admin/users');
      state.users = getItems(payload);
      renderUsers();
      setText('[data-users-count]', String(state.users.length));
      setPageStatus('is-success', 'Users loaded.', `${state.users.length} record(s).`);
    } catch (error) {
      console.error(error);
      state.users = [];
      renderUsers();
      setText('[data-users-count]', '0');
      setPageStatus('is-warning', 'Unable to load users.', parseErrorMessage(error));
    }
  }

  function openAddModal() {
    const modal = qs('[data-user-add-modal]');
    const form = qs('[data-user-create-form]', modal);
    if (!modal || !form) return;
    form.reset();
    if (form.elements.role) form.elements.role.value = 'Standard';
    clearModalStatus('[data-user-add-status]');
    document.body.classList.add('admin-modal-open');
    modal.hidden = false;
    setTimeout(() => form.elements.first_name && form.elements.first_name.focus(), 0);
  }

  function closeAddModal() {
    const modal = qs('[data-user-add-modal]');
    if (modal) modal.hidden = true;
    document.body.classList.remove('admin-modal-open');
    clearModalStatus('[data-user-add-status]');
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
    clearModalStatus('[data-user-edit-status]');
    document.body.classList.add('admin-modal-open');
    modal.hidden = false;
  }

  function closeEdit() {
    state.editingUsername = '';
    const modal = qs('[data-user-edit-modal]');
    if (modal) modal.hidden = true;
    document.body.classList.remove('admin-modal-open');
    clearModalStatus('[data-user-edit-status]');
  }

  function showTempPassword(result) {
    const panel = qs('[data-temp-password-panel]');
    if (!panel) return;
    const password = result.temporary_password || '';
    if (!password) {
      panel.hidden = true;
      panel.innerHTML = '';
      return;
    }
    panel.hidden = false;
    panel.innerHTML = `<strong>Temporary password</strong><span>Copy now. It cannot be viewed again.</span><code>${escapeHtml(password)}</code><button type="button" data-copy-temp-password>Copy</button>`;
  }

  function setBusy(form, busy) {
    if (!form) return;
    qsa('button, input, select', form).forEach((field) => {
      if (field.matches('[type="button"].secondary')) return;
      field.disabled = !!busy;
    });
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
    setModalStatus('[data-user-add-status]', '', 'Creating user…', '');
    setBusy(form, true);
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
      setPageStatus('is-success', 'User created.', 'Temporary password shown below.');
    } catch (error) {
      console.error(error);
      setModalStatus('[data-user-add-status]', 'is-warning', 'Unable to create user.', parseErrorMessage(error));
      setPageStatus('is-warning', 'Create user failed.', 'See the Add User modal.');
    } finally {
      setBusy(form, false);
    }
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
    setModalStatus('[data-user-edit-status]', '', 'Saving user…', '');
    setBusy(form, true);
    try {
      await request(`/admin/users/${encodeURIComponent(state.editingUsername)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      closeEdit();
      await loadUsers();
      setPageStatus('is-success', 'User saved.', '');
    } catch (error) {
      console.error(error);
      setModalStatus('[data-user-edit-status]', 'is-warning', 'Unable to save user.', parseErrorMessage(error));
      setPageStatus('is-warning', 'Save user failed.', 'See the Edit User modal.');
    } finally {
      setBusy(form, false);
    }
  }

  async function resetPassword(username) {
    if (!confirm('Generate a new temporary password for this user?')) return;
    setPageStatus('', 'Resetting password…', '');
    try {
      const result = await request(`/admin/users/${encodeURIComponent(username)}/reset-password`, { method: 'POST' });
      showTempPassword(result);
      await loadUsers();
      setPageStatus('is-success', 'Temporary password generated.', 'Copy it now.');
    } catch (error) {
      setPageStatus('is-warning', 'Unable to reset password.', parseErrorMessage(error));
    }
  }

  async function setEnabled(username, enabled) {
    setPageStatus('', enabled ? 'Enabling user…' : 'Disabling user…', '');
    try {
      await request(`/admin/users/${encodeURIComponent(username)}/${enabled ? 'enable' : 'disable'}`, { method: 'POST' });
      await loadUsers();
      setPageStatus('is-success', enabled ? 'User enabled.' : 'User disabled.', '');
    } catch (error) {
      setPageStatus('is-warning', 'Unable to update user.', parseErrorMessage(error));
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
    normalizeUsersToolbar();
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
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      if (qs('[data-user-add-modal]:not([hidden])')) closeAddModal();
      if (qs('[data-user-edit-modal]:not([hidden])')) closeEdit();
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

/* batch59a-hotfix-v5-users-admin-ui-consistency */
.settings-card[data-settings-users] {
  margin-top: 42px !important;
  padding: 28px !important;
  border-radius: 22px !important;
  background: #ffffff !important;
  border: 1px solid rgba(226, 232, 240, 0.96) !important;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.055) !important;
}
.settings-card[data-settings-users] .users-toolbar {
  display: flex !important;
  align-items: stretch !important;
  justify-content: space-between !important;
  gap: 16px !important;
  margin: 22px 0 20px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}
.settings-card[data-settings-users] .users-toolbar > strong,
.settings-card[data-settings-users] [data-users-count] {
  display: none !important;
}
.settings-card[data-settings-users] .users-toolbar-status-left {
  flex: 1 1 auto !important;
  min-width: 260px !important;
  display: flex !important;
  align-items: stretch !important;
}
.settings-card[data-settings-users] .users-toolbar-actions {
  flex: 0 0 auto !important;
  display: flex !important;
  align-items: stretch !important;
  justify-content: flex-end !important;
  gap: 12px !important;
}
.settings-card[data-settings-users] .users-inline-status {
  width: min(720px, 100%) !important;
  min-height: 54px !important;
  display: grid !important;
  align-content: center !important;
  gap: 3px !important;
  margin: 0 !important;
  padding: 12px 16px !important;
  border-radius: 14px !important;
  border: 1px solid rgba(148, 163, 184, 0.26) !important;
  background: #f8fafc !important;
  color: #334155 !important;
  box-shadow: none !important;
}
.settings-card[data-settings-users] .users-inline-status[hidden] {
  display: none !important;
}
.settings-card[data-settings-users] .users-inline-status strong {
  margin: 0 !important;
  font-weight: 900 !important;
  color: #0f172a !important;
}
.settings-card[data-settings-users] .users-inline-status span {
  margin: 0 !important;
  font-size: 0.88rem !important;
  line-height: 1.35 !important;
  overflow-wrap: anywhere !important;
}
.settings-card[data-settings-users] .users-inline-status.is-success {
  background: #f0fdf4 !important;
  border-color: rgba(22, 163, 74, 0.28) !important;
  color: #166534 !important;
}
.settings-card[data-settings-users] .users-inline-status.is-success strong {
  color: #052e16 !important;
}
.settings-card[data-settings-users] .users-inline-status.is-warning {
  background: #fff7ed !important;
  border-color: rgba(194, 65, 12, 0.34) !important;
  color: #9a3412 !important;
}
.settings-card[data-settings-users] .users-inline-status.is-warning strong {
  color: #7c2d12 !important;
}
.settings-card[data-settings-users] .users-table-wrap {
  margin-top: 0 !important;
  border-radius: 18px !important;
  border: 1px solid rgba(226, 232, 240, 0.96) !important;
  background: #ffffff !important;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.035) !important;
  overflow: auto !important;
}
.settings-card[data-settings-users] .users-temp-password[hidden],
.settings-card[data-settings-users] .users-temp-password:empty,
.settings-card[data-settings-users] .users-temp-password:not(:has(code)) {
  display: none !important;
}
.admin-sidebar .nav-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.admin-sidebar .nav-icon i,
.admin-page-heading .page-icon i,
.settings-card-heading > span i {
  display: inline-block !important;
  font-family: "Font Awesome 6 Free" !important;
  font-weight: 900 !important;
  line-height: 1 !important;
  font-style: normal !important;
}
body.admin-modal-open {
  overflow: hidden !important;
}
.user-add-modal,
.user-edit-modal,
.admin-modal-overlay {
  position: fixed !important;
  inset: 0 !important;
  z-index: 3000 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 32px !important;
  background: rgba(15, 23, 42, 0.52) !important;
  backdrop-filter: blur(2px) !important;
}
.user-add-modal[hidden],
.user-edit-modal[hidden],
.admin-modal-overlay[hidden] {
  display: none !important;
}
.user-add-card,
.user-edit-card,
.admin-modal-card {
  position: relative !important;
  width: min(620px, calc(100vw - 48px)) !important;
  max-height: calc(100vh - 48px) !important;
  overflow-y: auto !important;
  display: grid !important;
  gap: 14px !important;
  background: #ffffff !important;
  border: 1px solid rgba(226, 232, 240, 0.95) !important;
  border-radius: 20px !important;
  padding: 32px !important;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.28) !important;
}
.user-add-card .eyebrow,
.user-edit-card .eyebrow {
  margin: 0 !important;
}
.user-add-card h2,
.user-edit-card h2 {
  margin: 0 !important;
  line-height: 1.18 !important;
}
.user-add-card .settings-note,
.user-edit-card .settings-note {
  margin: 0 0 4px !important;
}
.user-add-card form,
.user-edit-card form {
  display: grid !important;
  gap: 14px !important;
}
.user-add-card label,
.user-edit-card label {
  display: grid !important;
  gap: 7px !important;
  margin: 0 !important;
  font-size: 0.86rem !important;
  font-weight: 850 !important;
  color: #334155 !important;
}
.user-add-card input,
.user-add-card select,
.user-edit-card input,
.user-edit-card select {
  width: 100% !important;
  min-height: 48px !important;
  border: 1px solid #d1d5db !important;
  border-radius: 12px !important;
  padding: 11px 13px !important;
  color: #111827 !important;
  background: #fff !important;
  font: inherit !important;
}
.user-add-card input:focus,
.user-add-card select:focus,
.user-edit-card input:focus,
.user-edit-card select:focus {
  outline: none !important;
  border-color: rgba(185, 28, 28, 0.48) !important;
  box-shadow: 0 0 0 4px rgba(185, 28, 28, 0.08) !important;
}
.user-add-card .modal-close,
.user-edit-card .modal-close {
  position: absolute !important;
  top: 18px !important;
  right: 18px !important;
  width: 42px !important;
  height: 42px !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: #f1f5f9 !important;
  color: #0f172a !important;
  cursor: pointer !important;
  font-size: 1.45rem !important;
  line-height: 1 !important;
}
.user-add-card .settings-actions,
.user-edit-card .settings-actions {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  margin-top: 8px !important;
}
.users-modal-status {
  display: grid !important;
  gap: 4px !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(148, 163, 184, 0.28) !important;
  border-radius: 13px !important;
  background: #f8fafc !important;
  color: #334155 !important;
  line-height: 1.42 !important;
}
.users-modal-status[hidden] {
  display: none !important;
}
.users-modal-status strong {
  color: #0f172a !important;
  font-weight: 900 !important;
}
.users-modal-status span {
  font-size: 0.88rem !important;
  overflow-wrap: anywhere !important;
}
.users-modal-status.is-warning {
  background: #fff7ed !important;
  border-color: rgba(194, 65, 12, 0.34) !important;
  color: #9a3412 !important;
}
.users-modal-status.is-warning strong {
  color: #7c2d12 !important;
}
.users-modal-status.is-success {
  background: #f0fdf4 !important;
  border-color: rgba(21, 128, 61, 0.3) !important;
  color: #166534 !important;
}
.users-checkbox {
  display: flex !important;
  align-items: center !important;
  gap: 9px !important;
}
.users-checkbox input {
  width: auto !important;
  min-height: auto !important;
}
@media (max-width: 760px) {
  .settings-card[data-settings-users] {
    padding: 22px !important;
  }
  .settings-card[data-settings-users] .users-toolbar {
    flex-direction: column !important;
  }
  .settings-card[data-settings-users] .users-toolbar-actions,
  .settings-card[data-settings-users] .users-toolbar-actions .admin-button {
    width: 100% !important;
  }
  .user-add-modal,
  .user-edit-modal,
  .admin-modal-overlay {
    padding: 18px !important;
  }
  .user-add-card,
  .user-edit-card,
  .admin-modal-card {
    width: min(100%, calc(100vw - 24px)) !important;
    padding: 28px 22px 24px !important;
  }
}
'''

DOC_TEXT = """# Phase 8 Batch 59A Hotfix v5 — Users Admin UI Consistency

Status: targeted local UI hotfix

## Purpose

Normalize Settings > Users behavior with the rest of the admin UI after local Batch 59A testing.

## Fixes

- Moves the users return/status message into the toolbar row on the left.
- Keeps Refresh Users and Add User buttons on the right.
- Shortens success/error status messages.
- Keeps Add/Edit User modal error messages inside the modal.
- Normalizes the Add/Edit User modal overlay, spacing, and body scroll behavior.
- Keeps the Users table Full Name based.
- Keeps First Name and Last Name only inside the Add User form.
- Ensures sidebar Font Awesome icons are normalized on the Settings page.

## Not changed

- No Cognito backend route change.
- No IAM policy change.
- No DynamoDB users table.
- No EC2 or deployment change.

## Current known create-user test note

If Create User shows `401 Unauthorized`, log out and log back in before retrying. If the Admin group was added after the current login token was issued, the browser token must be refreshed by logging in again.
"""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace('\\', '/')


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='')
    print(f"[ok] Wrote {rel(path)}")


def ensure_fontawesome(text: str) -> str:
    if "cdnjs.cloudflare.com/ajax/libs/font-awesome" in text or "fontawesome" in text.lower():
        return text
    if '<link rel="stylesheet" href="./assets/css/admin.css" />' in text:
        return text.replace('<link rel="stylesheet" href="./assets/css/admin.css" />', FA_LINK + '\n  <link rel="stylesheet" href="./assets/css/admin.css" />', 1)
    return text.replace('</head>', '  ' + FA_LINK + '\n</head>', 1)


def normalize_sidebar_icons(text: str) -> str:
    for label, icon in NAV_ICON_MAP.items():
        pattern = re.compile(
            r'(<a class="nav-item[^"]*"[^>]*>\s*<span class="nav-icon">)(.*?)(</span>\s*<span>' + re.escape(label) + r'</span>\s*</a>)',
            flags=re.DOTALL,
        )
        text = pattern.sub(r'\1<i class="' + icon + r'" aria-hidden="true"></i>\3', text)
    return text


def replace_or_insert_modals(text: str) -> str:
    add_pattern = re.compile(r'\n\s*<div class="user-add-modal[^>]*data-user-add-modal.*?</div>\s*</div>', re.DOTALL)
    if add_pattern.search(text):
        text = add_pattern.sub('\n' + ADD_MODAL_HTML, text, count=1)
        print('[ok] Replaced Add User modal with v5 version.')
    else:
        idx = text.find('<div class="user-edit-modal')
        if idx == -1:
            idx = text.find('</body>')
        if idx != -1:
            text = text[:idx] + ADD_MODAL_HTML + '\n\n' + text[idx:]
            print('[ok] Added Add User modal with v5 version.')

    edit_pattern = re.compile(r'\n\s*<div class="user-edit-modal[^>]*data-user-edit-modal.*?</div>\s*</div>', re.DOTALL)
    if edit_pattern.search(text):
        text = edit_pattern.sub('\n' + EDIT_MODAL_HTML, text, count=1)
        print('[ok] Replaced Edit User modal with v5 version.')
    else:
        idx = text.find('</body>')
        if idx != -1:
            text = text[:idx] + EDIT_MODAL_HTML + '\n' + text[idx:]
            print('[ok] Added Edit User modal with v5 version.')
    return text


def ensure_toolbar_button_markup(text: str) -> str:
    if 'data-user-add-open' in text:
        return text
    text2 = re.sub(
        r'(<button[^>]+data-users-refresh[^>]*>Refresh Users</button>)',
        r'\1\n              <button class="admin-button" type="button" data-user-add-open>Add User</button>',
        text,
        count=1,
    )
    if text2 != text:
        print('[ok] Added Add User toolbar button.')
    return text2


def patch_settings_html() -> None:
    if not SETTINGS_HTML.exists():
        raise SystemExit(f"[fail] Missing {rel(SETTINGS_HTML)}")
    text = read(SETTINGS_HTML)
    text = ensure_fontawesome(text)
    text = normalize_sidebar_icons(text)
    text = ensure_toolbar_button_markup(text)
    text = replace_or_insert_modals(text)
    write(SETTINGS_HTML, text)


def patch_js() -> None:
    if not ADMIN_JS.parent.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_JS.parent)}")
    write(ADMIN_JS, ADMIN_USERS_JS)


def patch_css() -> None:
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")
    text = read(ADMIN_CSS)
    if MARKER not in text:
        text = text.rstrip() + CSS_APPEND
        write(ADMIN_CSS, text)
    else:
        print(f"[skip] CSS marker already present in {rel(ADMIN_CSS)}")


def main() -> None:
    print(f"[start] Applying {MARKER}")
    patch_settings_html()
    patch_js()
    patch_css()
    write(DOC, DOC_TEXT)
    print(f"[done] {MARKER} applied.")
    print('[done] Users status moved to toolbar-left, actions stay right, modal spacing/feedback normalized.')
    print('[done] No Cognito/IAM/backend/DynamoDB/EC2 change.')


if __name__ == '__main__':
    main()
