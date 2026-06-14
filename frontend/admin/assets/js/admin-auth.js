(function () {
  'use strict';

  const TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';
  const REFRESH_TOKEN_KEY = 'rsa_admin_refresh_token';
  const MODE_KEY = 'rsa_admin_auth_mode';
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
    const badge = document.createElement('div');
    badge.className = 'admin-auth-dev-badge';
    badge.setAttribute('data-admin-auth-badge', 'true');

    if (!config || config.mode === 'disabled') {
      badge.textContent = 'Local admin mode';
    } else if (config.mode === 'mock') {
      badge.textContent = 'Mock admin auth mode';
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
      console.warn('Admin auth guard failed in local preview mode:', error);
    });

    document.addEventListener('click', (event) => {
      const logoutButton = event.target.closest('[data-admin-logout]');
      if (!logoutButton) return;
      event.preventDefault();
      clearToken();
      window.location.replace('./login.html?logged_out=1');
    });
  });
}());
