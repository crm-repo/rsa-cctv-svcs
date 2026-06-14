Phase 8 Batch 55C — Admin Page Overall Polish

Purpose:
- Polish the admin UI after Batch 55B category/subcategory/brand protection.
- Restore/fix Batch 55A media picker execution so image fields use Choose File / Restore Current again.
- Improve admin wording, labels, navigation, dashboard icons, read-only field styling, required field indicators, login page theme, and logout behavior.

What this batch changes:
1. Sidebar navigation:
   - Products heading becomes Catalog.
   - All Products becomes Products.
   - Contents links remain clickable from every admin page.
   - Promotions link is no longer accidentally disabled.
   - Adds Logout button to the sidebar.
   - Removes outdated Local admin preview / Unprotected until Cognito batch sidebar card.

2. Product drawer:
   - Create product drawer closes after successful create.
   - Edit product opens directly to editable fields instead of showing duplicate read-only details first.
   - Save Product is disabled until fields change.
   - Read-only fields are visually emphasized.
   - Package Placement becomes Promote Package with Yes/No.
   - Promote Package is enabled only when category is Packages/Kits.

3. Media picker:
   - Repairs admin-media.js formatting/execution.
   - Product Image / Brand Logo media fields use Choose File / Restore Current.
   - Existing assets/images/... paths remain preserved.
   - No uploads/... path is saved unless backend confirms upload_prepared=true.

4. Admin UI polish:
   - Uses RSA public-site dark red theme (#b91c1c / #7f1d1d).
   - Dashboard cards use Font Awesome icons.
   - System responses are more user-friendly and avoid backend API wording.
   - Removes batch/internal wording from UI.
   - Adds required-field asterisks through form labels.
   - Add Category now includes Icon Code.
   - Login page gets desktop security-products background SVG and mobile gradient background.

Deferred to Batch 55D:
- Settings page behavior.
- Admin user dropdown/profile behavior.
- Bell notification behavior.

Safety:
- No DynamoDB table deletion.
- No rsa_id_counters reset.
- No S3 setup.
- No real media upload/storage implementation.
- Batch 55A media path preservation remains intact.
- Batch 55B category/subcategory/brand protections remain intact.

Apply from project root:

python backend/scripts/patch_admin_page_overall_polish_55c.py

Verify locally:

node --check .\frontend\admin\assets\js\admin-media.js
node --check .\frontend\admin\assets\js\admin-catalog.js
node --check .\frontend\admin\assets\js\admin-dashboard.js
node --check .\frontend\admin\assets\js\admin-cms.js
node --check .\frontend\admin\assets\js\admin-leads.js

Select-String -Path .\frontend\admin\assets\js\admin-catalog.js -Pattern "batch55c-admin-page-overall-polish|Promote Package|Product Image|Icon Code|data-save-button"
Select-String -Path .\frontend\admin\assets\js\admin-media.js -Pattern "batch55a-admin-media-path-interim-fix|RSAAdminMedia|upload_prepared|Restore Current"
Select-String -Path .\frontend\admin\assets\css\admin.css -Pattern "batch55c-admin-page-overall-polish|--rsa-red: #b91c1c"
Select-String -Path .\frontend\admin\assets\css\admin-auth.css -Pattern "batch55c-admin-login-theme|admin-login-security-bg.svg"
Select-String -Path .\frontend\admin\products.html -Pattern "Catalog|Products|promotions.html|about.html|data-admin-logout"

Browser checks:
- Product Add/Edit shows Product Image media picker, not raw Image Path.
- Create Product closes after success.
- Edit Product Save button is disabled until a change is made.
- Promote Package is enabled only for Packages/Kits.
- Category Add/Edit includes Icon Code.
- Contents links are clickable from Products/Categories/Brands.
- Promotions opens from the left menu.
- Dashboard icons use Font Awesome.
- Login page uses the new desktop background and mobile gradient.
- Logout redirects to login.

Commit/push:

git status
git add frontend/admin backend/scripts/patch_admin_page_overall_polish_55c.py docs/phase8_batch55c_admin_page_overall_polish.md README_PHASE8_BATCH55C_ADMIN_PAGE_OVERALL_POLISH.txt
git commit -m "Polish admin pages and restore media picker"
git push

Deploy to EC2 only after local verification using the known project release script.
