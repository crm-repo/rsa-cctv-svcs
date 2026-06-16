(function () {
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
