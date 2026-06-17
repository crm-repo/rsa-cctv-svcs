from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_API = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-api.js"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_v6b_admin_api_auth_header.md"
MARKER = "batch59a-hotfix-v6b-admin-api-auth-header"

FIXED_REQUEST = """  async function request(path, options = {}) {
    const base = getApiBaseUrl();
    const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
    const { headers: optionHeaders = {}, ...fetchOptions } = options || {};
    const hasBody = Object.prototype.hasOwnProperty.call(fetchOptions, 'body') && fetchOptions.body != null;
    const response = await fetch(url, {
      ...fetchOptions,
      headers: {
        Accept: 'application/json',
        ...getAuthHeaders(),
        ...(hasBody ? { 'Content-Type': 'application/json' } : {}),
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

DOC_TEXT = """# Phase 8 Batch 59A Hotfix v6B — Admin API Auth Header Preservation

Status: targeted local auth-header hotfix

## Purpose

Fix Settings > Users create/update/reset/enable/disable requests returning `401 Unauthorized` while user listing works.

## Root cause

The shared admin API request helper built authenticated headers, then spread `...options` after the `headers` object. When POST/PUT code supplied `options.headers`, the final spread could replace the authenticated headers and drop the bearer token.

## Fix

`frontend/admin/assets/js/admin-api.js` now separates `options.headers` from the rest of `options`, spreads fetch options first, and then builds the final headers object last.

## Changed files

```text
frontend/admin/assets/js/admin-api.js
backend/scripts/apply_batch59a_hotfix_v6b_admin_api_auth_header.py
docs/phase8_batch59a_hotfix_v6b_admin_api_auth_header.md
```

## Not changed

```text
Cognito groups
IAM policies
FastAPI routes
DynamoDB
S3
EC2/Nginx
Users UI layout
```
"""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace('\\', '/')
    except ValueError:
        return str(path)


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='')
    print(f"[ok] Wrote {rel(path)}")


def patch_admin_api() -> None:
    if not ADMIN_API.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_API)}")

    text = read(ADMIN_API)
    if "const { headers: optionHeaders = {}, ...fetchOptions } = options || {};" in text:
        print(f"[skip] {rel(ADMIN_API)} already preserves Authorization headers after options split")
        return

    # Replace only the request() helper, stopping before getItems(). This is deliberately broader
    # than v6 because the existing file may have different blank lines/spacing.
    pattern = re.compile(
        r"  async function request\(path, options = \{\}\) \{[\s\S]*?\n  \}\n\n  function getItems",
        flags=re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(
            "[fail] Could not locate admin-api.js request() helper. No files changed. "
            "Paste frontend/admin/assets/js/admin-api.js for review."
        )

    replacement = FIXED_REQUEST + "\n  function getItems"
    updated = text[:match.start()] + replacement + text[match.end():]
    write(ADMIN_API, updated)

    verify = read(ADMIN_API)
    required = [
        "const { headers: optionHeaders = {}, ...fetchOptions } = options || {};",
        "...getAuthHeaders(),",
        "...optionHeaders",
        "...fetchOptions,"
    ]
    missing = [item for item in required if item not in verify]
    if missing:
        raise SystemExit(f"[fail] Patch verification failed. Missing: {missing}")
    print(f"[ok] Patched {rel(ADMIN_API)}")


def main() -> None:
    print(f"[start] Applying {MARKER}")
    patch_admin_api()
    write(DOC, DOC_TEXT)
    print(f"[done] {MARKER} applied.")
    print("[done] Admin API request helper now preserves Authorization bearer headers for POST/PUT requests.")
    print("[done] No Cognito/IAM/backend/DynamoDB/S3/EC2 change.")


if __name__ == '__main__':
    main()
