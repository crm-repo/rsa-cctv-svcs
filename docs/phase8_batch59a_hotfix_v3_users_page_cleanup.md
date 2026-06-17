# Phase 8 Batch 59A Hotfix v3 — Settings Users Page Cleanup

Status: targeted Batch 59A UI cleanup after local browser testing

## Purpose

This hotfix corrects the remaining Settings > Users UI issues from local testing.

## Fixes

- Moves the Cognito Users section out of the earlier Settings grid so it is visually separated from the Account, Notifications, and System status cards.
- Removes the redundant visible `1 users` count above the Users table; the status message already shows the loaded count.
- Ensures sidebar icons render by adding/normalizing Font Awesome icons on Settings page navigation.
- Keeps Add User as a modal workflow.
- Keeps First Name and Last Name inside Add/Edit forms only; the table remains Full Name based.
- Keeps the empty temporary-password panel hidden unless an actual password is returned.
- Updates visible Settings system marker text from Batch 55D to Batch 59A where the old static marker is still present.

## Files changed

- `frontend/admin/settings.html`
- `frontend/admin/assets/css/admin.css`
- `docs/phase8_batch59a_hotfix_v3_users_page_cleanup.md`

## Not changed

- No Cognito route logic change.
- No IAM policy change.
- No DynamoDB users table.
- No EC2/deployment change.
