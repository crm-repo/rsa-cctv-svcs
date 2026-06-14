from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "frontend" / "admin"
PATCH_MARKER = b"batch55c-admin-icons-static-only-v2"

# This patch is intentionally icon-only.
# It edits existing admin HTML and existing admin-polish-v3.js only.
# It does not add any runtime script, observer, backend API, CSS, or DynamoDB change.

ICON_MAP = {
    "index": "fa-solid fa-gauge-high",
    "products": "fa-solid fa-box-open",
    "categories": "fa-solid fa-table-list",
    "brands": "fa-solid fa-certificate",
    "key-features": "fa-solid fa-star",
    "customers": "fa-solid fa-users",
    "bookings": "fa-solid fa-calendar-check",
    "inquiries": "fa-solid fa-file-circle-question",
    "about": "fa-solid fa-address-card",
    "project-gallery": "fa-solid fa-images",
    "services": "fa-solid fa-screwdriver-wrench",
    "contact-us": "fa-solid fa-address-book",
}

LABEL_MAP = {
    "index": "Dashboard",
    "products": "Products",
    "categories": "Categories",
    "brands": "Brands",
    "key-features": "Key Features",
    "customers": "Customers",
    "bookings": "Bookings",
    "inquiries": "Inquiries",
    "about": "About Us",
    "project-gallery": "Project Gallery",
    "services": "Services",
    "contact-us": "Contact Us",
}

PAGE_HEADING_FILES = {
    "products.html": "products",
    "categories.html": "categories",
    "brands.html": "brands",
    "key-features.html": "key-features",
    "customers.html": "customers",
    "bookings.html": "bookings",
    "inquiries.html": "inquiries",
    "about.html": "about",
    "project-gallery.html": "project-gallery",
    "services.html": "services",
    "contact-us.html": "contact-us",
}

METRIC_CARDS = {
    "Total Products": "products",
    "Active Brands": "brands",
    "Bookings": "bookings",
    "Inquiries": "inquiries",
    "Customers": "customers",
}

FORBIDDEN_PRESTATE_TOKENS = [
    b"admin-icon-consistency-55c.js",
    b"batch55c-admin-icon-consistency-update",
]

FORBIDDEN_RESULT_TOKENS = FORBIDDEN_PRESTATE_TOKENS + [
    b"fa-boxes-stackedes-stacked",
]

MOJIBAKE_TOKENS = [
    b"\xc3\xa2",  # character 'a with circumflex' in UTF-8, typical mojibake prefix
    b"\xef\xbf\xbd",  # replacement character
]

ICON_TAG_RE = rb'<i class="fa-solid fa-[a-z0-9-]+"></i>'


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def write_bytes(path: Path, data: bytes, apply: bool) -> None:
    if apply:
        path.write_bytes(data)


def fail_if_bad_prestate() -> None:
    if not ADMIN.exists():
        raise SystemExit(f"[fail] Admin folder not found: {ADMIN}")

    offenders: list[str] = []
    for path in list(ADMIN.glob("*.html")) + list((ADMIN / "assets/js").glob("*.js")):
        data = path.read_bytes()
        for token in FORBIDDEN_PRESTATE_TOKENS:
            if token in data:
                offenders.append(f"{rel(path)} contains {token.decode('ascii', errors='ignore')}")
        for token in MOJIBAKE_TOKENS:
            if token in data:
                offenders.append(f"{rel(path)} still contains mojibake/replacement characters; rollback to hotfix v2 and re-apply v3 first")
    bad_runtime = ADMIN / "assets/js/admin-icon-consistency-55c.js"
    if bad_runtime.exists():
        offenders.append(rel(bad_runtime))
    if offenders:
        raise SystemExit("[fail] Preflight stopped. Fix rollback first:\n" + "\n".join(offenders))


def icon_html(icon: str) -> bytes:
    return f'<i class="{icon}"></i>'.encode("ascii")


def replace_nav_item_icon(data: bytes, key: str) -> tuple[bytes, int]:
    href = f"./{key}.html".encode("ascii")
    if key == "index":
        href = b"./index.html"
    label = LABEL_MAP[key].encode("ascii")
    icon = icon_html(ICON_MAP[key])

    # Match existing sidebar nav item and replace only nav-icon content.
    pattern = (
        rb'(<a class="nav-item[^\"]*" href="' + re.escape(href) +
        rb'"><span class="nav-icon">)(?:' + ICON_TAG_RE + rb'|[^<]*)(</span><span>' +
        re.escape(label) + rb'</span></a>)'
    )
    data, count = re.subn(pattern, rb'\1' + icon + rb'\2', data)
    return data, count


def replace_page_heading_icon(data: bytes, key: str) -> tuple[bytes, int]:
    icon = icon_html(ICON_MAP[key])
    pattern = rb'<div class="page-icon">[\s\S]*?</div>'
    replacement = b'<div class="page-icon">' + icon + b'</div>'
    data, count = re.subn(pattern, replacement, data, count=1)
    return data, count


def replace_metric_card_icon(data: bytes, title: str, key: str) -> tuple[bytes, int]:
    icon = icon_html(ICON_MAP[key])
    # Match one complete metric-card that contains this title. Do not cross into another card.
    title_b = re.escape(title.encode("ascii"))
    card_pattern = rb'<article class="metric-card">(?:(?!</article>)[\s\S])*?<p>' + title_b + rb'</p>(?:(?!</article>)[\s\S])*?</article>'

    def replace_inside_card(match: re.Match[bytes]) -> bytes:
        card = match.group(0)
        icon_pattern = rb'(<span class="metric-icon">)(?:' + ICON_TAG_RE + rb'|(?:(?!</span>)[\s\S])*)(</span>)'
        updated, icon_count = re.subn(icon_pattern, rb'\1' + icon + rb'\2', card, count=1)
        return updated if icon_count else card

    data, count = re.subn(card_pattern, replace_inside_card, data, count=1)
    return data, count


def patch_html(path: Path, apply: bool) -> bool:
    original = read_bytes(path)
    data = original
    changes = 0

    for key in ICON_MAP:
        data, n = replace_nav_item_icon(data, key)
        changes += n

    page_key = PAGE_HEADING_FILES.get(path.name)
    if page_key:
        data, n = replace_page_heading_icon(data, page_key)
        changes += n

    if path.name == "index.html":
        for title, key in METRIC_CARDS.items():
            data, n = replace_metric_card_icon(data, title, key)
            changes += n

    if data != original:
        write_bytes(path, data, apply)
        print(f"[ok] {'Would update' if not apply else 'Updated'} {rel(path)} ({changes} icon replacements)")
        return True
    return False


def patch_polish_v3_js(path: Path, apply: bool) -> bool:
    if not path.exists():
        return False
    original = read_bytes(path)
    data = original
    changes = 0

    for key, icon in ICON_MAP.items():
        label = LABEL_MAP[key].encode("ascii")
        href = f"./{key}.html".encode("ascii")
        if key == "index":
            href = b"./index.html"
        icon_b = icon.encode("ascii")

        # NAV_SPEC object format in admin-polish-v3.js.
        pattern = (
            rb"(label: '" + re.escape(label) + rb"', href: '" + re.escape(href) + rb"', icon: ')[^']*(')"
        )
        data, n = re.subn(pattern, rb"\1" + icon_b + rb"\2", data)
        changes += n

        # Fallback for generated nav strings if present in another existing JS block.
        pattern2 = (
            rb'(<a class="nav-item[^\"]*" href="' + re.escape(href) +
            rb'"><span class="nav-icon"><i class=")[^\"]*("></i></span><span>' + re.escape(label) + rb'</span></a>)'
        )
        data, n = re.subn(pattern2, rb"\1" + icon_b + rb"\2", data)
        changes += n

    if data != original:
        write_bytes(path, data, apply)
        print(f"[ok] {'Would update' if not apply else 'Updated'} {rel(path)} ({changes} icon replacements)")
        return True
    return False


def assert_result() -> None:
    offenders: list[str] = []
    targets = list(ADMIN.glob("*.html")) + [ADMIN / "assets/js/admin-polish-v3.js"]
    for path in targets:
        if not path.exists():
            continue
        data = path.read_bytes()
        for token in FORBIDDEN_RESULT_TOKENS:
            if token in data:
                offenders.append(f"{rel(path)} contains forbidden token {token.decode('ascii', errors='ignore')}")
    if offenders:
        raise SystemExit("[fail] Forbidden icon residue remains:\n" + "\n".join(offenders))


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch 55C icon-only static patch v2")
    parser.add_argument("--apply", action="store_true", help="write changes to disk")
    parser.add_argument("--dry-run", action="store_true", help="show files that would change without writing")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        args.apply = True

    fail_if_bad_prestate()

    changed = 0
    for path in sorted(ADMIN.glob("*.html")):
        if patch_html(path, args.apply):
            changed += 1

    if patch_polish_v3_js(ADMIN / "assets/js/admin-polish-v3.js", args.apply):
        changed += 1

    if args.apply:
        assert_result()

    mode = "dry-run" if args.dry_run and not args.apply else "applied"
    print(f"[done] {PATCH_MARKER.decode('ascii')} {mode}. Files changed: {changed}")
    print("[done] Icon-only change: existing HTML icon tags and existing admin-polish-v3.js icon strings only.")
    print("[done] No new JS file, no script tag, no observer, no CSS, no backend/API/DynamoDB change.")


if __name__ == "__main__":
    main()
