(function () {
  'use strict';

  const TOKEN_KEY = 'rsa_admin_access_token';
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
    if (host === '127.0.0.1' || host === 'localhost') {
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

  function clearToken() {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(MODE_KEY);
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
      badge.textContent = 'Local admin preview · auth disabled';
    } else if (config.mode === 'mock') {
      badge.textContent = 'Mock admin auth mode';
    } else if (config.mode === 'cognito') {
      badge.textContent = config.is_cognito_configured ? 'Cognito auth prepared' : 'Cognito config incomplete';
    } else {
      badge.textContent = 'Admin auth prep';
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
        safety_note: 'Auth config endpoint unavailable; local preview remains unblocked.'
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

  window.RSAAdminAuth = {
    TOKEN_KEY,
    getApiBaseUrl,
    getToken,
    setToken,
    clearToken,
    getAuthHeader,
    loadConfig,
    checkStatus,
    initGuard,
    mockLogin
  };

  document.addEventListener('DOMContentLoaded', () => {
    initGuard().catch((error) => {
      console.warn('Admin auth guard failed in local preview mode:', error);
    });

    document.addEventListener('click', (event) => {
      const logoutButton = event.target.closest('[data-admin-logout]');
      if (!logoutButton) return;
      clearToken();
      window.location.href = './login.html';
    });
  });
}());
