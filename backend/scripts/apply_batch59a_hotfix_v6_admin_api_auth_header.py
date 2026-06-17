from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_API = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-api.js"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_v6_admin_api_auth_header.md"

BROKEN_SNIPPET = """  async function request(path, options = {}) {
    const base = getApiBaseUrl();
    const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
    const response = await fetch(url, {
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {})
      },
      ...options
    });
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`${response.status} ${response.statusText}${text ? ` - ${text}` : ''}`);
    }
    return response.json();
  }
"""

FIXED_SNIPPET = """  async function request(path, options = {}) {
    const base = getApiBaseUrl();
    const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
    const { headers: optionHeaders = {}, ...fetchOptions } = options || {};
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...optionHeaders
      }
    });
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`${response.status} ${response.statusText}${text ? ` - ${text}` : ''}`);
    }
    return response.json();
  }
"""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def patch_admin_api() -> None:
    if not ADMIN_API.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_API)}")
    text = ADMIN_API.read_text(encoding="utf-8")
    if "const { headers: optionHeaders = {}, ...fetchOptions } = options || {};" in text:
        print(f"[skip] {rel(ADMIN_API)} already preserves auth headers for POST/PUT requests")
        return
    if BROKEN_SNIPPET not in text:
        raise SystemExit(
            "[fail] Could not find the Batch 59A admin-api request() block to patch. "
            "Do not guess. Paste frontend/admin/assets/js/admin-api.js request() function for review."
        )
    ADMIN_API.write_text(text.replace(BROKEN_SNIPPET, FIXED_SNIPPET, 1), encoding="utf-8", newline="")
    print(f"[ok] Patched {rel(ADMIN_API)}")


def write_doc() -> None:
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("""# Phase 8 Batch 59A Hotfix v6 — Admin API Auth Header Preservation

## Purpose

Fix Settings > Users create/update/reset/enable/disable requests returning `401 Unauthorized` even when the current admin user can list Cognito users.

## Root cause

`frontend/admin/assets/js/admin-api.js` built an authenticated headers object, but then spread `...options` after the headers object. For POST/PUT requests where `options.headers` existed, the final spread replaced the authenticated headers and dropped the `Authorization` bearer token.

GET `/admin/users` could still work, while POST `/admin/users` failed with `401 Unauthorized`.

## Changed files

```text
frontend/admin/assets/js/admin-api.js
backend/scripts/apply_batch59a_hotfix_v6_admin_api_auth_header.py
docs/phase8_batch59a_hotfix_v6_admin_api_auth_header.md
```

## Not changed

```text
Cognito groups
IAM policies
FastAPI routes
DynamoDB
S3
EC2/Nginx
Admin Users UI layout
```

## Expected result

After hard refresh and login, Add User should send the bearer token and reach the backend create-user route. If creation still fails, the next error should be the actual Cognito/AdminCreateUser response rather than a frontend-auth-header 401.
""", encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(DOC)}")


def main() -> None:
    patch_admin_api()
    write_doc()
    print("[done] batch59a-hotfix-v6-admin-api-auth-header applied.")
    print("[done] POST/PUT admin API requests now preserve Authorization bearer headers.")
    print("[done] No Cognito/IAM/backend/DynamoDB/S3/EC2 change.")


if __name__ == "__main__":
    main()
