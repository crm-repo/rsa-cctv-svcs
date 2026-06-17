from pathlib import Path

MARKER = "batch59c-hotfix-v2-public-category-strip-only"
OLD_BAD_MARKER = "batch59c-public-category-strip-dynamodb-binding"
MAIN_PATH = Path("frontend/assets/js/main.js")
DOC_PATH = Path("docs/phase8_batch59c_public_category_strip_dynamodb_binding.md")


def fail(message: str) -> None:
    raise SystemExit(f"[fail] {message}")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        fail(f"Expected block not found: {label}")
    return text.replace(old, new, 1)


print("[start] Applying batch59c-hotfix-v2-public-category-strip-only")

if not MAIN_PATH.exists():
    fail("Missing frontend/assets/js/main.js")

text = MAIN_PATH.read_text(encoding="utf-8")

if OLD_BAD_MARKER in text and MARKER not in text:
    fail(
        "Old Batch 59C experimental marker is still present in main.js. "
        "Restore frontend/assets/js/main.js from git first, then rerun this hotfix."
    )

if MARKER in text:
    print("[skip] batch59c-hotfix-v2 marker already present in frontend/assets/js/main.js")
else:
    backup_path = MAIN_PATH.with_suffix(MAIN_PATH.suffix + ".bak59c-v2")
    backup_path.write_text(text, encoding="utf-8")
    print(f"[ok] Backup written: {backup_path}")

    text = replace_once(
        text,
        'const RSA_PUBLIC_CATALOG_DYNAMIC_VERSION = "batch49b-api-page-limit-fix";',
        f'const RSA_PUBLIC_CATALOG_DYNAMIC_VERSION = "{MARKER}";',
        "public catalog version marker",
    )

    text = replace_once(
        text,
        'const productFilterButtons = document.querySelectorAll(".product-filter-btn");',
        'let productFilterButtons = Array.from(document.querySelectorAll(".product-filter-btn"));',
        "productFilterButtons declaration",
    )

    helper_insertion_point = '  function renderBrandStrips() {'
    helpers = '''  /* batch59c-hotfix-v2-public-category-strip-only:
     Only the public category button strip is hydrated from /api/categories.
     Existing product/brand loading, pagination, modal, and promotions hero logic stay unchanged. */
  function isPublicCategoryVisible(category) {
    const flag = String(category && category.show_flag !== undefined ? category.show_flag : "Y").trim().toUpperCase();
    return flag !== "N" && flag !== "FALSE" && flag !== "0";
  }

  function normalizePublicCategory(category) {
    const name = firstNonEmpty(category.category_name, category.name, category.title, category.category_key);
    const key = slugify(firstNonEmpty(category.category_key, category.key, name));
    const icon = firstNonEmpty(category.icon_code, "fa-solid fa-folder");
    const displaySeq = numericValue(firstNonEmpty(category.display_seq, category.display_order, category.sort_order)) ?? 9999;

    return {
      key,
      name: firstNonEmpty(name, key),
      icon,
      displaySeq
    };
  }

  function publicCategoryButtonHtml(filter, label, iconClass, extraClass = "") {
    const classes = ["product-filter-btn", extraClass].filter(Boolean).join(" ");
    return `<button class="${escapeHtml(classes)}" data-filter="${escapeHtml(filter)}"><i class="${escapeHtml(iconClass)}"></i>${escapeHtml(label)}</button>`;
  }

  function balancePublicCategoryStrip(categoryFilterElement) {
    if (!categoryFilterElement) return;

    const buttons = Array.from(categoryFilterElement.querySelectorAll(".product-filter-btn"));
    categoryFilterElement.innerHTML = "";

    if (buttons.length <= 15) {
      categoryFilterElement.classList.remove("two-row");
      buttons.forEach((button) => categoryFilterElement.appendChild(button));
      return;
    }

    categoryFilterElement.classList.add("two-row");
    const firstRowCount = Math.ceil(buttons.length / 2);
    const firstRow = buttons.slice(0, firstRowCount);
    const secondRow = buttons.slice(firstRowCount);

    for (let index = 0; index < firstRowCount; index += 1) {
      if (firstRow[index]) categoryFilterElement.appendChild(firstRow[index]);
      if (secondRow[index]) categoryFilterElement.appendChild(secondRow[index]);
    }
  }

  async function renderPublicCategoryStripFromApi() {
    const categoryFilterElement = document.querySelector(".products-category-filter");
    if (!categoryFilterElement) return;

    let categoryRecords = [];

    try {
      categoryRecords = await fetchPagedApiItems("/api/categories", 50);
    } catch (error) {
      console.warn("Unable to load public categories from API. Keeping static category buttons.", error);
      return;
    }

    const categories = categoryRecords
      .filter(isPublicCategoryVisible)
      .map(normalizePublicCategory)
      .filter((category) => category.key)
      .sort((a, b) => a.displaySeq - b.displaySeq || a.name.localeCompare(b.name));

    if (!categories.length) return;

    categories.forEach((category) => {
      filterTitles[category.key] = category.name;
    });

    const categoryButtonsHtml = categories
      .map((category) => publicCategoryButtonHtml(category.key, category.name, category.icon))
      .join("");

    if (isPromotionsPage) {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large"),
        publicCategoryButtonHtml("sale", "Sale", "fa-solid fa-tag", "active promo-sale-locked"),
        categoryButtonsHtml
      ].join("");
    } else if (isBrandsPage) {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large"),
        categoryButtonsHtml
      ].join("");
    } else {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large", currentFilter === "all" ? "active" : ""),
        publicCategoryButtonHtml("sale", "Sale", "fa-solid fa-tag", currentFilter === "sale" ? "active" : ""),
        categoryButtonsHtml
      ].join("");
    }

    productFilterButtons = Array.from(categoryFilterElement.querySelectorAll(".product-filter-btn"));

    const allowedFilters = new Set(productFilterButtons.map((button) => button.dataset.filter || "all"));
    if (!allowedFilters.has(currentFilter)) {
      currentFilter = "all";
    }

    balancePublicCategoryStrip(categoryFilterElement);
    bindProductFilterButtons();
  }

'''

    if helper_insertion_point not in text:
        fail("renderBrandStrips insertion point not found")
    text = text.replace(helper_insertion_point, helpers + helper_insertion_point, 1)

    start = text.find('  productFilterButtons.forEach((button) => {')
    end = text.find('  document.querySelectorAll(".brand-strip-row").forEach((row) => {', start)
    if start == -1 or end == -1:
        fail("Product filter button handler block not found")

    new_click_block = '''  function bindProductFilterButtons() {
    productFilterButtons = Array.from(document.querySelectorAll(".product-filter-btn"));

    productFilterButtons.forEach((button) => {
      if (button.dataset.rsaBatch59cV2Bound === "true") return;
      button.dataset.rsaBatch59cV2Bound = "true";

      button.addEventListener("click", () => {
        if (isPromotionsPage && button.dataset.filter === "sale") return;

        if (isBrandsPage && currentBrand === "all") {
          productFilterButtons.forEach((btn) => btn.classList.remove("active"));
          currentFilter = "all";
          currentProductsPage = 0;
          setSectionTitle();
          renderProductsPage();
          return;
        }

        productFilterButtons.forEach((btn) => {
          if (!(isPromotionsPage && btn.dataset.filter === "sale")) btn.classList.remove("active");
        });

        button.classList.add("active");
        currentFilter = button.getAttribute("data-filter") || "all";
        currentProductsPage = 0;
        setSectionTitle();
        renderProductsPage();
      });
    });
  }

  bindProductFilterButtons();

'''
    text = text[:start] + new_click_block + text[end:]

    text = replace_once(
        text,
        "      renderBrandStrips();\n      await renderPromotionHeroBanners(publicProducts);",
        "      renderBrandStrips();\n      await renderPublicCategoryStripFromApi();\n      await renderPromotionHeroBanners(publicProducts);",
        "loadDynamicCatalogData category strip hook",
    )

    MAIN_PATH.write_text(text, encoding="utf-8")
    print("[ok] Patched frontend/assets/js/main.js")

DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
DOC_PATH.write_text("""# Phase 8 Batch 59C — Public Category Strip DynamoDB Binding

Status: Applied / pending local browser verification

Marker: batch59c-hotfix-v2-public-category-strip-only

## Scope

Hydrate the public category strips on Products, Promotions, and Brands from `/api/categories`.

## Behavior

- Products keeps virtual All Products and Sale buttons, then renders visible DynamoDB categories.
- Promotions keeps virtual All Products and locked Sale buttons, then renders visible DynamoDB categories.
- Brands keeps virtual All Products, then renders visible DynamoDB categories.
- Category button keys use `category_key`.
- Category button labels use `category_name`.
- Category icons use `icon_code`.
- Category order uses `display_seq`.
- Hidden categories are not shown publicly.

## Safety

- Frontend-only public catalog change.
- No backend route change.
- No DynamoDB table/data change.
- No Cognito change.
- No S3/media change.
- No EC2/Nginx/Route 53/CloudFront change.
- Static HTML category buttons remain as fallback if `/api/categories` cannot load.
""", encoding="utf-8")
print(f"[ok] Wrote {DOC_PATH}")

print("[done] batch59c-hotfix-v2-public-category-strip-only applied.")
print("[done] Products, Promotions, and Brands category strips now hydrate from /api/categories while preserving existing catalog loading.")
print("[done] No backend/IAM/Cognito/DynamoDB/S3/EC2/Route 53/CloudFront or paid notification change.")
