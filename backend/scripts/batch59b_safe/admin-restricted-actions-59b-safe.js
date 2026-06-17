(function () {
  'use strict';

  const MARKER = 'batch59b-safe-admin-only-restricted-actions';
  const ACCESS_TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';

  function decodeJwt(token) {
    try {
      const parts = String(token || '').split('.');
      if (parts.length < 2) return {};
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
      return JSON.parse(atob(padded));
    } catch (error) {
      return {};
    }
  }

  function getGroups() {
    const access = decodeJwt(window.localStorage.getItem(ACCESS_TOKEN_KEY));
    const id = decodeJwt(window.localStorage.getItem(ID_TOKEN_KEY));
    const groups = access['cognito:groups'] || id['cognito:groups'] || [];
    return Array.isArray(groups) ? groups : [];
  }

  function rawRoleFromGroups() {
    const groups = getGroups();
    if (groups.includes('Admin')) return 'Admin';
    if (groups.includes('Standard')) return 'Standard';
    return 'No role';
  }

  function isAdmin() {
    return rawRoleFromGroups() === 'Admin';
  }

  function textOf(el) {
    return String(el && el.textContent ? el.textContent : '').replace(/\s+/g, ' ').trim();
  }

  function hideElement(el) {
    if (!el || el.dataset.batch59bHidden === '1') return;
    el.dataset.batch59bHidden = '1';
    el.hidden = true;
    el.setAttribute('aria-hidden', 'true');
    el.style.display = 'none';
  }

  function markRole() {
    const admin = isAdmin();
    document.documentElement.classList.toggle('rsa-role-admin', admin);
    document.documentElement.classList.toggle('rsa-role-standard', !admin);
    document.documentElement.setAttribute('data-rsa-current-role', rawRoleFromGroups());
  }

  function hideSettingsForStandard() {
    if (isAdmin()) return;
    document.querySelectorAll('a[href$="settings.html"], a[href*="/settings.html"], [data-nav-settings]').forEach(hideElement);
  }

  function hideDestructiveControlsForStandard() {
    if (isAdmin()) return;

    const selectorList = [
      '[data-admin-only]',
      '[data-requires-admin]',
      '[data-restricted-admin]',
      '[data-delete-action]',
      '[data-action="delete"]',
      '[data-action="remove"]',
      '[data-action="destroy"]',
      '.admin-only',
      '.requires-admin',
      '.restricted-admin',
      '.delete-btn',
      '.btn-delete',
      '.js-delete',
      '.js-remove',
      '.danger-action'
    ];

    document.querySelectorAll(selectorList.join(',')).forEach(hideElement);

    document.querySelectorAll('button, a, [role="button"]').forEach((el) => {
      const label = `${textOf(el)} ${el.getAttribute('aria-label') || ''} ${el.getAttribute('title') || ''}`.toLowerCase();
      if (/\b(delete|remove|trash|destroy)\b/.test(label)) {
        hideElement(el);
      }
    });
  }

  function applyRestrictedActionGuard() {
    markRole();
    hideSettingsForStandard();
    hideDestructiveControlsForStandard();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyRestrictedActionGuard);
  } else {
    applyRestrictedActionGuard();
  }

  [50, 150, 350, 900, 1800].forEach((delay) => setTimeout(applyRestrictedActionGuard, delay));

  const observer = new MutationObserver(() => applyRestrictedActionGuard());
  observer.observe(document.documentElement, { childList: true, subtree: true });

  window.RSABatch59BRestrictedActions = {
    marker: MARKER,
    rawRoleFromGroups,
    isAdmin,
    applyRestrictedActionGuard
  };
}());
