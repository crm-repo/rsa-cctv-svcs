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
    'icon_path',
    'person_image_path'
  ]);

  function basename(value) {
    const text = String(value || '').trim();
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
    if (name === 'person_image_path' || name.includes('person_image')) return 'contact-persons';
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
      'contact-persons': 'uploads/contact-persons',
      general: 'uploads/general'
    }[mediaType] || 'uploads/general';
    return `${folder}/${safeName}`;
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
      file_name: file.name,
      field_value: buildClientFallbackKey(mediaType, file.name),
      object_key: buildClientFallbackKey(mediaType, file.name),
      message: 'Prepared local preview image key. Backend media endpoint was not available.'
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

  function enhanceInput(input) {
    if (!shouldEnhance(input)) return;

    input.dataset.mediaEnhanced = 'true';
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

    const file = document.createElement('input');
    file.type = 'file';
    file.accept = 'image/*';
    file.hidden = true;

    const note = document.createElement('small');
    note.className = 'admin-media-note';
    note.textContent = input.value
      ? `Stored image key: ${input.value}`
      : 'Select an image from your PC. Batch 24 prepares the image key; actual S3 upload comes later.';

    choose.addEventListener('click', () => file.click());

    clear.addEventListener('click', () => {
      input.value = '';
      display.value = '';
      note.textContent = 'Image selection cleared.';
    });

    file.addEventListener('change', async () => {
      const selected = file.files && file.files[0];
      if (!selected) return;

      display.value = selected.name;
      note.textContent = 'Preparing image key…';

      try {
        const result = await prepareMediaKey(input, selected);
        input.value = result.field_value || result.object_key || buildClientFallbackKey(inferMediaType(input), selected.name);
        display.value = result.file_name || selected.name;
        note.textContent = `${result.message || 'Image key prepared.'} Stored key: ${input.value}`;
      } catch (error) {
        input.value = buildClientFallbackKey(inferMediaType(input), selected.name);
        note.textContent = `Could not call media endpoint (${error.message}). Local key prepared: ${input.value}`;
      }
    });

    wrapper.append(display, choose, clear, file, note);
    input.insertAdjacentElement('afterend', wrapper);
  }

  function enhanceAll(root = document) {
    root.querySelectorAll('input[name]').forEach(enhanceInput);
  }

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
