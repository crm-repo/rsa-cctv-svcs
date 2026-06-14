from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "frontend" / "admin"
PATCH_MARKER = "batch55c-admin-icons-static-only"

# Static-only icon update.
# Safety rules:
# - No new JavaScript file is created.
# - No script tag is added to any HTML page.
# - No MutationObserver or runtime DOM loop is introduced.
# - Files are edited as bytes so existing UTF-8 characters are not decoded/re-encoded.

ASCII_REPLACEMENTS: tuple[tuple[bytes, bytes], ...] = (
    # Brand icons: use Font Awesome solid certificate consistently.
    (b"fa-solid fa-tags", b"fa-solid fa-certificate"),
    (b"fa-solid fa-tag", b"fa-solid fa-certificate"),

    # Key Features icons: use Font Awesome solid star consistently.
    (b"fa-solid fa-list-check", b"fa-solid fa-star"),
    (b"fa-solid fa-sparkles", b"fa-solid fa-star"),

    # Product/package icons: keep/normalize to boxes-stacked.
    (b"fa-solid fa-box", b"fa-solid fa-boxes-stacked"),
    (b"fa-solid fa-box-open", b"fa-solid fa-boxes-stacked"),
    (b"fa-solid fa-cubes", b"fa-solid fa-boxes-stacked"),

    # Category icons: keep/normalize to layer-group.
    (b"fa-solid fa-shapes", b"fa-solid fa-layer-group"),
    (b"fa-solid fa-table-cells-large", b"fa-solid fa-layer-group"),

    # Customer icons: keep/normalize to users.
    (b"fa-solid fa-user-group", b"fa-solid fa-users"),
    (b"fa-solid fa-address-card", b"fa-solid fa-users"),
)

# Exact page-heading replacements. These are targeted to the page icon wrapper only.
# The replacement bytes are UTF-8 encoded once here; the files themselves are not re-encoded.
PAGE_HEADING_REPLACEMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "products.html": ((
        '<div class="page-icon">□</div>',
        '<div class="page-icon"><i class="fa-solid fa-boxes-stacked"></i></div>',
    ),),
    "categories.html": ((
        '<div class="page-icon">◇</div>',
        '<div class="page-icon"><i class="fa-solid fa-layer-group"></i></div>',
    ),),
    "brands.html": ((
        '<div class="page-icon">◈</div>',
        '<div class="page-icon"><i class="fa-solid fa-certificate"></i></div>',
    ),),
    "key-features.html": ((
        '<div class="page-icon">✦</div>',
        '<div class="page-icon"><i class="fa-solid fa-star"></i></div>',
    ),),
    "customers.html": ((
        '<div class="page-icon">☷</div>',
        '<div class="page-icon"><i class="fa-solid fa-users"></i></div>',
    ),),
}

# If a page heading already has an FA icon but with an older class, normalize only that exact wrapper.
PAGE_HEADING_FA_REPLACEMENTS: tuple[tuple[bytes, bytes], ...] = (
    (b'<div class="page-icon"><i class="fa-solid fa-tags"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-certificate"></i></div>'),
    (b'<div class="page-icon"><i class="fa-solid fa-list-check"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-star"></i></div>'),
    (b'<div class="page-icon"><i class="fa-solid fa-box"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-boxes-stacked"></i></div>'),
    (b'<div class="page-icon"><i class="fa-solid fa-box-open"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-boxes-stacked"></i></div>'),
    (b'<div class="page-icon"><i class="fa-solid fa-shapes"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-layer-group"></i></div>'),
    (b'<div class="page-icon"><i class="fa-solid fa-user-group"></i></div>', b'<div class="page-icon"><i class="fa-solid fa-users"></i></div>'),
)

TARGET_PATTERNS = [
    "frontend/admin/*.html",
    "frontend/admin/assets/js/admin-polish-v3.js",
    "frontend/admin/assets/js/admin-dashboard.js",
    "frontend/admin/assets/js/admin-catalog.js",
    "frontend/admin/assets/js/admin-cms.js",
    "frontend/admin/assets/js/admin-leads.js",
]

FORBIDDEN_LEFTOVERS = (
    b"admin-icon-consistency-55c.js",
    b"MutationObserver",
    b"batch55c-admin-icon-consistency-update",
)


def iter_targets() -> list[Path]:
    paths: list[Path] = []
    for pattern in TARGET_PATTERNS:
        paths.extend(ROOT.glob(pattern))
    return sorted(set(p for p in paths if p.is_file()))


def patch_file(path: Path) -> bool:
    data = path.read_bytes()
    original = data

    for old, new in ASCII_REPLACEMENTS:
        data = data.replace(old, new)

    if path.name in PAGE_HEADING_REPLACEMENTS:
        for old_text, new_text in PAGE_HEADING_REPLACEMENTS[path.name]:
            data = data.replace(old_text.encode("utf-8"), new_text.encode("utf-8"))

    for old, new in PAGE_HEADING_FA_REPLACEMENTS:
        data = data.replace(old, new)

    if data != original:
        path.write_bytes(data)
        print(f"[ok] Updated {path.relative_to(ROOT)}")
        return True
    return False


def assert_no_failed_icon_runtime() -> None:
    offenders: list[str] = []
    for path in sorted((ADMIN).glob("*.html")):
        data = path.read_bytes()
        if b"admin-icon-consistency-55c.js" in data:
            offenders.append(str(path.relative_to(ROOT)))
    failed_script = ADMIN / "assets/js/admin-icon-consistency-55c.js"
    if failed_script.exists():
        offenders.append(str(failed_script.relative_to(ROOT)))
    if offenders:
        raise SystemExit("[fail] Failed icon runtime still present: " + ", ".join(offenders))


def assert_no_forbidden_new_runtime() -> None:
    offenders: list[str] = []
    for path in iter_targets():
        data = path.read_bytes()
        for token in FORBIDDEN_LEFTOVERS:
            if token in data:
                offenders.append(f"{path.relative_to(ROOT)} contains {token.decode('ascii', errors='ignore')}")
    if offenders:
        raise SystemExit("[fail] Forbidden icon-runtime residue found:\n" + "\n".join(offenders))


def main() -> None:
    if not ADMIN.exists():
        raise SystemExit(f"[fail] Admin folder not found: {ADMIN}")

    changed = 0
    for path in iter_targets():
        if patch_file(path):
            changed += 1

    assert_no_failed_icon_runtime()
    assert_no_forbidden_new_runtime()

    print(f"[done] {PATCH_MARKER} applied. Files changed: {changed}")
    print("[done] Static icon classes only. No new JS file, no script tag, no observer, no backend/API/DynamoDB changes.")


if __name__ == "__main__":
    main()
