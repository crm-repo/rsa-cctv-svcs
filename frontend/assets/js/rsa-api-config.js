/*
 * RSA CMS / Mini-CRM public API configuration
 * Phase 8 Batch 9
 *
 * This file is safe for the static frontend. It only defines configuration and
 * does not fetch or render anything by itself.
 */
(function configureRsaApi(global) {
  "use strict";

  const currentScript = document.currentScript;

  function getScriptData(name, fallback) {
    if (!currentScript || !currentScript.dataset) {
      return fallback;
    }
    return currentScript.dataset[name] || fallback;
  }

  function trimTrailingSlash(value) {
    return String(value || "").replace(/\/+$/, "");
  }

  const existingConfig = global.RSA_API_CONFIG || {};
  const localStorageApiBase = (() => {
    try {
      return global.localStorage ? global.localStorage.getItem("rsaApiBaseUrl") : null;
    } catch (_error) {
      return null;
    }
  })();

  const apiBaseUrl = trimTrailingSlash(
    existingConfig.apiBaseUrl ||
      global.RSA_API_BASE_URL ||
      localStorageApiBase ||
      getScriptData("apiBaseUrl", "http://127.0.0.1:8000/api")
  );

  global.RSA_API_CONFIG = {
    apiBaseUrl,
    timeoutMs: Number(existingConfig.timeoutMs || getScriptData("timeoutMs", 12000)),
    currency: existingConfig.currency || getScriptData("currency", "PHP"),
    currencyLocale: existingConfig.currencyLocale || getScriptData("currencyLocale", "en-PH"),
    imageFallback: existingConfig.imageFallback || getScriptData("imageFallback", "assets/images/placeholder-product.png"),
    debug: Boolean(existingConfig.debug || global.RSA_API_DEBUG || false),
  };
})(window);
