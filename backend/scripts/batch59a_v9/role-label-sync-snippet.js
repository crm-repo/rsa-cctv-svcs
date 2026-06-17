
(function () {
  'use strict';

  const MARKER = 'batch59a-hotfix-v9-users-role-labels-reset-spacing';
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

  function claims() {
    const access = decodeJwt(window.localStorage.getItem(ACCESS_TOKEN_KEY));
    const id = decodeJwt(window.localStorage.getItem(ID_TOKEN_KEY));
    return { access, id };
  }

  function groupsFromClaims() {
    const c = claims();
    const groups = c.access['cognito:groups'] || c.id['cognito:groups'] || [];
    return Array.isArray(groups) ? groups : [];
  }

  function rawRoleFromGroups() {
    const groups = groupsFromClaims();
    if (groups.includes('Admin')) return 'Admin';
    if (groups.includes('Standard')) return 'Standard';
    return 'No role';
  }

  function roleLabel(role) {
    if (role === 'Admin') return 'System Administrator';
    if (role === 'Standard') return 'Standard User';
    return role || 'No role';
  }

  function nameFromClaims() {
    const c = claims();
    const source = c.id && Object.keys(c.id).length ? c.id : c.access;
    const fullName = source.name || [source.given_name, source.family_name].filter(Boolean).join(' ');
    return String(fullName || source.email || source.username || source['cognito:username'] || 'Admin User').trim();
  }

  function initialsFromName(name) {
    const clean = String(name || '').trim();
    if (!clean) return 'AD';
    const parts = clean.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return clean.slice(0, 2).toUpperCase();
  }

  function hideSettingsForStandard(rawRole) {
    const isAdmin = rawRole === 'Admin';
    document.documentElement.classList.toggle('rsa-cognito-role-admin', isAdmin);
    document.documentElement.classList.toggle('rsa-cognito-role-standard', !isAdmin);
    if (isAdmin) return;
    document.querySelectorAll('a[href$="settings.html"], a[href*="/settings.html"], [data-nav-settings]').forEach((item) => {
      item.hidden = true;
      item.setAttribute('aria-hidden', 'true');
      item.style.display = 'none';
    });
  }

  function syncTopbarRole() {
    const rawRole = rawRoleFromGroups();
    const displayRole = roleLabel(rawRole);
    const name = nameFromClaims();
    hideSettingsForStandard(rawRole);

    document.querySelectorAll('.admin-avatar, .admin-user-card').forEach((card) => {
      const strong = card.querySelector('strong');
      const small = card.querySelector('small');
      const initials = card.querySelector('span, .avatar-initials');
      if (strong) strong.textContent = name;
      if (small) small.textContent = displayRole;
      if (initials && initials.children.length === 0) initials.textContent = initialsFromName(name);
      card.setAttribute('data-cognito-role', rawRole);
      card.setAttribute('title', `${name} · ${displayRole}`);
    });

    document.querySelectorAll('[data-admin-role], [data-settings-admin-role]').forEach((el) => {
      el.textContent = displayRole;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncTopbarRole);
  } else {
    syncTopbarRole();
  }
  [50, 150, 350, 900, 1800].forEach((delay) => setTimeout(syncTopbarRole, delay));
  window.RSAHotfix59ATopbarRoleV9 = { marker: MARKER, syncTopbarRole, rawRoleFromGroups, roleLabel };
}());
