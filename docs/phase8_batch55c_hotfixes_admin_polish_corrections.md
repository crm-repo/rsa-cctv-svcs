# Phase 8 Batch 55C-Hotfixes — Admin Polish Corrections

Status: Ready to apply after Batch 55C local patch.  
Scope: Corrections from admin inspection before EC2 deployment.

## Included fixes

- Logout now clears local/session admin auth tokens and redirects to `login.html?logged_out=1`.
- Login page no longer immediately bounces back to dashboard in local disabled-auth preview; it shows a Continue to Dashboard action instead.
- Sidebar navigation is normalized across Dashboard, Catalog, CRM and CMS pages so Catalog/CMS items stay clickable after visiting CRM pages.
- CRM pages now show the new Catalog / Products labels instead of old Products / All Products labels.
- Dashboard shortcut cards are real links instead of disabled buttons.
- Toolbar Visibility filters are replaced by Sort By controls; form-level Public Visibility remains unchanged.
- Most Recent is the default sort for Catalog, CMS and CRM tables so new/updated records appear first.
- Page-specific loaded messages now use labels like `7 Products records found` and `10 About Us records found`.
- Product/Catalog/CMS drawers no longer show duplicate form titles inside the drawer body.
- Product/Catalog/CMS drawers close after successful create or update.
- Public Visibility / Promote Package controls and media picker fields receive overflow/alignment fixes.
- Brand/category/subcategory/service/social keys are system-generated/read-only from display names where applicable.
- Existing Restore Current media picker behavior is kept.

## Deferred to 55D

- Full Settings page behavior.
- Admin user profile menu behavior.
- Bell notification details.

## Safety

- No DynamoDB table deletion.
- No `rsa_id_counters` reset.
- No S3 bucket setup.
- No real binary upload/storage enablement.
- No EC2 deployment required until local verification passes.
