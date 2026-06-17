from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = "batch59b-safe-admin-only-restricted-actions"
TARGET_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-restricted-actions-59b-safe.js"
ADMIN_AUTH_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-auth.js"
HEADER_UTILS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-header-utilities-55d.js"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
DOC = ROOT / "docs" / "phase8_batch59b_admin_only_restricted_actions.md"
ADMIN_HTML_DIR = ROOT / "frontend" / "admin"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def ok(message: str) -> None:
    print(f"[ok] {message}")


def fail(message: str) -> None:
    raise SystemExit(f"[fail] {message}")


def main() -> None:
    print("[start] Verifying batch59b-safe-admin-only-restricted-actions")

    for path in [TARGET_JS, ADMIN_CSS, DOC]:
        if not path.exists():
            fail(f"Missing {rel(path)}")
        ok(f"Found {rel(path)}")

    if MARKER not in text(TARGET_JS):
        fail(f"Marker missing from {rel(TARGET_JS)}")
    ok("Restricted-action JS marker present in copied safe JS file.")

    shared_paths = [path for path in [ADMIN_AUTH_JS, HEADER_UTILS_JS] if path.exists()]
    if not shared_paths:
        fail("No shared admin JS files found: admin-auth.js / admin-header-utilities-55d.js")
    if not any(MARKER in text(path) for path in shared_paths):
        fail("Safe Batch 59B marker not found in any shared admin JS file.")
    ok("Safe Batch 59B marker found in shared admin JS.")

    if MARKER not in text(ADMIN_CSS):
        fail(f"CSS marker missing from {rel(ADMIN_CSS)}")
    ok("CSS marker present.")

    # Guard against the previous broken broad HTML injection approach.
    broken = []
    if ADMIN_HTML_DIR.exists():
        for html in ADMIN_HTML_DIR.glob("*.html"):
            h = text(html)
            if "admin-restricted-actions-59b.js" in h or "admin-restricted-actions-59b-safe.js" in h:
                broken.append(rel(html))
    if broken:
        fail("Batch 59B safe package should not inject into admin HTML pages. Found script tag in: " + ", ".join(broken))
    ok("No Batch 59B script tags injected into admin HTML pages.")

    print("[done] Batch 59B safe local file verification passed.")


if __name__ == "__main__":
    main()
