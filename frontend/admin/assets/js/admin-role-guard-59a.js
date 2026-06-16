(function () {
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
