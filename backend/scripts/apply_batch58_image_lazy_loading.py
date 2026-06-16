#!/usr/bin/env python3
"""
Batch 58 - Image Optimization / Lazy Loading

Project-safe patcher. Adds lazy-loading attributes to non-critical public images.
It intentionally avoids hero/header/logo image markup and does not touch backend,
admin upload behavior, S3 paths, or DynamoDB records.

Usage from project root:
  python scripts/apply_batch58_image_lazy_loading.py --dry-run
  python scripts/apply_batch58_image_lazy_loading.py --execute
"""
from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path

BATCH_MARKER = "batch58-image-lazy-loading"
PUBLIC_HTML_FILES = [
    "index.html",
    "products.html",
    "promotions.html",
    "brands.html",
    "about.html",
    "services.html",
    "contact-us.html",
    "booking.html",
]
JS_FUNCTIONS_TO_PATCH = [
    "renderProductCard",
    "renderFeaturedCard",
    "renderPromoCard",
    "renderBrandCard",
    "renderAboutPage",
    "renderContactInfo",
]

IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)


def add_lazy_attrs_to_img_tag(tag: str) -> tuple[str, bool]:
    """Return patched img tag and whether it changed."""
    original = tag
    if re.search(r"\bloading\s*=", tag, re.IGNORECASE) and re.search(r"\bdecoding\s*=", tag, re.IGNORECASE):
        return tag, False

    attrs = []
    if not re.search(r"\bloading\s*=", tag, re.IGNORECASE):
        attrs.append('loading="lazy"')
    if not re.search(r"\bdecoding\s*=", tag, re.IGNORECASE):
        attrs.append('decoding="async"')

    if not attrs:
        return tag, False

    tag = re.sub(r"<img\b", "<img " + " ".join(attrs), tag, count=1, flags=re.IGNORECASE)
    return tag, tag != original


def patch_all_img_tags(text: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        new_tag, changed = add_lazy_attrs_to_img_tag(match.group(0))
        if changed:
            count += 1
        return new_tag

    return IMG_RE.sub(repl, text), count


def is_critical_html_image_context(prefix: str, tag: str) -> bool:
    """Skip likely above-the-fold / critical images in static HTML fallback."""
    context = (prefix[-700:] + " " + tag).lower()
    critical_tokens = [
        "navbar",
        "nav-",
        "header",
        "logo",
        "hero",
        "-hero-",
        "hero-section",
        "promotions-hero",
        "brands-hero",
        "home-hero",
        "about-page-hero",
        "services-page-hero",
        "contact-page-hero",
        "booking-page-hero",
        "mobile-menu",
    ]
    return any(token in context for token in critical_tokens)


def patch_html_file(text: str) -> tuple[str, int, int]:
    changed_count = 0
    skipped_count = 0
    output = []
    last = 0

    for match in IMG_RE.finditer(text):
        start, end = match.span()
        tag = match.group(0)
        output.append(text[last:start])

        if is_critical_html_image_context(text[:start], tag):
            output.append(tag)
            skipped_count += 1
        else:
            new_tag, changed = add_lazy_attrs_to_img_tag(tag)
            output.append(new_tag)
            if changed:
                changed_count += 1

        last = end

    output.append(text[last:])
    return "".join(output), changed_count, skipped_count


def find_function_block(text: str, function_name: str) -> tuple[int, int] | None:
    pattern = re.compile(rf"(^\s*function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{)", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None

    start = match.start()
    brace_start = text.find("{", match.start())
    if brace_start == -1:
        return None

    depth = 0
    in_string = None
    escape = False
    in_line_comment = False
    in_block_comment = False

    for index in range(brace_start, len(text)):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
            continue

        if in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
            continue

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue

        if char == "/" and nxt == "/":
            in_line_comment = True
            continue
        if char == "/" and nxt == "*":
            in_block_comment = True
            continue
        if char in ('"', "'", "`"):
            in_string = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1

    return None


def patch_js_file(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for function_name in JS_FUNCTIONS_TO_PATCH:
        block_range = find_function_block(text, function_name)
        if not block_range:
            counts[function_name] = -1
            continue
        start, end = block_range
        block = text[start:end]
        patched, count = patch_all_img_tags(block)
        if count:
            text = text[:start] + patched + text[end:]
        counts[function_name] = count

    # Add a marker comment without changing runtime behavior.
    if BATCH_MARKER not in text:
        marker_comment = f'/* {BATCH_MARKER}: non-critical rendered images use loading="lazy" and decoding="async". */\n'
        text = marker_comment + text
    return text, counts


def backup_file(path: Path, backup_root: Path) -> Path:
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / path.name
    counter = 1
    while backup_path.exists():
        backup_path = backup_root / f"{path.stem}.{counter}{path.suffix}"
        counter += 1
    shutil.copy2(path, backup_path)
    return backup_path


def write_if_execute(path: Path, new_text: str, execute: bool, backup_root: Path) -> Path | None:
    if not execute:
        return None
    backup = backup_file(path, backup_root)
    path.write_text(new_text, encoding="utf-8")
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 58 image lazy-loading patcher")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only.")
    parser.add_argument("--execute", action="store_true", help="Write changes.")
    args = parser.parse_args()

    if args.dry_run == args.execute:
        raise SystemExit("Choose exactly one: --dry-run or --execute")

    root = Path(args.project_root).resolve()
    frontend = root / "frontend"
    main_js = frontend / "assets" / "js" / "main.js"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    review_dir = root / "docs" / "review"
    backup_root = review_dir / f"batch58_backups_{timestamp}"
    report_lines = [
        "Batch 58 - Image Optimization / Lazy Loading",
        f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}",
        f"Project root: {root}",
        "Scope: public frontend HTML + selected existing main.js render functions",
        "Skipped: hero/header/logo critical static HTML image contexts",
        "Not touched: backend, admin upload logic, DynamoDB, S3 paths",
        "",
    ]

    total_changes = 0

    if main_js.exists():
        original = main_js.read_text(encoding="utf-8")
        patched, counts = patch_js_file(original)
        change_count = sum(count for count in counts.values() if count > 0)
        total_changes += change_count + (0 if BATCH_MARKER in original else 1)
        report_lines.append(f"JS: {main_js.relative_to(root)}")
        for fn, count in counts.items():
            status = "not found" if count == -1 else f"{count} img tag(s) updated"
            report_lines.append(f"  {fn}: {status}")
        if patched != original:
            backup = write_if_execute(main_js, patched, args.execute, backup_root)
            if backup:
                report_lines.append(f"  backup: {backup.relative_to(root)}")
        else:
            report_lines.append("  no changes needed")
        report_lines.append("")
    else:
        report_lines.append(f"WARN missing JS file: {main_js}")

    for html_name in PUBLIC_HTML_FILES:
        path = frontend / html_name
        if not path.exists():
            report_lines.append(f"WARN missing HTML file: frontend/{html_name}")
            continue
        original = path.read_text(encoding="utf-8")
        patched, changed_count, skipped_count = patch_html_file(original)
        total_changes += changed_count
        report_lines.append(f"HTML: {path.relative_to(root)}")
        report_lines.append(f"  {changed_count} img tag(s) updated")
        report_lines.append(f"  {skipped_count} critical/fallback img tag(s) skipped")
        if patched != original:
            backup = write_if_execute(path, patched, args.execute, backup_root)
            if backup:
                report_lines.append(f"  backup: {backup.relative_to(root)}")
        else:
            report_lines.append("  no changes needed")
        report_lines.append("")

    report_lines.append(f"Total planned/actual updates: {total_changes}")
    report_lines.append("Result: no functional data/API behavior changed.")

    review_dir.mkdir(parents=True, exist_ok=True)
    report_path = review_dir / "batch58_image_lazy_loading_report.txt"
    if args.execute:
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print("EXECUTE complete")
        print(f"Report: {report_path}")
        print(f"Backups: {backup_root}")
    else:
        print("\n".join(report_lines))
        print("DRY RUN only. No files changed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
