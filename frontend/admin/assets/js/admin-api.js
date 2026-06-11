(function () {
  'use strict';

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

  function getAuthHeaders() {
    if (window.RSAAdminAuth && typeof window.RSAAdminAuth.getAuthHeader === 'function') {
      return window.RSAAdminAuth.getAuthHeader();
    }

    const token = window.localStorage.getItem('rsa_admin_access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function request(path, options = {}) {
    const base = getApiBaseUrl();
    const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
    const response = await fetch(url, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
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

  function getItems(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== 'object') return [];
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.data)) return payload.data;
    if (Array.isArray(payload.results)) return payload.results;
    return [];
  }

  function getCount(payload) {
    if (Array.isArray(payload)) return payload.length;
    if (!payload || typeof payload !== 'object') return 0;
    if (typeof payload.total === 'number') return payload.total;
    if (typeof payload.count === 'number') return payload.count;
    return getItems(payload).length;
  }

  async function postJson(path, payload) {
    return request(path, {
      method: 'POST',
      body: JSON.stringify(payload || {})
    });
  }

  async function putJson(path, payload) {
    return request(path, {
      method: 'PUT',
      body: JSON.stringify(payload || {})
    });
  }

  window.RSAAdminApi = {
    getApiBaseUrl,
    request,
    postJson,
    putJson,
    getItems,
    getCount,
    getAuthHeaders,
    endpoints: {
      products: '/products',
      brands: '/brands',
      bookings: '/bookings',
      inquiries: '/inquiries',
      customers: '/customers',
      categories: '/categories',
      keyFeatures: '/key-features',
      pagesAbout: '/pages/about',
      pagesServices: '/pages/services',
      pagesContact: '/pages/contact',
      adminAbout: '/admin/about',
      adminProjectGallery: '/admin/project-gallery',
      adminServices: '/admin/services',
      adminContactUs: '/admin/contact-us'
    }
  };
}());
