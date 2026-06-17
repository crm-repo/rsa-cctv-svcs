from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKER = "batch59b-full-admin-delete-actions"

CHECKS = [
    ROOT / "backend" / "app" / "routes" / "brands.py",
    ROOT / "backend" / "app" / "routes" / "categories.py",
    ROOT / "backend" / "app" / "routes" / "products.py",
    ROOT / "backend" / "app" / "routes" / "key_features.py",
    ROOT / "backend" / "app" / "services" / "brand_service.py",
    ROOT / "backend" / "app" / "services" / "category_service.py",
    ROOT / "backend" / "app" / "services" / "product_service.py",
    ROOT / "backend" / "app" / "services" / "key_feature_service.py",
    ROOT / "backend" / "app" / "repositories" / "brand_repository.py",
    ROOT / "backend" / "app" / "repositories" / "category_repository.py",
    ROOT / "backend" / "app" / "repositories" / "product_repository.py",
    ROOT / "backend" / "app" / "repositories" / "key_feature_repository.py",
    ROOT / "frontend" / "admin" / "assets" / "js" / "admin-catalog.js",
    ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css",
    ROOT / "docs" / "phase8_batch59b_admin_only_restricted_actions.md",
]

EXPECTED_TEXT = [
    (ROOT / "backend" / "app" / "routes" / "brands.py", '@router.delete("/admin/brands/{brand_id}"'),
    (ROOT / "backend" / "app" / "routes" / "categories.py", '@router.delete("/admin/categories/{category_id}"'),
    (ROOT / "backend" / "app" / "routes" / "products.py", '@router.delete("/admin/products/{product_id}"'),
    (ROOT / "backend" / "app" / "routes" / "key_features.py", '@router.delete("/admin/key-features/{key_feat_id}"'),
    (ROOT / "frontend" / "admin" / "assets" / "js" / "admin-catalog.js", "RSABatch59BDeleteActions"),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> None:
    print("[start] Verifying batch59b-full-admin-delete-actions")
    missing = [rel(path) for path in CHECKS if not path.exists()]
    if missing:
        raise SystemExit("[fail] Missing files: " + ", ".join(missing))

    missing_marker = []
    for path in CHECKS:
        text = path.read_text(encoding="utf-8")
        if MARKER not in text:
            missing_marker.append(rel(path))
    if missing_marker:
        raise SystemExit("[fail] Batch 59B marker missing from: " + ", ".join(missing_marker))

    for path, needle in EXPECTED_TEXT:
        text = path.read_text(encoding="utf-8")
        if needle not in text:
            raise SystemExit(f"[fail] Expected marker not found in {rel(path)}: {needle}")
        print(f"[ok] {needle} found in {rel(path)}")

    # The discarded safe-v2 broad guard should not remain active in shared JS.
    for path in [
        ROOT / "frontend" / "admin" / "assets" / "js" / "admin-auth.js",
        ROOT / "frontend" / "admin" / "assets" / "js" / "admin-header-utilities-55d.js",
    ]:
        if path.exists() and "admin-restricted-actions-59b-safe.js" in path.read_text(encoding="utf-8"):
            raise SystemExit(f"[fail] Discarded safe-v2 script reference still present in {rel(path)}")

    print("[done] Batch 59B full local file verification passed.")


if __name__ == "__main__":
    main()
