from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
BATCH_VERSION = "batch56b-admin-media-upload-integration"

ADMIN_MEDIA_JS = r'''(function () {
  'use strict';

  const BATCH56B_MEDIA_VERSION = 'batch56b-admin-media-upload-integration';
  window.RSA_ADMIN_MEDIA_UPLOAD_VERSION = BATCH56B_MEDIA_VERSION;

  const MEDIA_FIELD_NAMES = new Set([
    'image_path',
    'brand_logo_path',
    'hero_image_path',
    'company_story_image_path',
    'service_image_path',
    'project_image_path',
    'person_image_path',
    'logo_path',
    'icon_path'
  ]);

  const UPLOAD_ENABLED_TYPES = new Set([
    'products',
    'brands',
    'project-gallery',
    'contact-persons'
  ]);

  const DEFAULT_CONFIG = {
    upload_binary_enabled: true,
    max_upload_mb: 5,
    allowed_extensions: ['.jpeg', '.jpg', '.png', '.webp'],
    allowed_upload_media_types: ['brands', 'contact-persons', 'products', 'project-gallery']
  };

  let configPromise = null;

  function normalizeStoredPath(value) {
    const text = String(value || '').trim();
    if (!text) return '';
    if (/^https?:\/\//i.test(text)) return text;
    if (text.startsWith('/api/media/')) return text;
    if (text.startsWith('api/media/')) return `/${text}`;
    return text.replace(/^\.\//, '').replace(/^\/+/, '');
  }

  function basename(value) {
    const text = normalizeStoredPath(value);
    if (!text) return '';
    return text.split(/[\\/]/).filter(Boolean).pop() || text;
  }

  function extensionOf(fileName) {
    const base = String(fileName || '').toLowerCase();
    const index = base.lastIndexOf('.');
    return index >= 0 ? base.slice(index) : '';
  }

  function resolvePreviewSrc(value) {
    const path = normalizeStoredPath(value);
    if (!path) return '';
    if (/^https?:\/\//i.test(path)) return path;
    if (path.startsWith('/')) return path;
    if (path.startsWith('../') || path.startsWith('./')) return path;
    return `../${path}`;
  }

  function findForm(input) {
    return input.closest('form') || input.closest('[data-detail-drawer]') || document;
  }

  function fieldValue(root, names) {
    for (const name of names) {
      const field = root.querySelector(`[name="${name}"]`);
      if (!field) continue;
      const value = String(field.value || '').trim();
      if (value) return value;
    }
    return '';
  }

  function selectedLabel(root, name) {
    const select = root.querySelector(`select[name="${name}"]`);
    if (!select || !select.selectedOptions || !select.selectedOptions[0]) return '';
    const option = select.selectedOptions[0];
    const value = String(option.value || '').trim();
    const label = String(option.textContent || '').replace(/\s+/g, ' ').trim();
    if (!value) return '';
    return label.replace(/^No brand\s*\/\s*generic$/i, '').trim();
  }

  function pageName() {
    return String(window.location.pathname || '').split('/').pop().replace(/\.html$/i, '').toLowerCase();
  }

  function inferUploadMediaType(input) {
    const page = pageName();
    const name = String(input.name || '').toLowerCase();
    const root = findForm(input);

    if (page === 'products' && name === 'image_path') return 'products';
    if (page === 'brands' && name === 'brand_logo_path') return 'brands';
    if (page === 'project-gallery' && name === 'image_path') return 'project-gallery';

    if (page === 'contact-us' && name === 'person_image_path') {
      const contactType = fieldValue(root, ['contact_type']);
      return !contactType || contactType === 'Contact Person' ? 'contact-persons' : null;
    }

    return null;
  }

  function inferLegacyMediaType(input) {
    const page = pageName();
    const name = String(input.name || '').toLowerCase();
    if (page === 'brands' || name.includes('brand_logo')) return 'brands';
    if (page === 'project-gallery') return 'project-gallery';
    if (page === 'services') return 'services';
    if (page === 'about' || name.includes('hero') || name.includes('company_story')) return 'about';
    if (page === 'contact-us') return 'contact';
    if (page === 'products' || name === 'image_path') return 'products';
    return 'general';
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
    if (path.startsWith('/api/media/')) return `Current uploaded media path: ${path}`;
    if (/^https?:\/\//i.test(path)) return `Current external image URL: ${path}`;
    if (path.startsWith('assets/') || path.startsWith('brands/')) return `Current static image path: ${path}`;
    return `Current stored image path: ${path}`;
  }

  function dispatchFieldChanged(input) {
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function updatePreview(preview, value) {
    const src = resolvePreviewSrc(value);
    if (!src) {
      preview.hidden = true;
      preview.removeAttribute('src');
      return;
    }
    preview.src = src;
    preview.hidden = false;
  }

  function getApi() {
    return window.RSAAdminApi || null;
  }

  async function getMediaConfig() {
    if (!configPromise) {
      const api = getApi();
      if (!api || typeof api.request !== 'function') {
        configPromise = Promise.resolve(DEFAULT_CONFIG);
      } else {
        configPromise = api.request('/admin/media/config').catch(() => DEFAULT_CONFIG);
      }
    }
    return configPromise;
  }

  function validateFileAgainstConfig(file, config) {
    const allowedExtensions = new Set((config.allowed_extensions || DEFAULT_CONFIG.allowed_extensions).map(item => String(item).toLowerCase()));
    const extension = extensionOf(file.name);
    if (!allowedExtensions.has(extension)) {
      throw new Error(`Unsupported file type. Use JPG, PNG, or WEBP only.`);
    }

    const maxMb = Number(config.max_upload_mb || DEFAULT_CONFIG.max_upload_mb || 5);
    const maxBytes = maxMb * 1024 * 1024;
    if (file.size > maxBytes) {
      throw new Error(`Image is too large. Maximum upload size is ${maxMb} MB.`);
    }
  }

  function collectUploadContext(input) {
    const root = findForm(input);
    const productName = fieldValue(root, ['product_name']);
    const brandName = fieldValue(root, ['product_brand_name', 'brand_name']) || selectedLabel(root, 'product_brand_key');
    const featureOne = fieldValue(root, ['feature_01']);
    const subcategory = fieldValue(root, ['subcategory', 'subcategory_name']);
    const projectTitle = fieldValue(root, ['project_title']);
    const personName = fieldValue(root, ['person_name']);
    const serviceTitle = fieldValue(root, ['service_title']);

    const slugSource = productName || brandName || projectTitle || personName || serviceTitle || basename(input.value);

    return {
      slug_source: slugSource,
      product_name: productName,
      brand_name: brandName,
      feature_01: featureOne,
      subcategory
    };
  }

  async function uploadMediaFile(input, file) {
    const api = getApi();
    if (!api || typeof api.getApiBaseUrl !== 'function') {
      throw new Error('Admin API client is not available.');
    }

    const mediaType = inferUploadMediaType(input);
    if (!mediaType || !UPLOAD_ENABLED_TYPES.has(mediaType)) {
      throw new Error('Real upload is not enabled for this image field in Batch 56B.');
    }

    const config = await getMediaConfig();
    validateFileAgainstConfig(file, config);

    if (config.upload_binary_enabled === false) {
      throw new Error('Media upload storage is not enabled by the backend yet.');
    }

    const allowedTypes = new Set(config.allowed_upload_media_types || DEFAULT_CONFIG.allowed_upload_media_types);
    if (!allowedTypes.has(mediaType)) {
      throw new Error(`Upload group ${mediaType} is not enabled by the backend.`);
    }

    const formData = new FormData();
    formData.append('media_type', mediaType);
    formData.append('file', file);

    const context = collectUploadContext(input);
    Object.entries(context).forEach(([key, value]) => {
      if (value) formData.append(key, value);
    });

    const url = `${api.getApiBaseUrl()}/admin/media/upload`;
    const headers = {
      Accept: 'application/json',
      ...(typeof api.getAuthHeaders === 'function' ? api.getAuthHeaders() : {})
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData
    });

    const text = await response.text();
    let payload = null;
    try {
      payload = text ? JSON.parse(text) : null;
    } catch (_error) {
      payload = null;
    }

    if (!response.ok) {
      const detail = payload && payload.detail ? payload.detail : text;
      throw new Error(detail || `${response.status} ${response.statusText}`);
    }

    if (!payload || payload.upload_prepared !== true) {
      throw new Error('Upload did not return upload_prepared=true. Existing path was preserved.');
    }

    return payload;
  }

  function legacyUnsupportedMessage(input, selectedName) {
    const mediaType = inferLegacyMediaType(input);
    return `Selected ${selectedName}, but real upload is not enabled for ${mediaType} fields in Batch 56B. Existing saved path was preserved.`;
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
    file.accept = '.jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp';
    file.hidden = true;

    const preview = document.createElement('img');
    preview.className = 'admin-media-preview';
    preview.alt = 'Selected media preview';
    preview.loading = 'lazy';

    const note = document.createElement('small');
    note.className = 'admin-media-note';

    const uploadType = inferUploadMediaType(input);
    const uploadEnabled = uploadType && UPLOAD_ENABLED_TYPES.has(uploadType);
    setNote(
      note,
      uploadEnabled
        ? `${currentPathMessage(input.value)} Choose File uploads to media storage before save.`
        : `${currentPathMessage(input.value)} Upload is not enabled for this field in Batch 56B; existing path will be preserved.`,
      uploadEnabled ? 'info' : 'warning'
    );
    updatePreview(preview, input.value);

    choose.addEventListener('click', () => file.click());

    clear.addEventListener('click', () => {
      input.value = '';
      display.value = '';
      input.dataset.mediaKey = '';
      input.dataset.uploadPrepared = '';
      updatePreview(preview, '');
      setNote(note, 'Image path cleared. Save only if you intentionally want this record to have no image.', 'warning');
      dispatchFieldChanged(input);
    });

    restore.addEventListener('click', () => {
      const original = normalizeStoredPath(input.dataset.originalMediaValue || '');
      input.value = original;
      display.value = basename(original);
      input.dataset.mediaKey = '';
      input.dataset.uploadPrepared = '';
      updatePreview(preview, original);
      setNote(note, `${currentPathMessage(original)} Restored from the value loaded when this form opened.`, original ? 'info' : 'warning');
      dispatchFieldChanged(input);
    });

    file.addEventListener('change', async () => {
      const selected = file.files && file.files[0];
      if (!selected) return;

      const previousValue = normalizeStoredPath(input.value);
      const previousDisplay = display.value;
      const previousMediaKey = input.dataset.mediaKey || '';
      const objectUrl = URL.createObjectURL(selected);

      display.value = selected.name;
      preview.src = objectUrl;
      preview.hidden = false;
      choose.disabled = true;
      clear.disabled = true;
      restore.disabled = true;

      const uploadTypeNow = inferUploadMediaType(input);
      if (!uploadTypeNow || !UPLOAD_ENABLED_TYPES.has(uploadTypeNow)) {
        input.value = previousValue;
        display.value = previousDisplay || basename(previousValue) || selected.name;
        updatePreview(preview, previousValue);
        setNote(note, legacyUnsupportedMessage(input, selected.name), 'warning');
        choose.disabled = false;
        clear.disabled = false;
        restore.disabled = false;
        URL.revokeObjectURL(objectUrl);
        file.value = '';
        return;
      }

      setNote(note, `Uploading ${selected.name}...`, 'info');

      try {
        const result = await uploadMediaFile(input, selected);
        const preparedValue = normalizeStoredPath(result.field_value || result.media_url || result.public_path || '');
        const mediaKey = normalizeStoredPath(result.media_key || result.object_key || '');

        if (!preparedValue) {
          throw new Error('Upload succeeded but no media URL was returned.');
        }

        input.value = preparedValue;
        input.dataset.mediaKey = mediaKey;
        input.dataset.uploadPrepared = 'true';
        display.value = result.file_name || basename(preparedValue) || selected.name;
        updatePreview(preview, preparedValue);
        setNote(note, `${result.message || 'Image uploaded successfully.'} Save this record to keep the new image path.`, 'success');
        dispatchFieldChanged(input);
      } catch (error) {
        input.value = previousValue;
        input.dataset.mediaKey = previousMediaKey;
        input.dataset.uploadPrepared = '';
        display.value = previousDisplay || basename(previousValue) || selected.name;
        updatePreview(preview, previousValue);
        setNote(note, `Upload failed: ${error.message}. Existing saved path was preserved.`, 'warning');
      } finally {
        choose.disabled = false;
        clear.disabled = false;
        restore.disabled = false;
        URL.revokeObjectURL(objectUrl);
        file.value = '';
      }
    });

    wrapper.append(preview, display, choose, clear, restore, file, note);
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
'''

ADMIN_MEDIA_CSS = r'''.admin-media-picker {
  display: grid;
  grid-template-columns: 74px minmax(180px, 1fr) auto auto auto;
  gap: 8px;
  align-items: center;
  margin-top: 6px;
}

.admin-media-picker .admin-media-filename {
  min-width: 0;
  background: #f9fafb;
  cursor: default;
}

.admin-media-preview {
  width: 64px;
  height: 52px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f8fafc;
}

.admin-media-preview[hidden] {
  display: none;
}

.admin-media-button,
.admin-media-clear,
.admin-media-restore {
  white-space: nowrap;
}

.admin-media-note {
  grid-column: 1 / -1;
  display: block;
  color: #6b7280;
  font-size: 12px;
  line-height: 1.4;
}

.admin-media-note[data-tone="success"] {
  color: #047857;
}

.admin-media-note[data-tone="warning"] {
  color: #b45309;
}

.admin-media-note[data-tone="info"] {
  color: #475569;
}

.admin-button.ghost {
  background: #ffffff;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

.admin-media-picker button:disabled {
  opacity: 0.62;
  cursor: wait;
}

/* batch56b-admin-media-upload-integration */
@media (max-width: 860px) {
  .admin-media-picker {
    grid-template-columns: 74px minmax(160px, 1fr) auto;
  }

  .admin-media-restore {
    grid-column: 2 / -1;
    justify-self: start;
  }
}

@media (max-width: 720px) {
  .admin-media-picker {
    grid-template-columns: 1fr;
  }

  .admin-media-preview {
    width: 100%;
    height: 150px;
  }
}
'''

DOC = r'''# Batch 56B - Admin media upload integration

Batch 56B connects the Batch 56A backend/S3 media upload endpoint to the existing admin media picker.

## Scope

Integrated real uploads for:

- Products: `image_path`
- Brands: `brand_logo_path`
- Project Gallery: `image_path`
- Contact Us: `person_image_path` for Contact Person records

Not included:

- No backend route changes
- No DynamoDB schema changes
- No S3 bucket/IAM changes
- No CloudFront or Route 53
- No email/SMS/notification changes
- No About/Services upload enablement in this batch

## Behavior

Choose File now uploads the selected image to `POST /api/admin/media/upload` before the record is saved.

Successful upload returns `upload_prepared=true` and a `/api/media/...` path. The hidden form field is updated only after the backend confirms upload success.

If upload fails, the existing image path is preserved.

Restore Current restores the image path that was loaded when the form opened.

## Safety

- JPG/JPEG/PNG/WEBP only
- Backend max upload limit from `/api/admin/media/config`
- Existing admin bearer token is used
- No unauthenticated upload
- Static legacy image paths remain supported
'''

README = r'''Batch 56B - Admin media upload integration

Apply:
  python backend/scripts/patch_admin_media_upload_integration_56b.py

Verify:
  node --check frontend/admin/assets/js/admin-media.js
  Select-String -Path .\frontend\admin\assets\js\admin-media.js,.\frontend\admin\assets\css\admin-media.css -Pattern "batch56b-admin-media-upload-integration"
  Select-String -Path .\frontend\admin\*.html,.\frontend\admin\assets\js\*.js,.\frontend\admin\assets\css\*.css -Pattern "â|�|admin-icon-consistency-55c|fa-boxes-stackedes-stacked"

Browser checks:
  Products image upload
  Brand logo upload
  Project Gallery image upload
  Contact Person photo upload
  Failed upload preserves existing path
  Restore Current works
'''


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[ok] wrote {path}")


def preflight() -> None:
    media_service = ROOT / "backend" / "app" / "services" / "media_service.py"
    admin_media_route = ROOT / "backend" / "app" / "routes" / "admin_media.py"
    if not media_service.exists() or not admin_media_route.exists():
        raise SystemExit("[fail] Batch 56A media upload endpoint files are missing. Apply/verify Batch 56A first.")
    service_text = media_service.read_text(encoding="utf-8", errors="replace")
    route_text = admin_media_route.read_text(encoding="utf-8", errors="replace")
    if "batch56a-media-upload-endpoint" not in service_text or "/upload" not in route_text:
        raise SystemExit("[fail] Batch 56A upload endpoint marker was not found. Verify Batch 56A before applying 56B.")


def main() -> None:
    preflight()
    write(ROOT / "frontend" / "admin" / "assets" / "js" / "admin-media.js", ADMIN_MEDIA_JS)
    write(ROOT / "frontend" / "admin" / "assets" / "css" / "admin-media.css", ADMIN_MEDIA_CSS)
    write(ROOT / "docs" / "phase8_batch56b_admin_media_upload_integration.md", DOC)
    write(ROOT / "README_PHASE8_BATCH56B_ADMIN_MEDIA_UPLOAD_INTEGRATION.txt", README)
    print("[done] batch56b-admin-media-upload-integration applied.")
    print("[done] Admin media picker now uploads through the existing Batch 56A backend endpoint before save.")
    print("[done] No backend route, DynamoDB schema, S3 bucket/IAM, CloudFront, Route 53, email/SMS, or notification change.")


if __name__ == "__main__":
    main()
