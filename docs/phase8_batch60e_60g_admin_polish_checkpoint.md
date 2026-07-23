# Phase 8 Batch 60E-60G Admin Polish Checkpoint

Date: 2026-07-22  
Status: Local implementation and browser verification complete; consolidated GitHub/EC2 sync pending confirmation.

## Scope

This checkpoint records targeted admin presentation work completed after recovery of the Batch 60C branch changes into the current local `main` baseline.

## Batch 60E — Admin Contact Us Split Tables

### Completed

- Three separate admin tables:
  - Company Contact
  - Contact Persons
  - Social Media
- Type-specific columns only.
- No repeated non-applicable `---` display columns.
- Shared Search, Sort By, Clear Filters, Refresh, Add Contact Record, and View / Edit retained.

### Intentionally unchanged

- One `rsa_contact_us` DynamoDB table.
- Existing Contact Us API routes and repositories.
- Company Contact fixed/default record rules.
- Contact Person photo scope.
- Public Contact Us rendering.

## Batch 60F / 60F-1 — Dashboard Quick Actions

### Completed

- Add Product, Add Category, and Add Brand render as three equal desktop buttons on one row.
- Each button includes a boxed `+` indicator.
- Mobile screens use one-column stacking.

### Superseded behavior

The initial Batch 60F selector was too narrowly scoped and did not override the older global odd-item grid rule. Batch 60F-1 adds a dedicated layout class and is the accepted implementation.

## Batch 60G — Login Status Error-Only Polish

### Completed

- Normal email/password instruction remains in the login information note.
- Information note font size increased to `16px`.
- Emphasized login status remains empty/hidden when no error exists.
- Routine progress and success messages do not populate the emphasized error area.
- Actual login/configuration errors use friendly non-technical text.
- Status element retains accessible alert/live-region behavior.
- Cognito/JWT/authentication flow remains unchanged.

## Batch 60C Integration Recovery

The previously separate Batch 60C branch was integrated into the current local baseline while preserving later fixes, including:

- database-driven public phone/email headers;
- Promotions mobile hero rotation;
- Admin Sale Products sorting;
- Services card CTA cleanup;
- friendly login error handling.

Local JavaScript syntax and browser checks passed during the integration process.

## Files affected by the completed polish

```text
frontend/admin/contact-us.html
frontend/admin/index.html
frontend/admin/login.html
frontend/admin/assets/css/admin.css
frontend/admin/assets/css/admin-auth.css
frontend/admin/assets/js/admin-cms.js
backend/scripts/apply_batch60e_contact_split_tables.py
backend/scripts/apply_batch60f_dashboard_quick_actions.py
backend/scripts/apply_batch60f1_dashboard_quick_actions_row_fix.py
backend/scripts/apply_batch60g_login_status_error_only.py
```

The exact Git working tree may also include documentation and previously merged Batch 60C files.

## Pending closure

- Commit the consolidated current local version.
- Push `main` to GitHub.
- Deploy the same source tree to EC2 through the established release-folder script.
- Verify:
  - `/api/health`
  - admin login initial/error state
  - dashboard one-row Quick Actions
  - three Contact Us admin tables
  - recovered Batch 60C public/admin behavior
- Stop EC2 after verification unless active testing/demo continues.
