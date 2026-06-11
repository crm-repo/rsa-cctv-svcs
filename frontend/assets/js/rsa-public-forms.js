/*
 * RSA CMS / Mini-CRM public lead form integration
 * Phase 8 Batch 11
 *
 * Safe behavior:
 * - Binds only explicit data-rsa-booking-form / data-rsa-inquiry-form forms, or the
 *   obvious form on booking/contact pages.
 * - Posts to FastAPI through window.RsaApiClient.
 * - Adds loading, success, validation, and error states.
 * - Uses Philippines mobile-number examples and validation helpers.
 */
(function buildRsaLeadForms(global) {
  "use strict";

  const api = global.RsaApiClient;
  const config = global.RSA_API_CONFIG || {};

  const FIELD_ALIASES = {
    customer_name: [
      "customer_name",
      "customerName",
      "full_name",
      "fullName",
      "name",
      "your_name",
      "yourName",
      "client_name",
      "clientName",
    ],
    contact_number: [
      "contact_number",
      "contactNumber",
      "phone",
      "mobile",
      "mobile_number",
      "mobileNumber",
      "contact",
      "phone_number",
      "phoneNumber",
      "tel",
    ],
    email: ["email", "email_address", "emailAddress", "your_email", "yourEmail"],
    address: ["address", "site_address", "siteAddress", "location", "install_address", "installAddress"],
    preferred_date: ["preferred_date", "preferredDate", "booking_date", "bookingDate", "date", "schedule_date", "scheduleDate"],
    preferred_time: ["preferred_time", "preferredTime", "booking_time", "bookingTime", "time", "schedule_time", "scheduleTime"],
    service_interest: [
      "service_interest",
      "serviceInterest",
      "service",
      "service_type",
      "serviceType",
      "product_interest",
      "productInterest",
    ],
    notes: ["notes", "message", "details", "remarks", "comments", "requirements"],
    subject: ["subject", "inquiry_subject", "inquirySubject", "topic"],
    message: ["message", "notes", "details", "remarks", "comments", "requirements"],
    product_id: ["product_id", "productId", "product", "product_code", "productCode"],
    source_page: ["source_page", "sourcePage", "page", "source"],
  };

  function escapeHtml(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getPageName() {
    const path = String(global.location.pathname || "").toLowerCase();
    if (path.includes("booking")) return "booking";
    if (path.includes("contact-us") || path.includes("contact")) return "contact";
    if (path.includes("products")) return "products";
    if (path.includes("promotions")) return "promotions";
    return "public";
  }

  function normalizeSpaces(value) {
    return String(value === undefined || value === null ? "" : value).replace(/\s+/g, " ").trim();
  }

  function digitsOnly(value) {
    return String(value || "").replace(/\D+/g, "");
  }

  function normalizePhilippinesMobile(value) {
    let digits = digitsOnly(value);

    if (digits.startsWith("0063")) {
      digits = digits.slice(2);
    }

    // +63 (0) 919 123 4567 can become 6309191234567 after removing symbols.
    if (digits.startsWith("6309") && digits.length === 13) {
      digits = `63${digits.slice(3)}`;
    }

    // 0919 123 4567 -> 639191234567
    if (digits.startsWith("09") && digits.length === 11) {
      return `63${digits.slice(1)}`;
    }

    // 919 123 4567 -> 639191234567
    if (digits.startsWith("9") && digits.length === 10) {
      return `63${digits}`;
    }

    // +63 919 123 4567 -> 639191234567
    if (digits.startsWith("639") && digits.length === 12) {
      return digits;
    }

    return digits;
  }

  function looksLikePhilippinesMobile(value) {
    const normalized = normalizePhilippinesMobile(value);
    return /^639\d{9}$/.test(normalized);
  }

  function looksLikeEmail(value) {
    const trimmed = normalizeSpaces(value);
    if (!trimmed) return true;
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
  }

  function getField(form, aliases) {
    const candidates = Array.isArray(aliases) ? aliases : [aliases];

    for (const name of candidates) {
      if (form.elements && form.elements[name]) {
        return form.elements[name];
      }
    }

    for (const name of candidates) {
      const escapedName = global.CSS && CSS.escape ? CSS.escape(name) : name.replace(/[^a-zA-Z0-9_-]/g, "");
      const selector = [
        `[name="${escapedName}"]`,
        `#${escapedName}`,
        `[data-rsa-field="${escapedName}"]`,
        `[data-field="${escapedName}"]`,
      ].join(",");
      const field = form.querySelector(selector);
      if (field) return field;
    }

    return null;
  }

  function getFieldValue(form, fieldKey) {
    const field = getField(form, FIELD_ALIASES[fieldKey] || [fieldKey]);
    if (!field || field.value === undefined) {
      return "";
    }
    return normalizeSpaces(field.value);
  }

  function setFieldValue(form, fieldKey, value) {
    const field = getField(form, FIELD_ALIASES[fieldKey] || [fieldKey]);
    if (field && field.value !== undefined && value !== undefined && value !== null) {
      field.value = value;
    }
  }

  function removeEmptyValues(payload) {
    Object.keys(payload).forEach((key) => {
      if (payload[key] === null || payload[key] === undefined || payload[key] === "") {
        delete payload[key];
      }
    });
    return payload;
  }

  function bookingPayloadFromForm(form) {
    return removeEmptyValues({
      customer_name: getFieldValue(form, "customer_name"),
      contact_number: getFieldValue(form, "contact_number"),
      email: getFieldValue(form, "email"),
      address: getFieldValue(form, "address"),
      preferred_date: getFieldValue(form, "preferred_date"),
      preferred_time: getFieldValue(form, "preferred_time"),
      service_interest: getFieldValue(form, "service_interest"),
      notes: getFieldValue(form, "notes"),
    });
  }

  function inquiryPayloadFromForm(form) {
    const sourcePage = getFieldValue(form, "source_page") || form.dataset.rsaSourcePage || getPageName();
    return removeEmptyValues({
      product_id: getFieldValue(form, "product_id"),
      customer_name: getFieldValue(form, "customer_name"),
      contact_number: getFieldValue(form, "contact_number"),
      email: getFieldValue(form, "email"),
      subject: getFieldValue(form, "subject"),
      message: getFieldValue(form, "message"),
      source_page: sourcePage,
    });
  }

  function validateCommonLeadPayload(payload) {
    const errors = [];

    if (!payload.customer_name || payload.customer_name.length < 2) {
      errors.push("Name is required.");
    }

    if (!payload.contact_number) {
      errors.push("Philippines mobile number is required.");
    } else if (!looksLikePhilippinesMobile(payload.contact_number)) {
      errors.push("Enter a valid Philippines mobile number, for example +63 919 123 4567 or 0919 123 4567.");
    }

    if (payload.email && !looksLikeEmail(payload.email)) {
      errors.push("Enter a valid email address.");
    }

    return errors;
  }

  function validateBookingPayload(payload) {
    const errors = validateCommonLeadPayload(payload);

    if (payload.preferred_date) {
      const selected = new Date(`${payload.preferred_date}T00:00:00`);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (!Number.isNaN(selected.getTime()) && selected < today) {
        errors.push("Preferred date cannot be in the past.");
      }
    }

    return errors;
  }

  function validateInquiryPayload(payload) {
    return validateCommonLeadPayload(payload);
  }

  function ensureStatusElement(form) {
    let status = form.querySelector("[data-rsa-form-status]");
    if (status) return status;

    status = form.querySelector(".rsa-api-form-status, .form-status, #form-status, #booking-form-status, #inquiry-form-status");
    if (status) {
      status.setAttribute("data-rsa-form-status", "");
      return status;
    }

    status = document.createElement("div");
    status.className = "rsa-api-form-status";
    status.setAttribute("data-rsa-form-status", "");
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    form.appendChild(status);
    return status;
  }

  function setStatus(formOrElement, message, type) {
    const status = formOrElement && formOrElement.tagName === "FORM" ? ensureStatusElement(formOrElement) : formOrElement;
    if (!status) return;
    status.textContent = message || "";
    status.dataset.status = type || "info";
  }

  function setSubmitting(form, isSubmitting) {
    form.dataset.rsaSubmitting = isSubmitting ? "true" : "false";
    form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((button) => {
      button.disabled = Boolean(isSubmitting);
      if (button.tagName === "BUTTON") {
        if (isSubmitting) {
          button.dataset.rsaOriginalText = button.textContent;
          button.textContent = button.dataset.rsaSubmittingText || "Sending...";
        } else if (button.dataset.rsaOriginalText) {
          button.textContent = button.dataset.rsaOriginalText;
          delete button.dataset.rsaOriginalText;
        }
      }
    });
  }

  function focusFirstInvalidField(form, payload, errors) {
    if (!errors.length) return;
    let targetKey = null;
    if (!payload.customer_name) targetKey = "customer_name";
    else if (!payload.contact_number || !looksLikePhilippinesMobile(payload.contact_number)) targetKey = "contact_number";
    else if (payload.email && !looksLikeEmail(payload.email)) targetKey = "email";

    const field = targetKey ? getField(form, FIELD_ALIASES[targetKey]) : null;
    if (field && typeof field.focus === "function") {
      field.focus();
    }
  }

  function markFormAsBound(form) {
    form.dataset.rsaLeadFormBound = "true";
    form.dataset.rsaApiBound = "true";
  }

  function bindBookingForm(form) {
    if (!api || !form || form.dataset.rsaLeadFormBound === "true") return;

    markFormAsBound(form);
    form.setAttribute("data-rsa-booking-form", "");
    ensureStatusElement(form);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = bookingPayloadFromForm(form);
      const errors = validateBookingPayload(payload);

      if (errors.length) {
        setStatus(form, errors.join(" "), "error");
        focusFirstInvalidField(form, payload, errors);
        return;
      }

      try {
        setSubmitting(form, true);
        setStatus(form, "Sending booking request...", "loading");
        const result = await api.createBooking(payload);
        const reference = result && result.booking_id ? result.booking_id : "received";
        form.dataset.rsaLastReference = reference;
        setStatus(form, `Booking request sent. Reference: ${reference}`, "success");
        form.reset();
      } catch (error) {
        setStatus(form, `Could not send booking request: ${error.message}`, "error");
        if (config.debug) console.error(error);
      } finally {
        setSubmitting(form, false);
      }
    });
  }

  function bindInquiryForm(form) {
    if (!api || !form || form.dataset.rsaLeadFormBound === "true") return;

    markFormAsBound(form);
    form.setAttribute("data-rsa-inquiry-form", "");
    ensureStatusElement(form);
    prefillInquiryFormFromQuery(form);

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = inquiryPayloadFromForm(form);
      const errors = validateInquiryPayload(payload);

      if (errors.length) {
        setStatus(form, errors.join(" "), "error");
        focusFirstInvalidField(form, payload, errors);
        return;
      }

      try {
        setSubmitting(form, true);
        setStatus(form, "Sending inquiry...", "loading");
        const result = await api.createInquiry(payload);
        const reference = result && result.inquiry_id ? result.inquiry_id : "received";
        form.dataset.rsaLastReference = reference;
        setStatus(form, `Inquiry sent. Reference: ${reference}`, "success");
        form.reset();
      } catch (error) {
        setStatus(form, `Could not send inquiry: ${error.message}`, "error");
        if (config.debug) console.error(error);
      } finally {
        setSubmitting(form, false);
      }
    });
  }

  function formHasAnyField(form, fieldKeys) {
    return fieldKeys.some((key) => Boolean(getField(form, FIELD_ALIASES[key] || [key])));
  }

  function discoverBookingForms() {
    const explicit = Array.from(document.querySelectorAll("form[data-rsa-booking-form]"));
    const page = getPageName();
    if (page !== "booking") {
      return explicit;
    }

    const candidates = Array.from(document.querySelectorAll("form")).filter((form) => {
      if (form.dataset.rsaInquiryForm !== undefined || form.hasAttribute("data-rsa-inquiry-form")) return false;
      return formHasAnyField(form, ["customer_name", "contact_number", "preferred_date", "preferred_time", "service_interest", "notes"]);
    });

    return Array.from(new Set(explicit.concat(candidates.length ? candidates : Array.from(document.querySelectorAll("form")).slice(0, 1))));
  }

  function discoverInquiryForms() {
    const explicit = Array.from(document.querySelectorAll("form[data-rsa-inquiry-form]"));
    const page = getPageName();
    if (page !== "contact" && page !== "products" && page !== "promotions") {
      return explicit;
    }

    const candidates = Array.from(document.querySelectorAll("form")).filter((form) => {
      if (form.dataset.rsaBookingForm !== undefined || form.hasAttribute("data-rsa-booking-form")) return false;
      return formHasAnyField(form, ["customer_name", "contact_number", "message", "subject"]);
    });

    return Array.from(new Set(explicit.concat(candidates.length ? candidates : Array.from(document.querySelectorAll("form")).slice(0, 1))));
  }

  function prefillInquiryFormFromQuery(form) {
    if (!form) return;
    let params;
    try {
      params = new URLSearchParams(global.location.search || "");
    } catch (_error) {
      return;
    }

    const productId = params.get("product_id") || params.get("productId");
    const subject = params.get("subject");
    const sourcePage = params.get("source_page") || params.get("sourcePage") || getPageName();

    if (productId) setFieldValue(form, "product_id", productId);
    if (subject) setFieldValue(form, "subject", subject);
    if (sourcePage) setFieldValue(form, "source_page", sourcePage);
  }

  function bindProductInquiryButtons() {
    document.querySelectorAll("[data-rsa-product-inquiry]").forEach((button) => {
      if (button.dataset.rsaProductInquiryBound === "true") return;
      button.dataset.rsaProductInquiryBound = "true";
      button.addEventListener("click", () => {
        const productId = button.dataset.rsaProductInquiry;
        const currentInquiryForm = document.querySelector("form[data-rsa-inquiry-form]");

        if (currentInquiryForm) {
          setFieldValue(currentInquiryForm, "product_id", productId);
          setFieldValue(currentInquiryForm, "subject", `Product inquiry: ${productId}`);
          setFieldValue(currentInquiryForm, "source_page", getPageName());
          currentInquiryForm.scrollIntoView({ behavior: "smooth", block: "start" });
          setStatus(currentInquiryForm, `Product ${productId} selected for inquiry.`, "info");
          return;
        }

        const baseUrl = "contact-us.html";
        const query = new URLSearchParams({
          product_id: productId || "",
          subject: productId ? `Product inquiry: ${productId}` : "Product inquiry",
          source_page: getPageName(),
        });
        global.location.href = `${baseUrl}?${query.toString()}`;
      });
    });
  }

  function bindAllLeadForms() {
    if (!api) {
      return;
    }

    discoverBookingForms().forEach(bindBookingForm);
    discoverInquiryForms().forEach(bindInquiryForm);
    bindProductInquiryButtons();
  }

  global.RsaLeadForms = {
    normalizePhilippinesMobile,
    looksLikePhilippinesMobile,
    bookingPayloadFromForm,
    inquiryPayloadFromForm,
    validateBookingPayload,
    validateInquiryPayload,
    bindBookingForm,
    bindInquiryForm,
    bindAllLeadForms,
    setStatus,
  };

  document.addEventListener("DOMContentLoaded", bindAllLeadForms);
})(window);
