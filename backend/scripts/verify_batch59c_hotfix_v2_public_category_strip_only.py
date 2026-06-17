from pathlib import Path

MARKER = "batch59c-hotfix-v2-public-category-strip-only"

checks = [
    (
        Path("frontend/assets/js/main.js"),
        [
            MARKER,
            'let productFilterButtons = Array.from(document.querySelectorAll(".product-filter-btn"));',
            "function renderPublicCategoryStripFromApi()",
            'fetchPagedApiItems("/api/categories", 50)',
            "function bindProductFilterButtons()",
            "await renderPublicCategoryStripFromApi();",
            "Unable to load public categories from API. Keeping static category buttons.",
        ],
    ),
    (
        Path("docs/phase8_batch59c_public_category_strip_dynamodb_binding.md"),
        [
            "Phase 8 Batch 59C",
            MARKER,
            "/api/categories",
            "No backend route change",
            "Static HTML category buttons remain as fallback",
        ],
    ),
]

print("[start] Verifying batch59c-hotfix-v2-public-category-strip-only")
failed = False
for path, markers in checks:
    if not path.exists():
        print(f"[fail] Missing {path}")
        failed = True
        continue
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            print(f"[fail] Missing marker in {path}: {marker}")
            failed = True
        else:
            print(f"[ok] {path} contains: {marker}")

if failed:
    raise SystemExit(1)

print("[done] batch59c-hotfix-v2-public-category-strip-only local file verification passed.")
