"""Batch 54C revised hotfix: package products without fixed prices use quotation flow.

This script performs two targeted, idempotent edits:
1. backend/app/models/product.py
   - Allows Product.price to be optional so package records without price do not
     break /api/products response loading.
2. frontend/assets/js/main.js
   - Renders package products without price as "Get Quotation" on the catalog grid.
   - Updates the product modal primary action to "Get Quotation" and links to
     contact-us.html for quote-only package products.

Run from the project root:
    python backend/scripts/patch_package_quotation_price.py
"""
from __future__ import annotations

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_MODEL_PATH = PROJECT_ROOT / "backend" / "app" / "models" / "product.py"
MAIN_JS_PATH = PROJECT_ROOT / "frontend" / "assets" / "js" / "main.js"

PATCH_MARKER = 'RSA_PACKAGE_QUOTATION_PATCH_VERSION = "batch54c-package-quotation"'


def ensure_optional_import(text: str) -> str:
    if "Optional" not in text.split("\n", 20)[0:20].__str__() and "Optional[float]" in text:
        pass

    if re.search(r"^from typing import .*\bOptional\b", text, flags=re.MULTILINE):
        return text

    typing_match = re.search(r"^(from typing import )(.+)$", text, flags=re.MULTILINE)
    if typing_match:
        imports = [part.strip() for part in typing_match.group(2).split(",")]
        if "Optional" not in imports:
            imports.append("Optional")
            imports = sorted(imports)
            return text[:typing_match.start()] + typing_match.group(1) + ", ".join(imports) + text[typing_match.end():]
        return text

    future_match = re.search(r"^from __future__ import annotations\n", text, flags=re.MULTILINE)
    if future_match:
        insert_at = future_match.end()
        return text[:insert_at] + "\nfrom typing import Optional\n" + text[insert_at:]

    return "from typing import Optional\n\n" + text


def patch_product_model() -> bool:
    if not PRODUCT_MODEL_PATH.exists():
        print(f"ERROR: product model not found: {PRODUCT_MODEL_PATH}")
        return False

    text = PRODUCT_MODEL_PATH.read_text(encoding="utf-8")
    original = text

    if "    price: Optional[float] = None" not in text:
        replacements = [
            ("    price: float\n", "    price: Optional[float] = None\n"),
            ("    price: float = 0\n", "    price: Optional[float] = None\n"),
            ("    price: float | None = None\n", "    price: Optional[float] = None\n"),
        ]
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new, 1)
                break
        else:
            print("ERROR: could not find Product.price line to patch in backend/app/models/product.py")
            print("Expected one of: price: float, price: float = 0, price: float | None = None")
            return False

    text = ensure_optional_import(text)

    if text != original:
        PRODUCT_MODEL_PATH.write_text(text, encoding="utf-8")
        print(f"Updated: {PRODUCT_MODEL_PATH}")
    else:
        print("OK: Product.price is already optional.")
    return True


def patch_main_js() -> bool:
    if not MAIN_JS_PATH.exists():
        print(f"ERROR: frontend main.js not found: {MAIN_JS_PATH}")
        return False

    text = MAIN_JS_PATH.read_text(encoding="utf-8")
    original = text

    if PATCH_MARKER not in text:
        text = PATCH_MARKER + ";\n" + text

    # Patch normalizeProduct in the public catalog dynamic section.
    old = """    const rawSalePrice = firstNonEmpty(product.sale_price, product.promo_price, product.discount_price);
    const hasSalePrice = rawSalePrice !== \"\" && rawSalePrice !== null && rawSalePrice !== undefined;

    const displayPrice = hasSalePrice ? rawSalePrice : rawPrice;"""
    new = """    const rawSalePrice = firstNonEmpty(product.sale_price, product.promo_price, product.discount_price);
    const hasSalePrice = rawSalePrice !== \"\" && rawSalePrice !== null && rawSalePrice !== undefined;
    const categoryForQuote = slugify(categoryKey);
    const hasRawPrice = rawPrice !== \"\" && rawPrice !== null && rawPrice !== undefined;
    const quoteOnly = categoryForQuote === \"packages\" && !hasRawPrice && !hasSalePrice;

    const displayPrice = hasSalePrice ? rawSalePrice : rawPrice;"""
    if old in text and "const quoteOnly = categoryForQuote" not in text:
        text = text.replace(old, new, 1)

    text = text.replace("      categoryKey: slugify(categoryKey),", "      categoryKey: categoryForQuote,", 1)
    text = text.replace("      price: formatPrice(displayPrice),", "      price: quoteOnly ? \"Get Quotation\" : formatPrice(displayPrice),", 1)
    if "      quoteOnly," not in text:
        text = text.replace("      oldPrice: hasSalePrice ? formatPrice(rawPrice, \"\") : \"\",\n      features", "      oldPrice: hasSalePrice ? formatPrice(rawPrice, \"\") : \"\",\n      quoteOnly,\n      features", 1)

    # Preserve quote-only flag on generated product cards.
    if "card.dataset.productQuoteOnly" not in text:
        text = text.replace(
            "    card.dataset.productPrice = normalized.price;\n",
            "    card.dataset.productPrice = normalized.price;\n    card.dataset.productQuoteOnly = normalized.quoteOnly ? \"Y\" : \"N\";\n",
            1,
        )

    old_price_block = """      ${hasSale
        ? `<div class=\"catalog-price-row\"><span class=\"catalog-old-price\">${escapeHtml(normalized.oldPrice)}</span><span class=\"catalog-sale-price\">${escapeHtml(normalized.salePrice)}</span></div>`
        : `<p class=\"catalog-product-price\">${escapeHtml(normalized.price)}</p>`}"""
    new_price_block = """      ${hasSale
        ? `<div class=\"catalog-price-row\"><span class=\"catalog-old-price\">${escapeHtml(normalized.oldPrice)}</span><span class=\"catalog-sale-price\">${escapeHtml(normalized.salePrice)}</span></div>`
        : normalized.quoteOnly
          ? `<a href=\"contact-us.html\" class=\"catalog-product-price catalog-product-quote-link\">Get Quotation</a>`
          : `<p class=\"catalog-product-price\">${escapeHtml(normalized.price)}</p>`}"""
    if old_price_block in text and "catalog-product-quote-link" not in text:
        text = text.replace(old_price_block, new_price_block, 1)

    # Patch modal for quote-only package products.
    old_modal_price_vars = """    const currentPrice = card.dataset.productPrice || \"\";
    const oldPrice = card.dataset.productOldPrice || \"\";

    if (oldPrice) {"""
    new_modal_price_vars = """    const currentPrice = card.dataset.productPrice || \"\";
    const oldPrice = card.dataset.productOldPrice || \"\";
    const quoteOnly = card.dataset.productQuoteOnly === \"Y\" || currentPrice.toLowerCase().includes(\"quotation\");
    const modalPrimaryBtn = productModalOverlay.querySelector(\".product-modal-primary-btn\");

    if (modalPrimaryBtn) {
      modalPrimaryBtn.href = \"contact-us.html\";
      modalPrimaryBtn.innerHTML = quoteOnly
        ? '<i class=\"fa-solid fa-file-pen\"></i>Get Quotation'
        : '<i class=\"fa-solid fa-file-pen\"></i>Request Quotation';
    }

    if (!quoteOnly && oldPrice) {"""
    if old_modal_price_vars in text and "const quoteOnly = card.dataset.productQuoteOnly" not in text:
        text = text.replace(old_modal_price_vars, new_modal_price_vars, 1)

    old_modal_else = """    } else {
      if (modalSaleBadge) modalSaleBadge.classList.add(\"hidden\");
      modalProductPrice.innerHTML = `<span class=\"modal-regular-price\">${escapeHtml(currentPrice)}</span>`;
    }"""
    new_modal_else = """    } else {
      if (modalSaleBadge) modalSaleBadge.classList.add(\"hidden\");
      modalProductPrice.innerHTML = quoteOnly
        ? `<span class=\"modal-regular-price modal-quotation-text\">Get Quotation</span>`
        : `<span class=\"modal-regular-price\">${escapeHtml(currentPrice)}</span>`;
    }"""
    if old_modal_else in text and "modal-quotation-text" not in text:
        text = text.replace(old_modal_else, new_modal_else, 1)

    if text == original:
        print("OK: frontend quotation behavior already appears to be patched.")
        return True

    # Safety check: if we did not add the expected pieces, fail loudly before writing.
    required = [
        PATCH_MARKER,
        "card.dataset.productQuoteOnly",
        "catalog-product-quote-link",
        "modal-quotation-text",
    ]
    missing = [marker for marker in required if marker not in text]
    if missing:
        print("ERROR: frontend patch incomplete. Missing markers:")
        for marker in missing:
            print(f" - {marker}")
        print("Please inspect frontend/assets/js/main.js manually before deploying.")
        return False

    MAIN_JS_PATH.write_text(text, encoding="utf-8")
    print(f"Updated: {MAIN_JS_PATH}")
    return True


def main() -> int:
    ok_model = patch_product_model()
    ok_js = patch_main_js()
    if ok_model and ok_js:
        print("OK: Batch 54C package quotation hotfix applied.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
