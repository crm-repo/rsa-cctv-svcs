(function () {
  'use strict';

  const BATCH55C_HOTFIX_V2_VERSION = 'batch55c-hotfix-v2-admin-polish-corrections';
  window.RSA_BATCH55C_AUTH_HOTFIX_V2_VERSION = BATCH55C_HOTFIX_V2_VERSION;

  const TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';
  const REFRESH_TOKEN_KEY = 'rsa_admin_refresh_token';
  const MODE_KEY = 'rsa_admin_auth_mode';
  const LOGGED_OUT_KEY = 'rsa_admin_logged_out';
  const DEFAULT_API_BASE = 'http://127.0.0.1:8000/api';

  function normalizeBaseUrl(value) {
    return String(value || DEFAULT_API_BASE).replace(/\/$/, '');
  }

  function getApiBaseUrl() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('apiBase');
    if (fromQuery) return normalizeBaseUrl(fromQuery);

    if (window.RSA_ADMIN_API_BASE_URL) return normalizeBaseUrl(window.RSA_ADMIN_API_BASE_URL);

    const host = window.location.hostname;
    if (host === '127.0.0.1' || host === 'localhost' || !host) {
      return DEFAULT_API_BASE;
    }

    return normalizeBaseUrl(`${window.location.origin}/api`);
  }

  function getToken() {
    return window.localStorage.getItem(TOKEN_KEY) || '';
  }

  function setToken(token) {
    if (!token) {
      window.localStorage.removeItem(TOKEN_KEY);
      return;
    }
    window.localStorage.setItem(TOKEN_KEY, token);
  }

  function setCognitoTokens(result) {
    setToken(result.access_token || '');

    if (result.id_token) {
      window.localStorage.setItem(ID_TOKEN_KEY, result.id_token);
    }

    if (result.refresh_token) {
      window.localStorage.setItem(REFRESH_TOKEN_KEY, result.refresh_token);
    }
  }

  function clearToken() {
    const explicitKeys = [TOKEN_KEY, ID_TOKEN_KEY, REFRESH_TOKEN_KEY, MODE_KEY];
    explicitKeys.forEach((key) => {
      window.localStorage.removeItem(key);
      window.sessionStorage.removeItem(key);
    });

    [window.localStorage, window.sessionStorage].forEach((store) => {
      Object.keys(store).forEach((key) => {
        const normalized = String(key || '').toLowerCase();
        if (normalized.includes('rsa_admin') || normalized.includes('cognito') || normalized.includes('amplify') || normalized.includes('admin_auth')) {
          store.removeItem(key);
        }
      });
    });
  }

  function getAuthHeader() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function isLoginPage() {
    return /\/admin\/login\.html$/.test(window.location.pathname) || /\/admin\/login$/.test(window.location.pathname);
  }

  function showAuthBadge(config) {
    return;
    const badge = document.createElement('div');
    badge.className = 'admin-auth-dev-badge';
    badge.setAttribute('data-admin-auth-badge', 'true');

    if (!config || config.mode === 'disabled') {
      badge.textContent = 'Admin mode';
    } else if (config.mode === 'mock') {
      badge.textContent = 'Admin auth mode';
    } else if (config.mode === 'cognito') {
      badge.textContent = config.is_cognito_configured ? 'Cognito admin auth mode' : 'Cognito config incomplete';
    } else {
      badge.textContent = 'Admin auth';
    }

    document.body.appendChild(badge);
  }

  async function fetchJson(path, options = {}) {
    const base = getApiBaseUrl();
    const response = await fetch(`${base}${path}`, {
      headers: {
        Accept: 'application/json',
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

  async function loadConfig() {
    try {
      const config = await fetchJson('/admin/auth/config');
      window.localStorage.setItem(MODE_KEY, config.mode || 'disabled');
      window.RSAAdminAuth.config = config;
      return config;
    } catch (error) {
      window.RSAAdminAuth.configError = error;
      return {
        enabled: false,
        mode: 'disabled',
        safety_note: 'Auth config endpoint unavailable; local admin mode is active.'
      };
    }
  }

  async function checkStatus() {
    try {
      const status = await fetchJson('/admin/auth/status', {
        headers: {
          ...getAuthHeader()
        }
      });
      window.RSAAdminAuth.status = status;
      return status;
    } catch (error) {
      window.RSAAdminAuth.statusError = error;
      return {
        authenticated: false,
        error: error.message
      };
    }
  }

  async function initGuard() {
    const config = await loadConfig();

    if (!document.querySelector('[data-admin-auth-badge]')) {
      showAuthBadge(config);
    }

    if (!config.enabled || config.mode === 'disabled') {
      if (!isLoginPage() && window.localStorage.getItem(LOGGED_OUT_KEY) === '1') {
        window.location.href = './login.html?logged_out=1';
        return { allowed: false, config };
      }
      return { allowed: true, config };
    }

    const status = await checkStatus();

    if (!status.authenticated && !isLoginPage()) {
      const current = encodeURIComponent(window.location.href);
      window.location.href = `./login.html?next=${current}`;
      return { allowed: false, config, status };
    }

    return { allowed: status.authenticated || isLoginPage(), config, status };
  }

  async function mockLogin(token) {
    const result = await fetchJson('/admin/auth/mock-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token })
    });

    setToken(result.access_token || token);
    return result;
  }

  async function cognitoLogin(username, password) {
    const result = await fetchJson('/admin/auth/cognito-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });

    if (!result.challenge_required) {
      setCognitoTokens(result);
    }

    return result;
  }

  async function cognitoCompleteNewPassword(username, newPassword, session) {
    const result = await fetchJson('/admin/auth/cognito-complete-new-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, new_password: newPassword, session })
    });

    if (!result.challenge_required) {
      setCognitoTokens(result);
    }

    return result;
  }

  window.RSAAdminAuth = {
    TOKEN_KEY,
    ID_TOKEN_KEY,
    REFRESH_TOKEN_KEY,
    getApiBaseUrl,
    getToken,
    setToken,
    clearToken,
    getAuthHeader,
    loadConfig,
    checkStatus,
    initGuard,
    mockLogin,
    cognitoLogin,
    cognitoCompleteNewPassword
  };

  document.addEventListener('DOMContentLoaded', () => {
    initGuard().catch((error) => {
      console.warn('Admin auth guard failed:', error);
    });

    document.addEventListener('click', (event) => {
      const logoutButton = event.target.closest('[data-admin-logout]');
      if (!logoutButton) return;
      event.preventDefault();
      clearToken();
      window.localStorage.setItem(LOGGED_OUT_KEY, '1');
      window.location.replace('./login.html?logged_out=1');
    });
  });
}());

// batch59a-hotfix-v7-users-drawer-temp-password-role-guard

(function () {
  'use strict';

  const ACCESS_TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';

  function isSettingsPage() {
    return /\/admin\/settings\.html$/.test(window.location.pathname) || /\/admin\/settings$/.test(window.location.pathname);
  }

  if (isSettingsPage()) {
    document.documentElement.classList.add('rsa-auth-pending-settings');
  }

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

  function isAdmin() {
    return getGroups().includes('Admin');
  }

  function hideSettingsNavigation() {
    document.querySelectorAll('a[href$="settings.html"], a[href*="/settings.html"], [data-nav-settings]').forEach((item) => {
      item.hidden = true;
      item.setAttribute('aria-hidden', 'true');
      item.style.display = 'none';
    });
  }

  function applyRoleGuard() {
    const admin = isAdmin();
    document.documentElement.classList.toggle('rsa-role-admin', admin);
    document.documentElement.classList.toggle('rsa-role-standard', !admin);

    if (!admin) hideSettingsNavigation();

    if (isSettingsPage()) {
      if (!admin) {
        window.location.replace('./dashboard.html?adminOnly=settings');
        return;
      }
      document.documentElement.classList.remove('rsa-auth-pending-settings');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyRoleGuard);
  } else {
    applyRoleGuard();
  }
  window.addEventListener('storage', applyRoleGuard);
  setTimeout(applyRoleGuard, 150);
  setTimeout(applyRoleGuard, 650);
}());

// batch59a-hotfix-v8-users-role-temp-password-reset
(function () {
  'use strict';

  const MARKER = 'batch59a-hotfix-v8-users-role-temp-password-reset';
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

  function roleFromGroups() {
    const groups = groupsFromClaims();
    if (groups.includes('Admin')) return 'Admin';
    if (groups.includes('Standard')) return 'Standard';
    return 'No role';
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

  function hideSettingsForStandard(role) {
    const isAdmin = role === 'Admin';
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
    const role = roleFromGroups();
    const name = nameFromClaims();
    hideSettingsForStandard(role);

    document.querySelectorAll('.admin-avatar, .admin-user-card').forEach((card) => {
      const strong = card.querySelector('strong');
      const small = card.querySelector('small');
      const initials = card.querySelector('span, .avatar-initials');
      if (strong) strong.textContent = name;
      if (small) small.textContent = role;
      if (initials && initials.children.length === 0) initials.textContent = initialsFromName(name);
      card.setAttribute('data-cognito-role', role);
      card.setAttribute('title', `${name} · ${role}`);
    });

    document.querySelectorAll('[data-admin-role]:not(body), [data-settings-admin-role]').forEach((el) => {
      el.textContent = role;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncTopbarRole);
  } else {
    syncTopbarRole();
  }
  [100, 350, 900, 1800].forEach((delay) => setTimeout(syncTopbarRole, delay));
  window.RSAHotfix59ATopbarRoleV8 = { marker: MARKER, syncTopbarRole, roleFromGroups };
}());

// batch59a-hotfix-v9-users-role-labels-reset-spacing
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

    document.querySelectorAll('[data-admin-role]:not(body), [data-settings-admin-role]').forEach((el) => {
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

/* batch60a-precheck-hotfix-v2-admin-role-label-selector-not-body: role label updater no longer targets body[data-admin-role]. */
