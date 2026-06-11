/*
 * RSA CMS / Mini-CRM public frontend render helpers
 * Phase 8 Batch 11
 *
 * These helpers are dependency-free and scoped to RSA API integration classes.
 * Existing static pages remain safe unless a page explicitly adds data-rsa-* hooks
 * or the Batch 10 preview loader is enabled.
 */
(function buildRsaPublicRenderers(global) {
  "use strict";

  const api = global.RsaApiClient;
  const config = global.RSA_API_CONFIG || {};

  function escapeHtml(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatPrice(value) {
    if (value === undefined || value === null || value === "") {
      return "";
    }

    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) {
      return escapeHtml(value);
    }

    try {
      return new Intl.NumberFormat(config.currencyLocale || "en-PH", {
        style: "currency",
        currency: config.currency || "PHP",
        maximumFractionDigits: 0,
      }).format(numericValue);
    } catch (_error) {
      return `₱${numericValue.toLocaleString("en-PH")}`;
    }
  }

  function collectFeatures(product) {
    const features = [];
    for (let index = 1; index <= 10; index += 1) {
      const key = `feature_${String(index).padStart(2, "0")}`;
      if (product[key]) {
        features.push(product[key]);
      }
    }
    return features;
  }

  function toArray(payload) {
    if (!api) {
      return [];
    }
    return api.getItems ? api.getItems(payload) : Array.isArray(payload) ? payload : payload && payload.items ? payload.items : [];
  }

  function setStatus(element, message, type) {
    if (!element) {
      return;
    }
    element.textContent = message || "";
    element.dataset.status = type || "info";
  }

  function productCardHtml(product) {
    const salePrice = product.sale_price;
    const isOnSale = salePrice !== null && salePrice !== undefined && salePrice !== "";
    const features = collectFeatures(product).slice(0, 4);
    const imagePath = product.image_path || config.imageFallback || "assets/images/placeholder-product.png";
    const brandName = product.product_brand_name || product.category_name || "RSA";

    return `
      <article class="rsa-api-product-card" data-product-id="${escapeHtml(product.product_id)}" data-category="${escapeHtml(product.category_key)}" data-brand="${escapeHtml(product.product_brand_key)}">
        <div class="rsa-api-product-card__image-wrap">
          ${isOnSale ? '<span class="rsa-api-product-card__badge">Sale</span>' : ""}
          <img class="rsa-api-product-card__image" src="${escapeHtml(imagePath)}" alt="${escapeHtml(product.product_name)}" loading="lazy">
        </div>
        <div class="rsa-api-product-card__body">
          <p class="rsa-api-product-card__brand">${escapeHtml(brandName)}</p>
          <h3 class="rsa-api-product-card__title">${escapeHtml(product.product_name)}</h3>
          ${product.product_model ? `<p class="rsa-api-product-card__model">Model: ${escapeHtml(product.product_model)}</p>` : ""}
          ${features.length ? `<ul class="rsa-api-product-card__features">${features.map((feature) => `<li>${escapeHtml(feature)}</li>`).join("")}</ul>` : ""}
          <div class="rsa-api-product-card__footer">
            <div class="rsa-api-product-card__price">
              ${isOnSale ? `<span class="rsa-api-product-card__price-sale">${escapeHtml(formatPrice(salePrice))}</span><span class="rsa-api-product-card__price-original">${escapeHtml(formatPrice(product.price))}</span>` : `<span>${escapeHtml(formatPrice(product.price))}</span>`}
            </div>
            <button class="rsa-api-product-card__button" type="button" data-rsa-product-inquiry="${escapeHtml(product.product_id)}">Inquire</button>
          </div>
        </div>
      </article>
    `;
  }

  function renderProducts(container, products) {
    if (!container) {
      return;
    }

    if (!products || !products.length) {
      container.innerHTML = '<div class="rsa-api-empty-state">No products found.</div>';
      return;
    }

    container.innerHTML = products.map(productCardHtml).join("");
  }

  function brandCardHtml(brand) {
    const logoPath = brand.logo_path || config.imageFallback || "assets/images/placeholder-product.png";
    return `
      <article class="rsa-api-brand-card" data-brand-key="${escapeHtml(brand.brand_key)}">
        <img class="rsa-api-brand-card__logo" src="${escapeHtml(logoPath)}" alt="${escapeHtml(brand.brand_name)} logo" loading="lazy">
        <div>
          <h3 class="rsa-api-brand-card__name">${escapeHtml(brand.brand_name)}</h3>
          <p class="rsa-api-brand-card__meta">${brand.featured_brand ? "Featured brand" : "Brand partner"}</p>
        </div>
      </article>
    `;
  }

  function renderBrands(container, brands) {
    if (!container) {
      return;
    }
    if (!brands || !brands.length) {
      container.innerHTML = '<div class="rsa-api-empty-state">No brands found.</div>';
      return;
    }
    container.innerHTML = brands.map(brandCardHtml).join("");
  }

  function serviceCardHtml(service) {
    return `
      <article class="rsa-api-service-card">
        <p class="rsa-api-service-card__eyebrow">${escapeHtml(service.service_slug || "service")}</p>
        <h3 class="rsa-api-service-card__title">${escapeHtml(service.service_title)}</h3>
        <p class="rsa-api-service-card__text">${escapeHtml(service.short_description || service.service_description || "")}</p>
        ${service.cta_url ? `<a class="rsa-api-button" href="${escapeHtml(service.cta_url)}">${escapeHtml(service.cta_label || "Learn more")}</a>` : ""}
      </article>
    `;
  }

  function renderServices(container, services) {
    if (!container) {
      return;
    }
    if (!services || !services.length) {
      container.innerHTML = '<div class="rsa-api-empty-state">No services found.</div>';
      return;
    }
    container.innerHTML = services.map(serviceCardHtml).join("");
  }

  function renderAbout(container, about, gallery) {
    if (!container) {
      return;
    }
    if (!about) {
      container.innerHTML = '<div class="rsa-api-empty-state">No About Us content found.</div>';
      return;
    }

    const whyBullets = [];
    for (let index = 1; index <= 6; index += 1) {
      const key = `why_choose_bullet_${String(index).padStart(2, "0")}`;
      if (about[key]) {
        whyBullets.push(about[key]);
      }
    }

    container.innerHTML = `
      <article class="rsa-api-info-card">
        <h3 class="rsa-api-info-card__title">${escapeHtml(about.hero_title || about.company_story_title || "About RSA")}</h3>
        <p class="rsa-api-info-card__text">${escapeHtml(about.hero_subtitle || about.company_story_body || "")}</p>
      </article>
      <article class="rsa-api-info-card">
        <h3 class="rsa-api-info-card__title">${escapeHtml(about.mission_title || "Mission")}</h3>
        <p class="rsa-api-info-card__text">${escapeHtml(about.mission_body || "")}</p>
      </article>
      <article class="rsa-api-info-card">
        <h3 class="rsa-api-info-card__title">${escapeHtml(about.vision_title || "Vision")}</h3>
        <p class="rsa-api-info-card__text">${escapeHtml(about.vision_body || "")}</p>
      </article>
      <article class="rsa-api-info-card">
        <h3 class="rsa-api-info-card__title">${escapeHtml(about.why_choose_title || "Why Choose RSA")}</h3>
        <ul class="rsa-api-list">
          ${whyBullets.map((bullet) => `<li>${escapeHtml(bullet)}</li>`).join("")}
        </ul>
      </article>
      ${gallery && gallery.length ? `<article class="rsa-api-info-card"><h3 class="rsa-api-info-card__title">Project Gallery Preview</h3><p class="rsa-api-info-card__text">${escapeHtml(gallery.length)} visible project gallery item(s) loaded from API.</p></article>` : ""}
    `;
  }

  function renderContact(container, contactPage) {
    if (!container) {
      return;
    }

    const company = contactPage && contactPage.company_contact ? contactPage.company_contact : {};
    const persons = contactPage && Array.isArray(contactPage.contact_persons) ? contactPage.contact_persons : [];
    const socials = contactPage && Array.isArray(contactPage.social_media) ? contactPage.social_media : [];

    container.innerHTML = `
      <div class="rsa-api-contact-grid">
        <article class="rsa-api-info-card">
          <h3 class="rsa-api-info-card__title">Company Contact</h3>
          <ul class="rsa-api-list">
            ${company.primary_contact_number ? `<li><strong>Primary:</strong> ${escapeHtml(company.primary_contact_number)}</li>` : ""}
            ${company.secondary_contact_number ? `<li><strong>Secondary:</strong> ${escapeHtml(company.secondary_contact_number)}</li>` : ""}
            ${company.company_email ? `<li><strong>Email:</strong> ${escapeHtml(company.company_email)}</li>` : ""}
            ${company.company_address ? `<li><strong>Office:</strong> ${escapeHtml(company.company_address)}</li>` : ""}
            ${company.showroom_address ? `<li><strong>Showroom:</strong> ${escapeHtml(company.showroom_address)}</li>` : ""}
            ${company.business_hours ? `<li><strong>Hours:</strong> ${escapeHtml(company.business_hours)}</li>` : ""}
          </ul>
        </article>
        <article class="rsa-api-info-card">
          <h3 class="rsa-api-info-card__title">Contact Persons</h3>
          <ul class="rsa-api-list">
            ${persons.length ? persons.map((person) => `<li><strong>${escapeHtml(person.person_name)}</strong><br>${escapeHtml(person.position_title || person.department || "")}${person.phone_number ? `<br>${escapeHtml(person.phone_number)}` : ""}</li>`).join("") : "<li>No public contact persons found.</li>"}
          </ul>
        </article>
        <article class="rsa-api-info-card">
          <h3 class="rsa-api-info-card__title">Social Media</h3>
          <ul class="rsa-api-list">
            ${socials.length ? socials.map((social) => `<li><strong>${escapeHtml(social.platform_name)}</strong><br>${escapeHtml(social.profile_url || "")}</li>`).join("") : "<li>No social media links found.</li>"}
          </ul>
        </article>
      </div>
    `;
  }

  async function hydrateProductGrid(options) {
    if (!api) {
      return;
    }

    const settings = options || {};
    const container = typeof settings.container === "string" ? document.querySelector(settings.container) : settings.container;
    const status = typeof settings.status === "string" ? document.querySelector(settings.status) : settings.status;

    if (!container) {
      return;
    }

    const params = Object.assign(
      {
        page: container.dataset.rsaPage || 1,
        per_page: container.dataset.rsaPerPage || 12,
      },
      settings.params || {}
    );

    if (container.dataset.rsaCategory) {
      params.category = container.dataset.rsaCategory;
    }
    if (container.dataset.rsaBrand) {
      params.brand = container.dataset.rsaBrand;
    }
    if (container.dataset.rsaSale === "true") {
      params.sale = true;
    }

    try {
      setStatus(status, "Loading products...", "loading");
      const payload = await api.products(params);
      const items = toArray(payload);
      renderProducts(container, items);
      setStatus(status, `Loaded ${payload.total || items.length} products.`, "success");
    } catch (error) {
      setStatus(status, `Could not load products from API. Static content can remain visible. ${error.message}`, "error");
      if (config.debug) {
        console.error(error);
      }
    }
  }

  async function hydrateBrands(container, status) {
    if (!api || !container) {
      return;
    }
    try {
      setStatus(status, "Loading brands...", "loading");
      const payload = await api.brands();
      const items = toArray(payload);
      renderBrands(container, items);
      setStatus(status, `Loaded ${items.length} brands.`, "success");
    } catch (error) {
      setStatus(status, `Could not load brands from API. ${error.message}`, "error");
    }
  }

  async function hydrateServices(container, status) {
    if (!api || !container) {
      return;
    }
    try {
      setStatus(status, "Loading services...", "loading");
      const payload = await api.pageServices();
      const services = payload && Array.isArray(payload.services) ? payload.services : toArray(payload);
      renderServices(container, services);
      setStatus(status, `Loaded ${services.length} services.`, "success");
    } catch (error) {
      setStatus(status, `Could not load services from API. ${error.message}`, "error");
    }
  }

  async function hydrateAbout(container, status) {
    if (!api || !container) {
      return;
    }
    try {
      setStatus(status, "Loading About Us content...", "loading");
      const payload = await api.pageAbout();
      renderAbout(container, payload.about, payload.project_gallery || []);
      setStatus(status, "Loaded About Us content.", "success");
    } catch (error) {
      setStatus(status, `Could not load About Us content from API. ${error.message}`, "error");
    }
  }

  async function hydrateContact(container, status) {
    if (!api || !container) {
      return;
    }
    try {
      setStatus(status, "Loading contact content...", "loading");
      const payload = await api.pageContact();
      renderContact(container, payload);
      setStatus(status, "Loaded Contact Us content.", "success");
    } catch (error) {
      setStatus(status, `Could not load Contact Us content from API. ${error.message}`, "error");
    }
  }

  function readFormValue(form, names) {
    for (const name of names) {
      let field = form.elements[name];
      if (!field && global.CSS && CSS.escape) {
        field = form.querySelector(`#${CSS.escape(name)}`);
      }
      if (!field) {
        field = form.querySelector(`[data-rsa-field="${name}"]`);
      }
      if (field && field.value !== undefined && String(field.value).trim() !== "") {
        return String(field.value).trim();
      }
    }
    return null;
  }

  function bookingPayloadFromForm(form) {
    return {
      customer_name: readFormValue(form, ["customer_name", "name", "full_name", "fullName"]),
      contact_number: readFormValue(form, ["contact_number", "phone", "mobile", "contactNumber"]),
      email: readFormValue(form, ["email", "email_address", "emailAddress"]),
      address: readFormValue(form, ["address", "site_address", "siteAddress"]),
      preferred_date: readFormValue(form, ["preferred_date", "preferredDate", "date"]),
      preferred_time: readFormValue(form, ["preferred_time", "preferredTime", "time"]),
      service_interest: readFormValue(form, ["service_interest", "service", "serviceInterest"]),
      notes: readFormValue(form, ["notes", "message", "details"]),
    };
  }

  function inquiryPayloadFromForm(form) {
    return {
      product_id: readFormValue(form, ["product_id", "productId"]),
      customer_name: readFormValue(form, ["customer_name", "name", "full_name", "fullName"]),
      contact_number: readFormValue(form, ["contact_number", "phone", "mobile", "contactNumber"]),
      email: readFormValue(form, ["email", "email_address", "emailAddress"]),
      subject: readFormValue(form, ["subject", "inquiry_subject", "inquirySubject"]),
      message: readFormValue(form, ["message", "notes", "details"]),
      source_page: readFormValue(form, ["source_page", "sourcePage"]),
    };
  }

  function removeEmptyValues(payload) {
    Object.keys(payload).forEach((key) => {
      if (payload[key] === null || payload[key] === undefined || payload[key] === "") {
        delete payload[key];
      }
    });
    return payload;
  }

  function bindLeadForms() {
    if (global.RsaLeadForms && typeof global.RsaLeadForms.bindAllLeadForms === "function") {
      global.RsaLeadForms.bindAllLeadForms();
      return;
    }

    if (!api) {
      return;
    }

    document.querySelectorAll("[data-rsa-booking-form]").forEach((form) => {
      if (form.dataset.rsaApiBound === "true") {
        return;
      }
      form.dataset.rsaApiBound = "true";
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const status = form.querySelector("[data-rsa-form-status]");
        try {
          setStatus(status, "Sending booking request...", "loading");
          const payload = removeEmptyValues(bookingPayloadFromForm(form));
          const result = await api.createBooking(payload);
          setStatus(status, `Booking request sent. Reference: ${result.booking_id || "received"}`, "success");
          form.reset();
        } catch (error) {
          setStatus(status, `Could not send booking request: ${error.message}`, "error");
        }
      });
    });

    document.querySelectorAll("[data-rsa-inquiry-form]").forEach((form) => {
      if (form.dataset.rsaApiBound === "true") {
        return;
      }
      form.dataset.rsaApiBound = "true";
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const status = form.querySelector("[data-rsa-form-status]");
        try {
          setStatus(status, "Sending inquiry...", "loading");
          const payload = removeEmptyValues(inquiryPayloadFromForm(form));
          const result = await api.createInquiry(payload);
          setStatus(status, `Inquiry sent. Reference: ${result.inquiry_id || "received"}`, "success");
          form.reset();
        } catch (error) {
          setStatus(status, `Could not send inquiry: ${error.message}`, "error");
        }
      });
    });
  }

  global.RsaPublicRenderers = {
    escapeHtml,
    formatPrice,
    collectFeatures,
    productCardHtml,
    renderProducts,
    brandCardHtml,
    renderBrands,
    serviceCardHtml,
    renderServices,
    renderAbout,
    renderContact,
    hydrateProductGrid,
    hydrateBrands,
    hydrateServices,
    hydrateAbout,
    hydrateContact,
    bindLeadForms,
    bookingPayloadFromForm,
    inquiryPayloadFromForm,
    setStatus,
  };

  document.addEventListener("DOMContentLoaded", () => {
    const productContainer = document.querySelector("[data-rsa-products-container]");
    if (productContainer) {
      hydrateProductGrid({
        container: productContainer,
        status: document.querySelector("[data-rsa-products-status]"),
      });
    }
    const brandContainer = document.querySelector("[data-rsa-brands-container]");
    if (brandContainer) {
      hydrateBrands(brandContainer, document.querySelector("[data-rsa-brands-status]"));
    }
    const serviceContainer = document.querySelector("[data-rsa-services-container]");
    if (serviceContainer) {
      hydrateServices(serviceContainer, document.querySelector("[data-rsa-services-status]"));
    }
    const aboutContainer = document.querySelector("[data-rsa-about-container]");
    if (aboutContainer) {
      hydrateAbout(aboutContainer, document.querySelector("[data-rsa-about-status]"));
    }
    const contactContainer = document.querySelector("[data-rsa-contact-container]");
    if (contactContainer) {
      hydrateContact(contactContainer, document.querySelector("[data-rsa-contact-status]"));
    }
    bindLeadForms();
  });
})(window);
