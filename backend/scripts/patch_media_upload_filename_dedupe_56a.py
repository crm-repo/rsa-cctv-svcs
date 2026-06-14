from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIA_SERVICE = ROOT / "backend" / "app" / "services" / "media_service.py"
DOC = ROOT / "docs" / "phase8_batch56a_media_upload_filename_dedupe.md"

HELPER = r'''

def _merge_slug_parts(*parts: str) -> str:
    """Merge slug parts while removing repeated boundary phrases.

    Example:
    dahua + full-color-4k-bullet-camera + bullet-camera
    -> dahua-full-color-4k-bullet-camera
    """

    merged_words: list[str] = []
    for part in parts:
        slug = _slugify(part)
        if not slug:
            continue
        words = [word for word in slug.split("-") if word]
        if not words:
            continue

        if len(words) <= len(merged_words) and merged_words[-len(words):] == words:
            continue

        overlap = 0
        max_overlap = min(len(merged_words), len(words))
        for size in range(max_overlap, 0, -1):
            if merged_words[-size:] == words[:size]:
                overlap = size
                break

        merged_words.extend(words[overlap:])

    return "-".join(merged_words)
'''

OLD_STEM = r'''def _stem_from_context(
    media_type: str,
    *,
    original_filename: str,
    slug_source: str | None = None,
    product_name: str | None = None,
    brand_name: str | None = None,
    feature_01: str | None = None,
    subcategory: str | None = None,
) -> str:
    uploaded_stem = PurePosixPath(original_filename).stem

    if media_type == "products":
        # Prefer the final admin product name if present; otherwise use the approved
        # brand + shortened feature_01 + subcategory naming source.
        if product_name:
            source = product_name
        else:
            parts = [brand_name, _shorten_slug(feature_01 or ""), subcategory]
            source = " ".join(str(part or "").strip() for part in parts if str(part or "").strip())
        if not source:
            source = slug_source or uploaded_stem
    elif media_type == "brands":
        source = brand_name or slug_source or uploaded_stem
    elif media_type == "project-gallery":
        source = slug_source or product_name or uploaded_stem or "project-gallery"
    elif media_type == "contact-persons":
        source = slug_source or brand_name or product_name or uploaded_stem or "contact-person"
    else:
        source = slug_source or uploaded_stem or media_type

    slug = _slugify(source)
    if not slug:
        slug = _slugify(uploaded_stem) or media_type
    return slug[:80].strip("-") or media_type
'''

NEW_STEM = r'''def _stem_from_context(
    media_type: str,
    *,
    original_filename: str,
    slug_source: str | None = None,
    product_name: str | None = None,
    brand_name: str | None = None,
    feature_01: str | None = None,
    subcategory: str | None = None,
) -> str:
    uploaded_stem = PurePosixPath(original_filename).stem

    if media_type == "products":
        # Prefer the final admin product name if present; otherwise use the approved
        # brand + shortened feature_01 + subcategory naming source. The fallback
        # merge removes repeated boundary phrases such as feature_01 ending with
        # "bullet camera" and subcategory also being "Bullet Camera".
        if product_name:
            source_slug = _slugify(product_name)
        else:
            source_slug = _merge_slug_parts(
                brand_name or "",
                _shorten_slug(feature_01 or ""),
                subcategory or "",
            )
        if not source_slug:
            source_slug = _slugify(slug_source or uploaded_stem)
    elif media_type == "brands":
        source_slug = _slugify(brand_name or slug_source or uploaded_stem)
    elif media_type == "project-gallery":
        source_slug = _slugify(slug_source or product_name or uploaded_stem or "project-gallery")
    elif media_type == "contact-persons":
        source_slug = _slugify(slug_source or brand_name or product_name or uploaded_stem or "contact-person")
    else:
        source_slug = _slugify(slug_source or uploaded_stem or media_type)

    if not source_slug:
        source_slug = _slugify(uploaded_stem) or media_type
    return source_slug[:80].strip("-") or media_type
'''


def main() -> None:
    if not MEDIA_SERVICE.exists():
        raise SystemExit(f"[fail] Missing expected file: {MEDIA_SERVICE}")

    text = MEDIA_SERVICE.read_text(encoding="utf-8")
    if "batch56a-media-upload-endpoint" not in text:
        raise SystemExit("[fail] Batch 56A media upload endpoint marker not found. Apply Batch 56A first.")

    changed = False

    if "def _merge_slug_parts(" not in text:
        anchor = "def _stem_from_context("
        if anchor not in text:
            raise SystemExit("[fail] Could not find _stem_from_context insertion point.")
        text = text.replace(anchor, HELPER + "\n" + anchor, 1)
        changed = True

    if OLD_STEM in text:
        text = text.replace(OLD_STEM, NEW_STEM, 1)
        changed = True
    elif NEW_STEM in text:
        print("[ok] _stem_from_context already has filename de-dup logic")
    else:
        raise SystemExit("[fail] Could not match _stem_from_context safely. Stop and review manually.")

    if changed:
        MEDIA_SERVICE.write_text(text, encoding="utf-8")
        print(f"[ok] patched {MEDIA_SERVICE.relative_to(ROOT)}")
    else:
        print("[ok] no changes needed")

    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(
        "# Phase 8 Batch 56A Filename Slug De-dup Hotfix\n\n"
        "This small backend-only hotfix refines the Batch 56A media upload filename builder.\n\n"
        "## Purpose\n\n"
        "Product upload filenames still use readable slug filenames with a short unique suffix and the original validated extension. "
        "When product fallback naming is based on brand + shortened feature_01 + subcategory, repeated boundary phrases are removed.\n\n"
        "Example: `dahua-full-color-4k-bullet-camera-bullet-camera-0f4f9f.png` becomes "
        "`dahua-full-color-4k-bullet-camera-0f4f9f.png`.\n\n"
        "## Scope\n\n"
        "- Backend filename builder only.\n"
        "- No admin form integration.\n"
        "- No frontend change.\n"
        "- No DynamoDB schema change.\n"
        "- No S3 bucket creation.\n",
        encoding="utf-8",
    )
    print(f"[ok] wrote {DOC.relative_to(ROOT)}")
    print("[done] batch56a-media-upload-filename-dedupe applied.")
    print("[done] Backend filename-builder only. No frontend/admin form, DynamoDB, S3 bucket, or API contract change.")


if __name__ == "__main__":
    main()
