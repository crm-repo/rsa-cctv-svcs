# Phase 8 Batch 55B — Admin Category/Subcategory/Brand Protection Polish

## Purpose

Batch 55B adds admin-side category, subcategory, and brand protection so the reviewed Batch 54A/54B data structure can be maintained safely from Admin without breaking active products.

## Scope

### Product admin

- Adds `subcategory_key` support to the Product model and admin create/update payloads.
- Changes the Admin Product form from a free-text subcategory field to a category-filtered subcategory dropdown.
- Stores both category snapshot fields (`category_key`, `category_name`) and subcategory fields (`subcategory_key`, `subcategory`).
- Product form lists active brands/categories by default and preserves the current hidden brand/category when editing an existing record.

### Categories admin

- Adds nested `subcategories` support on `Category` records.
- Shows subcategory count in the category table and full subcategory detail in the drawer.
- Adds a subcategory editor using this line format:

```text
10 | 2mp-dome-camera | 2MP Dome Camera
```

- Blocks hiding a category when active products still use it.
- Blocks changing category key/prefix while active products still use the category.
- Blocks deleting/removing a subcategory if any product still uses it.
- Does not add subcategory hide/show behavior.

### Brands admin

- Blocks hiding a brand when active products still use it.
- Synchronizes product brand snapshot fields when brand name/key/logo changes.
- Delete remains disabled; no destructive brand delete endpoint is introduced.

## Safety rules

- No DynamoDB tables are deleted.
- `rsa_id_counters` are not reset.
- No real S3/local upload storage is implemented.
- Batch 55A media path behavior is preserved.
- Existing `assets/images/...` paths remain valid.
- EC2 can stay stopped while applying and committing this patch.

## Files changed

- `backend/app/models/category.py`
- `backend/app/models/product.py`
- `backend/app/services/category_service.py`
- `backend/app/services/product_service.py`
- `backend/app/services/brand_service.py`
- `frontend/admin/assets/js/admin-catalog.js`
- `backend/scripts/patch_admin_category_subcategory_brand_protection.py`
- `docs/phase8_batch55b_admin_category_subcategory_brand_protection.md`

## Verification

After applying the patch, verify the markers:

```powershell
Select-String -Path .\frontend\admin\assets\js\admin-catalog.js -Pattern "batch55b-admin-category-subcategory-brand-protection|subcategory_key|subcategories_text"
Select-String -Path .\backend\app\models\category.py -Pattern "CategorySubcategory|subcategories"
Select-String -Path .\backend\app\models\product.py -Pattern "subcategory_key"
Select-String -Path .\backend\app\services\category_service.py -Pattern "Cannot hide category|Cannot delete subcategory"
Select-String -Path .\backend\app\services\brand_service.py -Pattern "Cannot hide brand|batch55b-brand-snapshot-sync"
```

Recommended local smoke checks:

1. Open Admin Products and confirm Category is a dropdown.
2. Select a category and confirm Subcategory dropdown changes.
3. Save a product and confirm `subcategory_key` and `subcategory` are stored.
4. Open Admin Categories and confirm subcategories are visible/editable in the drawer.
5. Try hiding a category or brand that active products use; backend should block the save.
6. Confirm Batch 55A image picker behavior still preserves existing `assets/images/...` paths.
