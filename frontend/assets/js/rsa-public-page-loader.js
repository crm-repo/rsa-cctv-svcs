/*
 * RSA CMS / Mini-CRM public page API loader
 * Phase 8 Batch 10
 *
 * This file prepares public pages to render API data. It is safe by default:
 * - If pages have data-rsa-* containers, it hydrates those containers.
 * - If pages do not have containers, it does nothing unless preview mode is enabled.
 * - Preview mode is enabled by adding ?rsaApiPreview=1 or setting data-preview="true"
 *   on this script tag.
 */
(function loadRsaPublicPages(global) {
  "use strict";

  const renderers = global.RsaPublicRenderers;
  const currentScript = document.currentScript;

  function getScriptFlag(name) {
    return Boolean(currentScript && currentScript.dataset && currentScript.dataset[name] === "true");
  }

  function getQueryFlag(name) {
    try {
      return new URLSearchParams(global.location.search).get(name) === "1";
    } catch (_error) {
      return false;
    }
  }

  function getPageName() {
    const path = String(global.location.pathname || "").toLowerCase();
    if (path.includes("promotions")) return "promotions";
    if (path.includes("products")) return "products";
    if (path.includes("brands")) return "brands";
    if (path.includes("about")) return "about";
    if (path.includes("services")) return "services";
    if (path.includes("contact-us") || path.includes("contact")) return "contact";
    if (path.includes("booking")) return "booking";
    if (path.endsWith("/") || path.includes("index")) return "home";
    return "unknown";
  }

  function createSection(options) {
    const settings = options || {};
    const section = document.createElement("section");
    section.className = "rsa-api-section";
    section.dataset.rsaApiPreviewSection = "true";
    section.innerHTML = `
      <div class="rsa-api-section__header">
        <div>
          <p class="rsa-api-section__eyebrow">API preview</p>
          <h2 class="rsa-api-section__title">${settings.title || "API-connected content"}</h2>
          <p class="rsa-api-section__subtitle">${settings.subtitle || "Loaded from FastAPI mock APIs. Existing static content remains available as fallback."}</p>
        </div>
        <div class="rsa-api-status" data-status="info" ${settings.statusAttr || ""}>Ready</div>
      </div>
      <div class="rsa-api-grid" ${settings.containerAttr || ""}></div>
    `;
    return section;
  }

  function insertPreviewSection(section) {
    const main = document.querySelector("main");
    const target = main || document.body;
    if (main && main.firstElementChild) {
      main.insertBefore(section, main.firstElementChild.nextSibling);
      return;
    }
    target.appendChild(section);
  }

  function ensureHookForPage(pageName) {
    if (!renderers) {
      return;
    }

    const previewEnabled = getScriptFlag("preview") || getQueryFlag("rsaApiPreview");
    if (!previewEnabled) {
      return;
    }

    if (document.querySelector("[data-rsa-api-preview-section]")) {
      return;
    }

    if (pageName === "products") {
      const section = createSection({
        title: "Products loaded from API",
        subtitle: "Preview of GET /api/products. Static catalog stays untouched until final page replacement.",
        statusAttr: "data-rsa-products-status",
        containerAttr: "data-rsa-products-container data-rsa-per-page=\"12\"",
      });
      insertPreviewSection(section);
      return;
    }

    if (pageName === "promotions") {
      const section = createSection({
        title: "Promotions loaded from API",
        subtitle: "Preview of sale-only GET /api/products?sale=true. Promotions sale hard filter is preserved.",
        statusAttr: "data-rsa-products-status",
        containerAttr: "data-rsa-products-container data-rsa-sale=\"true\" data-rsa-per-page=\"12\"",
      });
      insertPreviewSection(section);
      return;
    }

    if (pageName === "brands") {
      const section = createSection({
        title: "Brands loaded from API",
        subtitle: "Preview of GET /api/brands. Existing brand strip remains untouched.",
        statusAttr: "data-rsa-brands-status",
        containerAttr: "data-rsa-brands-container",
      });
      insertPreviewSection(section);
      return;
    }

    if (pageName === "services") {
      const section = createSection({
        title: "Services loaded from API",
        subtitle: "Preview of GET /api/pages/services.",
        statusAttr: "data-rsa-services-status",
        containerAttr: "data-rsa-services-container",
      });
      insertPreviewSection(section);
      return;
    }

    if (pageName === "about") {
      const section = createSection({
        title: "About Us loaded from API",
        subtitle: "Preview of GET /api/pages/about.",
        statusAttr: "data-rsa-about-status",
        containerAttr: "data-rsa-about-container",
      });
      insertPreviewSection(section);
      return;
    }

    if (pageName === "contact") {
      const section = createSection({
        title: "Contact Us loaded from API",
        subtitle: "Preview of GET /api/pages/contact using the consolidated rsa_contact_us structure.",
        statusAttr: "data-rsa-contact-status",
        containerAttr: "data-rsa-contact-container",
      });
      insertPreviewSection(section);
    }
  }

  function hydrateExistingHooks() {
    if (!renderers) {
      return;
    }

    const productContainer = document.querySelector("[data-rsa-products-container]");
    if (productContainer && productContainer.dataset.rsaApiLoaded !== "true") {
      productContainer.dataset.rsaApiLoaded = "true";
      renderers.hydrateProductGrid({
        container: productContainer,
        status: document.querySelector("[data-rsa-products-status]"),
      });
    }

    const brandContainer = document.querySelector("[data-rsa-brands-container]");
    if (brandContainer && brandContainer.dataset.rsaApiLoaded !== "true") {
      brandContainer.dataset.rsaApiLoaded = "true";
      renderers.hydrateBrands(brandContainer, document.querySelector("[data-rsa-brands-status]"));
    }

    const serviceContainer = document.querySelector("[data-rsa-services-container]");
    if (serviceContainer && serviceContainer.dataset.rsaApiLoaded !== "true") {
      serviceContainer.dataset.rsaApiLoaded = "true";
      renderers.hydrateServices(serviceContainer, document.querySelector("[data-rsa-services-status]"));
    }

    const aboutContainer = document.querySelector("[data-rsa-about-container]");
    if (aboutContainer && aboutContainer.dataset.rsaApiLoaded !== "true") {
      aboutContainer.dataset.rsaApiLoaded = "true";
      renderers.hydrateAbout(aboutContainer, document.querySelector("[data-rsa-about-status]"));
    }

    const contactContainer = document.querySelector("[data-rsa-contact-container]");
    if (contactContainer && contactContainer.dataset.rsaApiLoaded !== "true") {
      contactContainer.dataset.rsaApiLoaded = "true";
      renderers.hydrateContact(contactContainer, document.querySelector("[data-rsa-contact-status]"));
    }

    renderers.bindLeadForms();
  }

  document.addEventListener("DOMContentLoaded", () => {
    const pageName = getPageName();
    ensureHookForPage(pageName);
    hydrateExistingHooks();
  });
})(window);
