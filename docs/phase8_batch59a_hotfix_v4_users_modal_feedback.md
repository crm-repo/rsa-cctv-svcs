# Phase 8 Batch 59A Hotfix v4 — Users Modal Feedback

Status: targeted local UI hotfix

## Purpose

Correct the Add/Edit User modal feedback behavior so create/update errors are visible inside the modal instead of behind the overlay.

## Fixes

- Adds an inline status/error area inside the Add User modal.
- Adds an inline status/error area inside the Edit User modal.
- Keeps the modal open when create/update fails so the error can be read and corrected.
- Keeps Users table as Full Name based.
- Keeps First Name and Last Name only inside the Add User modal.
- Keeps Edit User as Full Name only.
- Keeps the temporary password panel hidden unless a password is returned.
- Improves modal spacing/overlay consistency.
- Adds clearer message for 401 Unauthorized: log out/in and retry before deeper debugging.

## Files changed

- `frontend/admin/settings.html`
- `frontend/admin/assets/js/admin-users-59a.js`
- `frontend/admin/assets/css/admin.css`
- `docs/phase8_batch59a_hotfix_v4_users_modal_feedback.md`

## Not changed

- No Cognito/IAM/backend route changes.
- No DynamoDB users table.
- No EC2/deployment change.
