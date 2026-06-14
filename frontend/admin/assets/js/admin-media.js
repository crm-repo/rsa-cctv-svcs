(function () {
  'use strict';

  const MEDIA_FIELD_NAMES = new Set([
    'image_path',
    'brand_logo_path',
    'hero_image_path',
    'company_story_image_path',
    'service_image_path',
    'project_image_path',
    'logo_path',
    'icon_path'
  ]);

  const RSA_ADMIN_MEDIA_INTERIM_VERSION = 'batch55a-admin-media-path-interim-fix';
  window.RSA_ADMIN_MEDIA_INTERIM_VERSION = RSA_ADMIN_MEDIA_INTERIM_VERSION;

  function normalizeStoredPath(value) {
    return String(value || '').trim().replace(/^\.\//, '').replace(/^\/+/, '');
  }

  function basename(value) {
    const text = normalizeStoredPath(value);
    if (!text) return '';
    return text.split(/[\\/]/).filter(Boolean).pop() || text;
  }

  function inferMediaType(input) {
    const path = window.location.pathname.toLowerCase();
    const name = String(input.name || '').toLowerCase();

    if (path.includes('brands') || name.includes('brand_logo')) return 'brands';
    if (path.includes('project-gallery')) return 'project-gallery';
    if (path.includes('services')) return 'services';
    if (path.includes('about') || name.includes('hero') || name.includes('company_story')) return 'about';
    if (path.includes('contact')) return 'contact';
    if (path.includes('products') || name === 'image_path') return 'products';
    return 'general';
  }

  function buildClientFallbackKey(mediaType, fileName) {
    const safeName = String(fileName || '')
      .trim()
      .replace(/\s+/g, '-')
      .replace(/[^A-Za-z0-9._-]/g, '')
      .toLowerCase();
    const folder = {
      products: 'uploads/products',
      brands: 'uploads/brands',
      'project-gallery': 'uploads/project-gallery',
      services: 'uploads/services',
      about: 'uploads/about',
      contact: 'uploads/contact',
      general: 'uploads/general'
    }[mediaType] || 'uploads/general';
    return `${folder}/${safeName}`;
  }

  function isStoredPathPublicNow(value) {
    const path = normalizeStoredPath(value);
    if (!path) return false;
    return path.startsWith('assets/images/') || path.startsWith('http://') || path.startsWith('https://');
  }

  async function prepareMediaKey(input, file) {
    const mediaType = inferMediaType(input);

    if (window.RSAAdminApi && typeof window.RSAAdminApi.postJson === 'function') {
      const result = await window.RSAAdminApi.postJson('/admin/media/prepare-upload', {
        media_type: mediaType,
        file_name: file.name,
        content_type: file.type || null,
        size_bytes: file.size || null
      });
      return result;
    }

    return {
      storage_mode: 'client-fallback',
      upload_prepared: false,
      file_name: file.name,
      field_value: buildClientFallbackKey(mediaType, file.name),
      object_key: buildClientFallbackKey(mediaType, file.name),
      message: 'Backend media endpoint was not available. Existing image path was preserved.'
    };
  }

  function shouldEnhance(input) {
    if (!input || input.dataset.mediaEnhanced === 'true') return false;
    if (!input.name) return false;
    if (input.type === 'file') return false;
    if (input.closest('[data-media-picker]')) return false;

    const name = input.name.toLowerCase();
    return MEDIA_FIELD_NAMES.has(name) || name.endsWith('_image_path') || name.endsWith('_logo_path');
  }

  function setNote(note, text, tone) {
    note.textContent = text;
    note.dataset.tone = tone || '';
  }

  function currentPathMessage(value) {
    const path = normalizeStoredPath(value);
    if (!path) return 'No image path is currently stored.';
    if (isStoredPathPublicNow(path)) return `Current public image path: ${path}`;
    return `Current stored image path: ${path}`;
  }

  function enhanceInput(input) {
    if (!shouldEnhance(input)) return;

    input.dataset.mediaEnhanced = 'true';
    input.dataset.originalMediaValue = normalizeStoredPath(input.value);
    input.value = normalizeStoredPath(input.value);
    input.hidden = true;

    const wrapper = document.createElement('div');
    wrapper.className = 'admin-media-picker';
    wrapper.dataset.mediaPicker = 'true';

    const display = document.createElement('input');
    display.type = 'text';
    display.readOnly = true;
    display.className = 'admin-media-filename';
    display.placeholder = 'No image selected';
    display.value = basename(input.value);

    const choose = document.createElement('button');
    choose.type = 'button';
    choose.className = 'admin-button secondary admin-media-button';
    choose.textContent = 'Choose File';

    const clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'admin-button ghost admin-media-clear';
    clear.textContent = 'Clear';

    const restore = document.createElement('button');
    restore.type = 'button';
    restore.className = 'admin-button ghost admin-media-restore';
    restore.textContent = 'Restore Current';

    const file = document.createElement('input');
    file.type = 'file';
    file.accept = 'image/*';
    file.hidden = true;

    const note = document.createElement('small');
    note.className = 'admin-media-note';
    setNote(note, `${currentPathMessage(input.value)} Browse is safe-preview only until upload storage/S3 is enabled.`, input.value ? 'info' : 'warning');

    choose.addEventListener('click', () => file.click());

    clear.addEventListener('click', () => {
      input.value = '';
      display.value = '';
      setNote(note, 'Image path cleared. Save only if you intentionally want this record to have no image.', 'warning');
    });

    restore.addEventListener('click', () => {
      const original = normalizeStoredPath(input.dataset.originalMediaValue || '');
      input.value = original;
      display.value = basename(original);
      setNote(note, `${currentPathMessage(original)} Restored from the value loaded when this form opened.`, original ? 'info' : 'warning');
    });

    file.addEventListener('change', async () => {
      const selected = file.files && file.files[0];
      if (!selected) return;

      const previousValue = normalizeStoredPath(input.value);
      display.value = selected.name;
      setNote(note, 'Checking media upload readiness…', 'info');

      try {
        const result = await prepareMediaKey(input, selected);
        const preparedValue = normalizeStoredPath(result.field_value || result.public_path || result.object_key || '');

        if (result.upload_prepared === true && preparedValue) {
          input.value = preparedValue;
          display.value = result.file_name || selected.name;
          setNote(note, `${result.message || 'Image upload prepared.'} Stored path: ${input.value}`, 'success');
          return;
        }

        input.value = previousValue;
        display.value = basename(previousValue) || selected.name;
        const futureKey = preparedValue || buildClientFallbackKey(inferMediaType(input), selected.name);
        setNote(
          note,
          `Selected ${selected.name}, but binary upload/storage is not active yet. Existing saved path was preserved${previousValue ? `: ${previousValue}` : ' as blank'}. Future upload key would be: ${futureKey}`,
          'warning'
        );
      } catch (error) {
        input.value = previousValue;
        display.value = basename(previousValue) || selected.name;
        setNote(note, `Could not prepare media (${error.message}). Existing saved path was preserved${previousValue ? `: ${previousValue}` : ' as blank'}.`, 'warning');
      }
    });

    wrapper.append(display, choose, clear, restore, file, note);
    input.insertAdjacentElement('afterend', wrapper);
  }

  function enhanceAll(root = document) {
    root.querySelectorAll('input[name]').forEach(enhanceInput);
  }

  window.RSAAdminMedia = { enhanceAll, enhanceInput };

  document.addEventListener('DOMContentLoaded', () => {
    enhanceAll();
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType !== Node.ELEMENT_NODE) return;
          if (node.matches && node.matches('input[name]')) enhanceInput(node);
          if (node.querySelectorAll) enhanceAll(node);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
}());
