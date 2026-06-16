# Batch 55B — Admin Category/Subcategory/Brand Protection Polish

This batch adds the admin category/subcategory/brand protection polish planned after Batch 55A.

## What it changes

- Product admin uses a Category dropdown and category-filtered Subcategory dropdown.
- Product records support and save `subcategory_key` plus `subcategory`.
- Category records support nested `subcategories`.
- Categories admin shows subcategory counts and lets you edit subcategory rows inside the category drawer.
- Category hide is blocked when active products still use the category.
- Subcategory removal is blocked when products still use the subcategory.
- Brand hide is blocked when active products still use the brand.
- Brand snapshot changes sync to affected product records.
- Batch 55A media path behavior is preserved.

## Apply patch

From project root:

```powershell
python backend/scripts/patch_admin_category_subcategory_brand_protection.py
```

## Verify files

```powershell
Select-String -Path .\frontend\admin\assets\js\admin-catalog.js -Pattern "batch55b-admin-category-subcategory-brand-protection|subcategory_key|subcategories_text"
Select-String -Path .\backend\app\models\category.py -Pattern "CategorySubcategory|subcategories"
Select-String -Path .\backend\app\models\product.py -Pattern "subcategory_key"
Select-String -Path .\backend\app\services\category_service.py -Pattern "Cannot hide category|Cannot delete subcategory"
Select-String -Path .\backend\app\services\brand_service.py -Pattern "Cannot hide brand|batch55b-brand-snapshot-sync"
```

## Local admin checks

1. Start local backend and admin as usual.
2. Open Admin Products.
3. Confirm Category is a dropdown and Subcategory changes when Category changes.
4. Save an edited product and confirm it keeps `category_key/category_name` and `subcategory_key/subcategory`.
5. Open Admin Categories.
6. Confirm the drawer shows subcategory rows in `display_seq | key | name` format.
7. Try removing a used subcategory; backend should block it.
8. Try hiding a category or brand used by active products; backend should block it.
9. Confirm Batch 55A Admin media picker still preserves existing `assets/images/...` paths.

## Commit

```powershell
git status
git add backend/app/models/category.py backend/app/models/product.py backend/app/services/category_service.py backend/app/services/product_service.py backend/app/services/brand_service.py frontend/admin/assets/js/admin-catalog.js backend/scripts/patch_admin_category_subcategory_brand_protection.py docs/phase8_batch55b_admin_category_subcategory_brand_protection.md README_PHASE8_BATCH55B_ADMIN_CATEGORY_SUBCATEGORY_BRAND_PROTECTION.txt
git commit -m "Add admin category and brand protection polish"
git push
```

## EC2 note

EC2 can stay stopped while applying and committing this batch. Start it only if you are ready to deploy and test the updated Admin UI live.
