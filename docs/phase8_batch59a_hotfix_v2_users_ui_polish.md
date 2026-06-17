# Phase 8 Batch 59A Hotfix v2 — Users UI Polish

Status: hotfix for Batch 59A local UI testing

## Purpose

This hotfix corrects the Settings > Users visual issues found after the Cognito users API started loading successfully.

## Fixes

- Hides the empty red temporary-password panel. It should only appear after Create User or Reset Password when a one-time password is returned.
- Keeps the Users table as a Full Name table. First Name and Last Name remain inside the Add/Edit User modal only.
- Separates the Users toolbar/card area and the Users table area visually, matching the other admin pages where filters/toolbars and tables are separate cards.
- Improves Add/Edit User modal spacing, input height, action button spacing, and close-button spacing.

## Files changed

- `frontend/admin/assets/css/admin.css`
- `frontend/admin/assets/js/admin-users-59a.js` only receives a small defensive helper to keep the temporary-password panel hidden when empty.

## Not changed

- No Cognito backend route changes.
- No IAM policy changes.
- No DynamoDB users table.
- No EC2/deployment change.
