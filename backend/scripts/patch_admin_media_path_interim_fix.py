from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ADMIN_MEDIA_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-media.js"
BRANDS_JSON = ROOT / "backend" / "app" / "data" / "review_import" / "brands.json"

SAFE_ADMIN_MEDIA_JS = r"(function () {\n  'use strict';\n\n  const MEDIA_FIELD_NAMES = new Set([\n    'image_path',\n    'brand_logo_path',\n    'hero_image_path',\n    'company_story_image_path',\n    'service_image_path',\n    'project_image_path',\n    'logo_path',\n    'icon_path'\n  ]);\n\n  const RSA_ADMIN_MEDIA_INTERIM_VERSION = 'batch55a-admin-media-path-interim-fix';\n  window.RSA_ADMIN_MEDIA_INTERIM_VERSION = RSA_ADMIN_MEDIA_INTERIM_VERSION;\n\n  function normalizeStoredPath(value) {\n    return String(value || '').trim().replace(/^\\.\\//, '').replace(/^\\/+/, '');\n  }\n\n  function basename(value) {\n    const text = normalizeStoredPath(value);\n    if (!text) return '';\n    return text.split(/[\\\\/]/).filter(Boolean).pop() || text;\n  }\n\n  function inferMediaType(input) {\n    const path = window.location.pathname.toLowerCase();\n    const name = String(input.name || '').toLowerCase();\n\n    if (path.includes('brands') || name.includes('brand_logo')) return 'brands';\n    if (path.includes('project-gallery')) return 'project-gallery';\n    if (path.includes('services')) return 'services';\n    if (path.includes('about') || name.includes('hero') || name.includes('company_story')) return 'about';\n    if (path.includes('contact')) return 'contact';\n    if (path.includes('products') || name === 'image_path') return 'products';\n    return 'general';\n  }\n\n  function buildClientFallbackKey(mediaType, fileName) {\n    const safeName = String(fileName || '')\n      .trim()\n      .replace(/\\s+/g, '-')\n      .replace(/[^A-Za-z0-9._-]/g, '')\n      .toLowerCase();\n    const folder = {\n      products: 'uploads/products',\n      brands: 'uploads/brands',\n      'project-gallery': 'uploads/project-gallery',\n      services: 'uploads/services',\n      about: 'uploads/about',\n      contact: 'uploads/contact',\n      general: 'uploads/general'\n    }[mediaType] || 'uploads/general';\n    return `${folder}/${safeName}`;\n  }\n\n  function isStoredPathPublicNow(value) {\n    const path = normalizeStoredPath(value);\n    if (!path) return false;\n    return path.startsWith('assets/images/') || path.startsWith('http://') || path.startsWith('https://');\n  }\n\n  async function prepareMediaKey(input, file) {\n    const mediaType = inferMediaType(input);\n\n    if (window.RSAAdminApi && typeof window.RSAAdminApi.postJson === 'function') {\n      const result = await window.RSAAdminApi.postJson('/admin/media/prepare-upload', {\n        media_type: mediaType,\n        file_name: file.name,\n        content_type: file.type || null,\n        size_bytes: file.size || null\n      });\n      return result;\n    }\n\n    return {\n      storage_mode: 'client-fallback',\n      upload_prepared: false,\n      file_name: file.name,\n      field_value: buildClientFallbackKey(mediaType, file.name),\n      object_key: buildClientFallbackKey(mediaType, file.name),\n      message: 'Backend media endpoint was not available. Existing image path was preserved.'\n    };\n  }\n\n  function shouldEnhance(input) {\n    if (!input || input.dataset.mediaEnhanced === 'true') return false;\n    if (!input.name) return false;\n    if (input.type === 'file') return false;\n    if (input.closest('[data-media-picker]')) return false;\n\n    const name = input.name.toLowerCase();\n    return MEDIA_FIELD_NAMES.has(name) || name.endsWith('_image_path') || name.endsWith('_logo_path');\n  }\n\n  function setNote(note, text, tone) {\n    note.textContent = text;\n    note.dataset.tone = tone || '';\n  }\n\n  function currentPathMessage(value) {\n    const path = normalizeStoredPath(value);\n    if (!path) return 'No image path is currently stored.';\n    if (isStoredPathPublicNow(path)) return `Current public image path: ${path}`;\n    return `Current stored image path: ${path}`;\n  }\n\n  function enhanceInput(input) {\n    if (!shouldEnhance(input)) return;\n\n    input.dataset.mediaEnhanced = 'true';\n    input.dataset.originalMediaValue = normalizeStoredPath(input.value);\n    input.value = normalizeStoredPath(input.value);\n    input.hidden = true;\n\n    const wrapper = document.createElement('div');\n    wrapper.className = 'admin-media-picker';\n    wrapper.dataset.mediaPicker = 'true';\n\n    const display = document.createElement('input');\n    display.type = 'text';\n    display.readOnly = true;\n    display.className = 'admin-media-filename';\n    display.placeholder = 'No image selected';\n    display.value = basename(input.value);\n\n    const choose = document.createElement('button');\n    choose.type = 'button';\n    choose.className = 'admin-button secondary admin-media-button';\n    choose.textContent = 'Choose File';\n\n    const clear = document.createElement('button');\n    clear.type = 'button';\n    clear.className = 'admin-button ghost admin-media-clear';\n    clear.textContent = 'Clear';\n\n    const restore = document.createElement('button');\n    restore.type = 'button';\n    restore.className = 'admin-button ghost admin-media-restore';\n    restore.textContent = 'Restore Current';\n\n    const file = document.createElement('input');\n    file.type = 'file';\n    file.accept = 'image/*';\n    file.hidden = true;\n\n    const note = document.createElement('small');\n    note.className = 'admin-media-note';\n    setNote(note, `${currentPathMessage(input.value)} Browse is safe-preview only until upload storage/S3 is enabled.`, input.value ? 'info' : 'warning');\n\n    choose.addEventListener('click', () => file.click());\n\n    clear.addEventListener('click', () => {\n      input.value = '';\n      display.value = '';\n      setNote(note, 'Image path cleared. Save only if you intentionally want this record to have no image.', 'warning');\n    });\n\n    restore.addEventListener('click', () => {\n      const original = normalizeStoredPath(input.dataset.originalMediaValue || '');\n      input.value = original;\n      display.value = basename(original);\n      setNote(note, `${currentPathMessage(original)} Restored from the value loaded when this form opened.`, original ? 'info' : 'warning');\n    });\n\n    file.addEventListener('change', async () => {\n      const selected = file.files && file.files[0];\n      if (!selected) return;\n\n      const previousValue = normalizeStoredPath(input.value);\n      display.value = selected.name;\n      setNote(note, 'Checking media upload readiness…', 'info');\n\n      try {\n        const result = await prepareMediaKey(input, selected);\n        const preparedValue = normalizeStoredPath(result.field_value || result.public_path || result.object_key || '');\n\n        if (result.upload_prepared === true && preparedValue) {\n          input.value = preparedValue;\n          display.value = result.file_name || selected.name;\n          setNote(note, `${result.message || 'Image upload prepared.'} Stored path: ${input.value}`, 'success');\n          return;\n        }\n\n        input.value = previousValue;\n        display.value = basename(previousValue) || selected.name;\n        const futureKey = preparedValue || buildClientFallbackKey(inferMediaType(input), selected.name);\n        setNote(\n          note,\n          `Selected ${selected.name}, but binary upload/storage is not active yet. Existing saved path was preserved${previousValue ? `: ${previousValue}` : ' as blank'}. Future upload key would be: ${futureKey}`,\n          'warning'\n        );\n      } catch (error) {\n        input.value = previousValue;\n        display.value = basename(previousValue) || selected.name;\n        setNote(note, `Could not prepare media (${error.message}). Existing saved path was preserved${previousValue ? `: ${previousValue}` : ' as blank'}.`, 'warning');\n      }\n    });\n\n    wrapper.append(display, choose, clear, restore, file, note);\n    input.insertAdjacentElement('afterend', wrapper);\n  }\n\n  function enhanceAll(root = document) {\n    root.querySelectorAll('input[name]').forEach(enhanceInput);\n  }\n\n  document.addEventListener('DOMContentLoaded', () => {\n    enhanceAll();\n    const observer = new MutationObserver((mutations) => {\n      mutations.forEach((mutation) => {\n        mutation.addedNodes.forEach((node) => {\n          if (node.nodeType !== Node.ELEMENT_NODE) return;\n          if (node.matches && node.matches('input[name]')) enhanceInput(node);\n          if (node.querySelectorAll) enhanceAll(node);\n        });\n      });\n    });\n    observer.observe(document.body, { childList: true, subtree: true });\n  });\n}());\n"

CANONICAL_BRAND_LOGOS = {
    "dahua": "dahua.png",
    "hikvision": "hikvision.png",
    "uniview": "uniview.png",
    "ezviz": "ezviz.png",
    "tplink": "tplink.png",
    "tp-link": "tplink.png",
    "d-link": "dlink.png",
    "dlink": "dlink.png",
    "bosch": "bosch.png",
    "seagate": "seagate.png",
    "western-digital": "wd.png",
    "wd": "wd.png",
    "hanwha": "hanwha.png",
    "hanhwa": "hanwha.png",
    "axis": "axis.png",
    "axis-communications": "axis.png",
    "imou": "imou.png",
    "avtech": "avtech.png",
    "panasonic": "panasonic.png",
    "cisco": "cisco.png",
    "eufy": "eufy.png",
    "aqara": "aqara.png",
    "igloohome": "igloohome.png",
    "arlo": "arlo.png",
    "unifi": "unifi.png",
    "mercusys": "mercusys.png",
    "yale": "yale.png",
}


def norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")


def patch_admin_media() -> None:
    if not ADMIN_MEDIA_JS.exists():
        raise FileNotFoundError(f"Missing admin media script: {ADMIN_MEDIA_JS}")
    ADMIN_MEDIA_JS.write_text(SAFE_ADMIN_MEDIA_JS, encoding="utf-8")
    print(f"[ok] Replaced {ADMIN_MEDIA_JS.relative_to(ROOT)} with Batch 55A safe interim media picker.")


def patch_brands_json() -> None:
    if not BRANDS_JSON.exists():
        print(f"[skip] {BRANDS_JSON.relative_to(ROOT)} not found; no static review brand file to patch.")
        return

    brands = json.loads(BRANDS_JSON.read_text(encoding="utf-8"))
    changed = 0
    for brand in brands:
        key = norm(brand.get("brand_key"))
        name = norm(brand.get("brand_name"))
        filename = CANONICAL_BRAND_LOGOS.get(key) or CANONICAL_BRAND_LOGOS.get(name)
        if not filename:
            continue
        expected = f"assets/images/brands/{filename}"
        if brand.get("brand_logo_path") != expected:
            brand["brand_logo_path"] = expected
            brand["updated_by"] = "batch55a-static-brand-logo-path-cleanup"
            changed += 1

    BRANDS_JSON.write_text(json.dumps(brands, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] Patched {BRANDS_JSON.relative_to(ROOT)} ({changed} logo path updates).")


def main() -> None:
    patch_admin_media()
    patch_brands_json()
    print("[done] Batch 55A admin media path interim fix applied.")


if __name__ == "__main__":
    main()
