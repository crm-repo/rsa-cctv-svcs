(function () {
  'use strict';

  const VERSION = 'batch59a-hotfix-v9-users-role-labels-reset-spacing';
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

  function roleLabel(role) {
    if (role === 'Admin') return 'System Administrator';
    if (role === 'Standard') return 'Standard User';
    return role || 'Standard User';
  }

  function normalizeRoleOptionLabels() {
    qsa('select[name="role"] option').forEach((option) => {
      if (option.value === 'Admin') option.textContent = 'System Administrator';
      if (option.value === 'Standard') option.textContent = 'Standard User';
    });
  }

  function rolePill(role) {
    const isAdmin = role === 'Admin';
    return `<span class="users-role-pill ${isAdmin ? 'is-admin' : 'is-standard'}">${escapeHtml(roleLabel(role || 'Standard'))}</span>`;
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
      setPageStatus('is-success', 'Users loaded.', `${state.users.length} loaded.`);
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
    normalizeRoleOptionLabels();
    if (form.elements.role) form.elements.role.value = 'Standard';
    clearModalStatus('[data-user-add-status]');
    modal.hidden = false;
    document.body.classList.add('admin-modal-open');
    requestAnimationFrame(() => modal.classList.add('is-open'));
    setTimeout(() => form.elements.first_name && form.elements.first_name.focus(), 80);
  }

  function closeAddModal() {
    const modal = qs('[data-user-add-modal]');
    if (modal) {
      modal.classList.remove('is-open');
      modal.hidden = true;
    }
    document.body.classList.remove('admin-modal-open');
    clearModalStatus('[data-user-add-status]');
  }

  function openEdit(username) {
    const user = state.users.find((item) => item.username === username || item.email === username);
    const form = qs('[data-user-edit-form]');
    const modal = qs('[data-user-edit-modal]');
    if (!user || !form || !modal) return;
    state.editingUsername = user.username;
    normalizeRoleOptionLabels();
    form.elements.full_name.value = displayName(user);
    form.elements.role.value = user.role || 'Standard';
    form.elements.enabled.checked = user.enabled !== false;
    setText('[data-edit-user-email]', user.email || user.username || 'User');
    clearModalStatus('[data-user-edit-status]');
    modal.hidden = false;
    document.body.classList.add('admin-modal-open');
    requestAnimationFrame(() => modal.classList.add('is-open'));
  }

  function closeEdit() {
    state.editingUsername = '';
    const modal = qs('[data-user-edit-modal]');
    if (modal) {
      modal.classList.remove('is-open');
      modal.hidden = true;
    }
    document.body.classList.remove('admin-modal-open');
    clearModalStatus('[data-user-edit-status]');
  }

  function renderTempPasswordHtml(result) {
    const password = result && result.temporary_password ? String(result.temporary_password) : '';
    if (!password) return '';
    return `<div class="users-temp-password-inline"><span>Copy this now. It cannot be viewed again.</span><code>${escapeHtml(password)}</code><button type="button" data-copy-temp-password>Copy</button></div>`;
  }

  function showTempPasswordInModal(selector, result, title) {
    const card = qs(selector);
    if (!card) return;
    const html = renderTempPasswordHtml(result);
    if (!html) {
      setModalStatus(selector, 'is-success', title || 'User created.', 'No temporary password was returned.');
      return;
    }
    card.hidden = false;
    card.className = 'users-modal-status is-success';
    card.innerHTML = `<strong>${escapeHtml(title || 'User created.')}</strong>${html}`;
  }

  function showTempPasswordOnPage(result, title) {
    const panel = qs('[data-temp-password-panel]');
    if (panel) {
      panel.hidden = true;
      panel.innerHTML = '';
    }
    const html = renderTempPasswordHtml(result);
    if (!html) {
      setPageStatus('is-success', title || 'Temporary password generated.', '');
      return;
    }
    setPageStatus('is-success', title || 'Temporary password generated.', 'Copy it now.');
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
      showTempPasswordInModal('[data-user-add-status]', result, 'User created.');
      form.reset();
      if (form.elements.role) form.elements.role.value = payload.role || 'Standard';
      await loadUsers();
      setPageStatus('is-success', 'User created.', 'Copy it from the drawer.');
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

  function ensureResetModal() {
    let modal = qs('[data-user-reset-modal]');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.className = 'user-reset-modal admin-modal-overlay';
    modal.setAttribute('data-user-reset-modal', '');
    modal.setAttribute('data-admin-requires-admin', '');
    modal.setAttribute('aria-hidden', 'true');
    modal.hidden = true;
    modal.innerHTML = `
      <div class="user-reset-card admin-modal-card" role="dialog" aria-modal="true" aria-labelledby="user-reset-title">
        <button class="modal-close" type="button" data-user-reset-close aria-label="Close">&times;</button>
        <p class="eyebrow">Reset Password</p>
        <h2 id="user-reset-title">Reset Password</h2>
        <p class="settings-note" data-user-reset-copy>Generate a new temporary password. It will be shown here once only.</p>
        <div class="users-modal-status" data-user-reset-status hidden></div>
        <div class="drawer-actions">
          <button class="admin-button secondary" type="button" data-user-reset-close>Close</button>
        </div>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', (event) => {
      if (event.target === modal || event.target.closest('[data-user-reset-close]')) {
        closeResetModal();
      }
    });
    return modal;
  }

  function openResetModal(username) {
    const modal = ensureResetModal();
    const title = qs('#user-reset-title', modal);
    if (title) title.textContent = 'Reset Password';
    clearModalStatus('[data-user-reset-status]');
    modal.dataset.username = username || '';
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('admin-modal-open');
    requestAnimationFrame(() => modal.classList.add('is-open'));
    return modal;
  }

  function closeResetModal() {
    const modal = qs('[data-user-reset-modal]');
    if (modal) {
      modal.classList.remove('is-open');
      modal.hidden = true;
      modal.setAttribute('aria-hidden', 'true');
      modal.dataset.username = '';
    }
    if (!qs('[data-user-add-modal].is-open') && !qs('[data-user-edit-modal].is-open')) {
      document.body.classList.remove('admin-modal-open');
    }
    clearModalStatus('[data-user-reset-status]');
  }

  async function resetPassword(username) {
    const user = state.users.find((item) => item.username === username || item.email === username);
    const label = user ? (user.email || user.username || 'this user') : 'this user';
    if (!confirm(`Generate a new temporary password for ${label}?`)) return;
    openResetModal(username);
    setModalStatus('[data-user-reset-status]', '', 'Resetting password…', '');
    try {
      const result = await request(`/admin/users/${encodeURIComponent(username)}/reset-password`, { method: 'POST' });
      showTempPasswordInModal('[data-user-reset-status]', result, 'Temporary password generated.');
      await loadUsers();
      setPageStatus('is-success', 'Password reset.', 'Copy it from the drawer.');
    } catch (error) {
      console.error(error);
      setModalStatus('[data-user-reset-status]', 'is-warning', 'Unable to reset password.', parseErrorMessage(error));
      setPageStatus('is-warning', 'Password reset failed.', 'See the reset password drawer.');
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
    normalizeRoleOptionLabels();
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
      const root = event.target.closest('.users-modal-status, .users-inline-status, [data-temp-password-panel]') || document;
      const code = qs('code', root) || qs('[data-temp-password-panel] code');
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
      if (qs('[data-user-add-modal].is-open')) closeAddModal();
      if (qs('[data-user-edit-modal].is-open')) closeEdit();
      if (qs('[data-user-reset-modal].is-open')) closeResetModal();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const usersCard = qs('[data-settings-users]');
    if (!usersCard) return;
    bind();
    loadUsers();
  });
})();
