"""Batch 54C hotfix: allow package/static products without a fixed price.

This script makes a targeted, idempotent edit to backend/app/models/product.py:
    price: float
becomes:
    price: Optional[float] = None

Run from the project root:
    python backend/scripts/patch_product_price_optional.py
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_MODEL_PATH = PROJECT_ROOT / "backend" / "app" / "models" / "product.py"

OLD = "    price: float\n"
NEW = "    price: Optional[float] = None\n"


def main() -> int:
    if not PRODUCT_MODEL_PATH.exists():
        print(f"ERROR: product model not found: {PRODUCT_MODEL_PATH}")
        return 1

    text = PRODUCT_MODEL_PATH.read_text(encoding="utf-8")
    if NEW in text:
        print("OK: product price is already optional.")
        return 0

    if OLD not in text:
        print("ERROR: expected line not found: '    price: float'")
        print("Please inspect backend/app/models/product.py manually.")
        return 1

    PRODUCT_MODEL_PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"Updated: {PRODUCT_MODEL_PATH}")
    print("Changed Product.price from required float to Optional[float] = None.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
