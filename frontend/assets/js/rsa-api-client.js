/*
 * RSA CMS / Mini-CRM public API client
 * Phase 8 Batch 9
 *
 * This file exposes window.RsaApiClient. It is intentionally dependency-free
 * and safe for static HTML pages. It does not run any request until a page or
 * smoke-test script calls one of the client methods.
 */
(function buildRsaApiClient(global) {
  "use strict";

  const config = global.RSA_API_CONFIG || {
    apiBaseUrl: "http://127.0.0.1:8000/api",
    timeoutMs: 12000,
  };

  function toQueryString(params) {
    const query = new URLSearchParams();

    Object.entries(params || {}).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        return;
      }
      query.set(key, String(value));
    });

    const serialized = query.toString();
    return serialized ? `?${serialized}` : "";
  }

  function buildUrl(path, params) {
    const normalizedPath = String(path || "").startsWith("/") ? path : `/${path}`;
    return `${config.apiBaseUrl}${normalizedPath}${toQueryString(params)}`;
  }

  function buildTimeoutSignal(timeoutMs) {
    if (!global.AbortController) {
      return { signal: undefined, cleanup: function noop() {} };
    }

    const controller = new AbortController();
    const timeoutId = global.setTimeout(() => controller.abort(), timeoutMs || config.timeoutMs || 12000);

    return {
      signal: controller.signal,
      cleanup: () => global.clearTimeout(timeoutId),
    };
  }

  async function request(path, options) {
    const requestOptions = options || {};
    const method = requestOptions.method || "GET";
    const params = requestOptions.params || {};
    const url = buildUrl(path, params);
    const timeout = buildTimeoutSignal(requestOptions.timeoutMs || config.timeoutMs);

    const headers = Object.assign(
      {
        Accept: "application/json",
      },
      requestOptions.headers || {}
    );

    const fetchOptions = {
      method,
      headers,
      signal: timeout.signal,
    };

    if (requestOptions.body !== undefined) {
      headers["Content-Type"] = "application/json";
      fetchOptions.body = JSON.stringify(requestOptions.body);
    }

    try {
      const response = await fetch(url, fetchOptions);
      const contentType = response.headers.get("content-type") || "";
      const payload = contentType.includes("application/json") ? await response.json() : await response.text();

      if (!response.ok) {
        const message = typeof payload === "object" && payload && payload.detail ? payload.detail : response.statusText;
        const error = new Error(message || `Request failed with status ${response.status}`);
        error.status = response.status;
        error.payload = payload;
        error.url = url;
        throw error;
      }

      return payload;
    } catch (error) {
      if (error && error.name === "AbortError") {
        const timeoutError = new Error(`Request timed out after ${requestOptions.timeoutMs || config.timeoutMs}ms`);
        timeoutError.url = url;
        throw timeoutError;
      }
      throw error;
    } finally {
      timeout.cleanup();
    }
  }

  function getItems(payload) {
    if (Array.isArray(payload)) {
      return payload;
    }
    if (payload && Array.isArray(payload.items)) {
      return payload.items;
    }
    return [];
  }

  global.RsaApiClient = {
    config,
    buildUrl,
    request,
    getItems,

    health: () => request("/health"),

    products: (params) => request("/products", { params }),
    product: (productId) => request(`/products/${encodeURIComponent(productId)}`),
    brands: () => request("/brands"),
    brand: (brandId) => request(`/brands/${encodeURIComponent(brandId)}`),
    brandByKey: (brandKey) => request(`/brands/key/${encodeURIComponent(brandKey)}`),
    categories: () => request("/categories"),
    keyFeatures: (params) => request("/key-features", { params }),
    packageBanners: () => request("/package-banners"),

    pageAbout: () => request("/pages/about"),
    pageContact: () => request("/pages/contact"),
    pageServices: () => request("/pages/services"),
    about: () => request("/about"),
    projectGallery: () => request("/project-gallery"),
    services: () => request("/services"),
    contact: () => request("/contact"),
    contactPersons: () => request("/contact-persons"),
    socialMedia: () => request("/social-media"),

    createBooking: (body) => request("/bookings", { method: "POST", body }),
    createInquiry: (body) => request("/inquiries", { method: "POST", body }),
  };
})(window);
