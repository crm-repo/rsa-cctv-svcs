from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PAYLOAD = SCRIPT_DIR / "batch59b_safe"
MARKER = "batch59b-safe-admin-only-restricted-actions"

ADMIN_AUTH_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-auth.js"
HEADER_UTILS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-header-utilities-55d.js"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
TARGET_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-restricted-actions-59b-safe.js"
DOC = ROOT / "docs" / "phase8_batch59b_admin_only_restricted_actions.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


def append_once(path: Path, snippet: str, label: str, comment_prefix: str = "//") -> bool:
    if not path.exists():
        print(f"[skip] Missing {rel(path)}; {label} not patched.")
        return False
    text = read(path)
    if MARKER in text:
        print(f"[skip] {label} already contains {MARKER}")
        return True
    suffix = f"\n\n{comment_prefix} {MARKER}\n{snippet.strip()}\n"
    write(path, text.rstrip() + suffix)
    return True


def main() -> None:
    print(f"[start] Applying {MARKER}")

    js_source = PAYLOAD / "admin-restricted-actions-59b-safe.js"
    css_source = PAYLOAD / "admin-restricted-actions-59b-safe.css"
    if not js_source.exists() or not css_source.exists():
        raise SystemExit("[fail] Missing Batch 59B safe payload files.")

    TARGET_JS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(js_source, TARGET_JS)
    print(f"[ok] Copied {js_source.name} -> {rel(TARGET_JS)}")

    js = read(js_source)
    patched_any_shared_js = False
    patched_any_shared_js = append_once(ADMIN_AUTH_JS, js, "admin auth shared guard") or patched_any_shared_js
    patched_any_shared_js = append_once(HEADER_UTILS_JS, js, "header utility shared guard") or patched_any_shared_js

    if not patched_any_shared_js:
        raise SystemExit(
            "[fail] Could not find a shared admin JS file to patch. No admin HTML was changed. "
            "Paste frontend/admin/assets/js/admin-auth.js and admin-header-utilities-55d.js paths/status for review."
        )

    css = read(css_source)
    append_once(ADMIN_CSS, css, "admin restricted-action CSS", comment_prefix="/*")

    doc_text = """# Phase 8 Batch 59B — Admin-only Restricted/Delete Actions\n\nStatus: Safe local patch package prepared.\n\n## Purpose\n\nBatch 59B makes admin-only/destructive controls role-aware without rewriting existing admin HTML pages.\n\n## Guardrails\n\n- Do not add delete behavior to lead records.\n- Bookings, inquiries, and customer/lead records remain non-delete for traceability.\n- Standard users should not see Settings or destructive/delete controls.\n- Backend route protection remains the source of truth when a protected endpoint exists.\n- This package does not change DynamoDB tables, Cognito schema, S3, EC2, Route 53, CloudFront, or paid notifications.\n\n## Implementation style\n\nThis package appends a safe role-aware guard to already-loaded shared admin JavaScript files only. It does not inject scripts into every admin HTML page and does not rewrite page initialization.\n\n## Files\n\n- `frontend/admin/assets/js/admin-restricted-actions-59b-safe.js`\n- `frontend/admin/assets/js/admin-auth.js` marker append, if present\n- `frontend/admin/assets/js/admin-header-utilities-55d.js` marker append, if present\n- `frontend/admin/assets/css/admin.css` marker append, if present\n\n## Verification\n\nRun:\n\n```powershell\npython .\\backend\\scripts\\verify_batch59b_safe_admin_only_restricted_actions.py\n```\n\nThen browser-test as Admin and Standard.\n"""
    write(DOC, doc_text)

    print(f"[done] {MARKER} applied.")
    print("[done] Safe 59B guard appended only to shared admin JS/CSS; no admin HTML pages were rewritten.")
    print("[done] Standard users hide Settings/delete controls; lead records remain non-delete.")
    print("[done] No backend/IAM/Cognito/DynamoDB/S3/EC2 change.")


if __name__ == "__main__":
    main()
