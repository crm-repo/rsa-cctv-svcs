from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
MARKER = "batch59b-full-admin-delete-actions"
SAFE_MARKER = "batch59b-safe-admin-only-restricted-actions"

BACKEND = ROOT / "backend" / "app"
FRONTEND_ADMIN = ROOT / "frontend" / "admin"
ADMIN_JS = FRONTEND_ADMIN / "assets" / "js"
ADMIN_CSS = FRONTEND_ADMIN / "assets" / "css" / "admin.css"
DOC = ROOT / "docs" / "phase8_batch59b_admin_only_restricted_actions.md"

FILES = {
    "product_repo": BACKEND / "repositories" / "product_repository.py",
    "brand_repo": BACKEND / "repositories" / "brand_repository.py",
    "category_repo": BACKEND / "repositories" / "category_repository.py",
    "key_feature_repo": BACKEND / "repositories" / "key_feature_repository.py",
    "product_service": BACKEND / "services" / "product_service.py",
    "brand_service": BACKEND / "services" / "brand_service.py",
    "category_service": BACKEND / "services" / "category_service.py",
    "key_feature_service": BACKEND / "services" / "key_feature_service.py",
    "product_route": BACKEND / "routes" / "products.py",
    "brand_route": BACKEND / "routes" / "brands.py",
    "category_route": BACKEND / "routes" / "categories.py",
    "key_feature_route": BACKEND / "routes" / "key_features.py",
    "admin_catalog": ADMIN_JS / "admin-catalog.js",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


def require(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"[fail] Missing required {label}: {rel(path)}")


def append_once(path: Path, marker: str, snippet: str, label: str) -> None:
    require(path, label)
    text = read(path)
    if marker in text:
        print(f"[skip] {label} already has {marker}")
        return
    write(path, text.rstrip() + "\n\n" + snippet.strip() + "\n")
    print(f"[ok] Added {label}")


def remove_safe_v2_append(path: Path) -> None:
    if not path.exists():
        return
    text = read(path)
    if SAFE_MARKER not in text:
        return
    # The discarded safe-v2 package appended the marker near EOF. Remove from the marker line onward.
    patterns = [
        rf"\n\s*//\s*{re.escape(SAFE_MARKER)}[\s\S]*$",
        rf"\n\s*/\*\s*{re.escape(SAFE_MARKER)}[\s\S]*$",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, count=1)
    if cleaned != text:
        write(path, cleaned.rstrip() + "\n")
        print(f"[ok] Removed discarded safe-v2 append from {rel(path)}")


def cleanup_discarded_safe_v2() -> None:
    for path in [ADMIN_JS / "admin-auth.js", ADMIN_JS / "admin-header-utilities-55d.js", ADMIN_CSS]:
        remove_safe_v2_append(path)
    stale = ADMIN_JS / "admin-restricted-actions-59b-safe.js"
    if stale.exists():
        stale.unlink()
        print(f"[ok] Removed stale {rel(stale)}")


REPO_PATCHES = {
    "product_repo": r'''
# --- batch59b-full-admin-delete-actions ---
def _batch59b_product_delete_product(self, product_id: str) -> bool:
    if hasattr(self, "delete"):
        return bool(self.delete(product_id))
    existing = self.get_by_id(product_id)
    if existing is None:
        return False
    self._repository.delete_by_id(product_id)
    return True

if not hasattr(ProductRepository, "delete_product"):
    ProductRepository.delete_product = _batch59b_product_delete_product  # type: ignore[attr-defined]
if not hasattr(DynamoDBProductRepository, "delete_product"):
    DynamoDBProductRepository.delete_product = _batch59b_product_delete_product  # type: ignore[attr-defined]
''',
    "brand_repo": r'''
# --- batch59b-full-admin-delete-actions ---
def _batch59b_brand_delete_brand(self, brand_id: str) -> bool:
    if hasattr(self, "delete"):
        return bool(self.delete(brand_id))
    existing = self.get_by_id(brand_id)
    if existing is None:
        return False
    self._repository.delete_by_id(brand_id)
    return True

if not hasattr(BrandRepository, "delete_brand"):
    BrandRepository.delete_brand = _batch59b_brand_delete_brand  # type: ignore[attr-defined]
if not hasattr(DynamoDBBrandRepository, "delete_brand"):
    DynamoDBBrandRepository.delete_brand = _batch59b_brand_delete_brand  # type: ignore[attr-defined]
''',
    "category_repo": r'''
# --- batch59b-full-admin-delete-actions ---
def _batch59b_category_delete_category(self, category_id: str) -> bool:
    if hasattr(self, "delete"):
        return bool(self.delete(category_id))
    existing = self.get_by_id(category_id)
    if existing is None:
        return False
    self._repository.delete_by_id(category_id)
    return True

if not hasattr(CategoryRepository, "delete_category"):
    CategoryRepository.delete_category = _batch59b_category_delete_category  # type: ignore[attr-defined]
if not hasattr(DynamoDBCategoryRepository, "delete_category"):
    DynamoDBCategoryRepository.delete_category = _batch59b_category_delete_category  # type: ignore[attr-defined]
''',
    "key_feature_repo": r'''
# --- batch59b-full-admin-delete-actions ---
def _batch59b_key_feature_delete_key_feature(self, key_feat_id: str) -> bool:
    if hasattr(self, "delete"):
        return bool(self.delete(key_feat_id))
    existing = self.get_by_id(key_feat_id)
    if existing is None:
        return False
    self._repository.delete_by_id(key_feat_id)
    return True

if not hasattr(KeyFeatureRepository, "delete_key_feature"):
    KeyFeatureRepository.delete_key_feature = _batch59b_key_feature_delete_key_feature  # type: ignore[attr-defined]
if not hasattr(DynamoDBKeyFeatureRepository, "delete_key_feature"):
    DynamoDBKeyFeatureRepository.delete_key_feature = _batch59b_key_feature_delete_key_feature  # type: ignore[attr-defined]
''',
}

SERVICE_PATCHES = {
    "product_service": r'''
# --- batch59b-full-admin-delete-actions ---
def delete_admin_product(product_id: str) -> bool:
    repository = _get_product_repository()
    existing = repository.get_by_id(product_id)
    if existing is None:
        return False
    if not hasattr(repository, "delete_product"):
        raise ValueError("Product repository delete support is unavailable.")
    return bool(repository.delete_product(product_id))
''',
    "brand_service": r'''
# --- batch59b-full-admin-delete-actions ---
def delete_admin_brand(brand_id: str) -> bool:
    repository = _get_brand_repository()
    existing = repository.get_by_id(brand_id)
    if existing is None:
        return False

    from app.repositories.repository_factory import create_product_repository

    brand_key = str(getattr(existing, "brand_key", "") or "").strip().lower()
    brand_name = str(getattr(existing, "brand_name", "") or "").strip().lower()
    for product in create_product_repository().list_all():
        product_brand_id = str(getattr(product, "brand_id", "") or "").strip()
        product_brand_key = str(getattr(product, "product_brand_key", "") or "").strip().lower()
        product_brand_name = str(getattr(product, "product_brand_name", "") or "").strip().lower()
        if product_brand_id == brand_id or (brand_key and product_brand_key == brand_key) or (brand_name and product_brand_name == brand_name):
            raise ValueError("Brand cannot be deleted because one or more products use it.")

    if not hasattr(repository, "delete_brand"):
        raise ValueError("Brand repository delete support is unavailable.")
    return bool(repository.delete_brand(brand_id))
''',
    "category_service": r'''
# --- batch59b-full-admin-delete-actions ---
def delete_admin_category(category_id: str) -> bool:
    repository = _get_category_repository()
    existing = repository.get_by_id(category_id)
    if existing is None:
        return False

    from app.repositories.repository_factory import create_product_repository

    category_key = str(getattr(existing, "category_key", "") or "").strip().lower()
    category_name = str(getattr(existing, "category_name", "") or "").strip().lower()
    for product in create_product_repository().list_all():
        product_category_id = str(getattr(product, "category_id", "") or "").strip()
        product_category_key = str(getattr(product, "category_key", "") or "").strip().lower()
        product_category_name = str(getattr(product, "category_name", "") or "").strip().lower()
        if product_category_id == category_id or (category_key and product_category_key == category_key) or (category_name and product_category_name == category_name):
            raise ValueError("Category cannot be deleted because one or more products use it.")

    if not hasattr(repository, "delete_category"):
        raise ValueError("Category repository delete support is unavailable.")
    return bool(repository.delete_category(category_id))
''',
    "key_feature_service": r'''
# --- batch59b-full-admin-delete-actions ---
def delete_admin_key_feature(key_feat_id: str) -> bool:
    repository = _get_key_feature_repository()
    existing = repository.get_by_id(key_feat_id)
    if existing is None:
        return False

    from app.repositories.repository_factory import create_product_repository

    feature_name = str(getattr(existing, "key_feat_name", "") or "").strip().lower()
    if feature_name:
        for product in create_product_repository().list_all():
            for index in range(1, 11):
                product_feature = str(getattr(product, f"feature_{index:02d}", "") or "").strip().lower()
                if product_feature and product_feature == feature_name:
                    raise ValueError("Key feature cannot be deleted because one or more products use it.")

    if not hasattr(repository, "delete_key_feature"):
        raise ValueError("Key feature repository delete support is unavailable.")
    return bool(repository.delete_key_feature(key_feat_id))
''',
}

ROUTE_PATCHES = {
    "product_route": r'''
# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_admin_59b(product_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.product_service import delete_admin_product
    try:
        deleted = delete_admin_product(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
''',
    "brand_route": r'''
# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand_admin_59b(brand_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.brand_service import delete_admin_brand
    try:
        deleted = delete_admin_brand(brand_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Brand not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
''',
    "category_route": r'''
# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_admin_59b(category_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.category_service import delete_admin_category
    try:
        deleted = delete_admin_category(category_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
''',
    "key_feature_route": r'''
# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/key-features/{key_feat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_key_feature_admin_59b(key_feat_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.key_feature_service import delete_admin_key_feature
    try:
        deleted = delete_admin_key_feature(key_feat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Key feature not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
''',
}

CATALOG_JS_PATCH = r'''
// --- batch59b-full-admin-delete-actions ---
(function () {
  'use strict';

  const MARKER = 'batch59b-full-admin-delete-actions';
  const PAGE_CONFIG = {
    products: { endpoint: '/admin/products', noun: 'product' },
    brands: { endpoint: '/admin/brands', noun: 'brand' },
    categories: { endpoint: '/admin/categories', noun: 'category' },
    'key-features': { endpoint: '/admin/key-features', noun: 'key feature' },
  };

  function qs(selector, root) { return (root || document).querySelector(selector); }
  function qsa(selector, root) { return Array.from((root || document).querySelectorAll(selector)); }

  function decodeJwt(token) {
    try {
      const parts = String(token || '').split('.');
      if (parts.length < 2) return {};
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
      return JSON.parse(atob(padded));
    } catch (error) {
      return {};
    }
  }

  function isAdmin() {
    if (window.RSAAdminRole && window.RSAAdminRole.isAdmin === true) return true;
    if (document.body && document.body.getAttribute('data-admin-role') === 'Admin') return true;
    const access = decodeJwt(window.localStorage.getItem('rsa_admin_access_token'));
    const id = decodeJwt(window.localStorage.getItem('rsa_admin_id_token'));
    const groups = access['cognito:groups'] || id['cognito:groups'] || [];
    return Array.isArray(groups) && groups.includes('Admin');
  }

  function currentPage() {
    const app = qs('[data-admin-app]');
    return app ? app.getAttribute('data-admin-page') : '';
  }

  function setStatus(kind, title, detail) {
    const banner = qs('[data-status-banner]');
    if (!banner) return;
    banner.className = 'status-banner';
    if (kind) banner.classList.add(kind);
    banner.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(detail || '')}</span>`;
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function rowId(row) {
    const firstStrong = row.querySelector('td strong');
    return firstStrong ? firstStrong.textContent.trim() : '';
  }

  function ensureDeleteButtons() {
    const page = currentPage();
    const cfg = PAGE_CONFIG[page];
    if (!cfg) return;

    // Only System Administrator/Admin gets the delete button. Standard users never see it.
    if (!isAdmin()) return;

    qsa('[data-table-body] tr[data-row-index]').forEach((row) => {
      if (row.querySelector('[data-batch59b-delete]')) return;
      const id = rowId(row);
      if (!id || id === '—') return;
      const actionCell = row.querySelector('td:last-child');
      if (!actionCell) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'table-action-link table-action-delete batch59b-delete-action';
      button.setAttribute('data-batch59b-delete', 'true');
      button.setAttribute('data-record-id', id);
      button.setAttribute('data-record-label', cfg.noun);
      button.textContent = 'Delete';
      actionCell.appendChild(document.createTextNode(' '));
      actionCell.appendChild(button);
    });
  }

  async function deleteRecord(id, cfg) {
    if (!window.RSAAdminApi) throw new Error('Admin API client is not loaded.');
    const base = window.RSAAdminApi.getApiBaseUrl().replace(/\/$/, '');
    const url = `${base}${cfg.endpoint}/${encodeURIComponent(id)}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        ...(typeof window.RSAAdminApi.getAuthHeaders === 'function' ? window.RSAAdminApi.getAuthHeaders() : {}),
      },
    });
    if (!response.ok) {
      let detail = '';
      try {
        const payload = await response.json();
        detail = payload && payload.detail ? payload.detail : JSON.stringify(payload);
      } catch (error) {
        detail = await response.text().catch(() => '');
      }
      throw new Error(detail || `${response.status} ${response.statusText}`);
    }
  }

  document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-batch59b-delete]');
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();

    const page = currentPage();
    const cfg = PAGE_CONFIG[page];
    const id = button.getAttribute('data-record-id') || '';
    if (!cfg || !id) return;

    const confirmed = window.confirm(`Delete this ${cfg.noun}? This is permanent and only allowed when dependency checks pass.`);
    if (!confirmed) return;

    try {
      button.disabled = true;
      setStatus('', `Deleting ${cfg.noun}…`, id);
      await deleteRecord(id, cfg);
      setStatus('is-success', `${cfg.noun.charAt(0).toUpperCase() + cfg.noun.slice(1)} deleted.`, id);
      const refresh = qs('[data-refresh-list]');
      if (refresh) refresh.click();
      else window.location.reload();
    } catch (error) {
      console.error(error);
      button.disabled = false;
      setStatus('is-warning', `Unable to delete ${cfg.noun}.`, error.message || 'The backend rejected this delete action.');
      window.alert(error.message || `Unable to delete ${cfg.noun}.`);
    }
  }, true);

  function scheduleEnsureDeleteButtons() {
    [0, 75, 250, 700, 1500].forEach((delay) => window.setTimeout(ensureDeleteButtons, delay));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleEnsureDeleteButtons);
  } else {
    scheduleEnsureDeleteButtons();
  }
  document.addEventListener('rsa-admin-role-ready', scheduleEnsureDeleteButtons);

  const target = qs('[data-table-body]') || document.body;
  if (target) {
    const observer = new MutationObserver(() => window.setTimeout(ensureDeleteButtons, 0));
    observer.observe(target, { childList: true, subtree: true });
  }

  window.RSABatch59BDeleteActions = { marker: MARKER, ensureDeleteButtons };
}());
'''

CSS_PATCH = r'''
/* batch59b-full-admin-delete-actions */
.table-action-delete,
.batch59b-delete-action {
  color: #b91c1c !important;
  border-color: rgba(185, 28, 28, 0.26) !important;
  background: rgba(254, 242, 242, 0.78) !important;
}

.table-action-delete:hover,
.batch59b-delete-action:hover {
  background: #fee2e2 !important;
  color: #991b1b !important;
}
'''

DOC_TEXT = """# Phase 8 Batch 59B — Admin-only Restricted/Delete Actions

Status: targeted full local patch package.

## Purpose

Batch 59B adds real Admin-only delete behavior for approved catalog records while preserving the non-delete rule for leads.

## Implemented in this package

- Adds backend `DELETE` routes protected by `require_admin_group` for:
  - Products
  - Brands
  - Categories
  - Key Features
- Adds repository delete helpers for mock and DynamoDB repositories.
- Adds dependency checks before delete:
  - Brand delete is blocked when any product uses the brand.
  - Category delete is blocked when any product uses the category.
  - Key Feature delete is blocked when any product uses that feature text.
- Adds Admin-only Delete buttons to catalog admin tables through `admin-catalog.js` only.
- Standard users do not receive Delete buttons.
- Customers, bookings, and inquiries remain non-delete for traceability.

## Not included

- No customer/booking/inquiry delete.
- No DynamoDB table changes.
- No Cognito schema/group changes.
- No S3/EC2/Route 53/CloudFront change.
- No global admin HTML rewrite.

## Browser verification

1. Login as System Administrator.
2. Open Brands.
3. Verify unused brand shows Delete.
4. Delete an unused brand and confirm it disappears after refresh.
5. Try deleting a brand used by products; backend should block it.
6. Login as Standard User and verify Delete is hidden.
"""


def main() -> None:
    print(f"[start] Applying {MARKER}")
    for label, path in FILES.items():
        require(path, label)

    cleanup_discarded_safe_v2()

    for label, snippet in REPO_PATCHES.items():
        append_once(FILES[label], MARKER, snippet, label)
    for label, snippet in SERVICE_PATCHES.items():
        append_once(FILES[label], MARKER, snippet, label)
    for label, snippet in ROUTE_PATCHES.items():
        append_once(FILES[label], MARKER, snippet, label)

    append_once(FILES["admin_catalog"], MARKER, CATALOG_JS_PATCH, "admin catalog delete UI")
    append_once(ADMIN_CSS, MARKER, CSS_PATCH, "admin delete CSS")

    write(DOC, DOC_TEXT)

    print(f"[done] {MARKER} applied.")
    print("[done] Admin-only catalog delete actions added for Products, Brands, Categories, and Key Features.")
    print("[done] Brand/category/key-feature dependency checks are enforced before delete.")
    print("[done] Customers, bookings, and inquiries remain non-delete.")
    print("[done] No DynamoDB table, Cognito schema, S3, EC2, Route 53, CloudFront, or paid notification change.")


if __name__ == "__main__":
    main()
