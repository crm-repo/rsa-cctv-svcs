# Batch 59A — Cognito Groups + Settings > Users

Status: implementation package prepared.

## Scope

- Use Cognito Groups for roles: `Admin` and `Standard`.
- Settings > Users reads and manages Cognito users through protected FastAPI routes.
- No DynamoDB users table is added.
- The browser never calls Cognito admin APIs directly.
- Admin-created users use suppressed invitation email and a backend-generated temporary password shown once only.
- First Name and Last Name map to Cognito `given_name` and `family_name`.
- The Users table displays generated Full Name.
- Standard users do not see Settings and backend user-management routes require Admin.

## Files patched or created

```text
backend/app/auth/admin_auth.py
backend/app/main.py
backend/app/models/admin_user.py
backend/app/routes/admin_users.py
backend/app/services/admin_user_service.py
frontend/admin/settings.html
frontend/admin/assets/js/admin-api.js
frontend/admin/assets/js/admin-role-guard-59a.js
frontend/admin/assets/js/admin-users-59a.js
frontend/admin/assets/css/admin.css
docs/phase8_batch59a_cognito_groups_settings_users.md
```

## Batch package standard

This file is intentionally stored flat under `docs/` as `phase8_batch59a_cognito_groups_settings_users.md`.

Do not recreate:

```text
docs/phase8/
docs/Phase 8 README/
root README txt/md files
```

Patch and verify scripts belong under:

```text
backend/scripts/
```

## Local verification markers

Expected file markers after applying:

```text
python ./backend/scripts/verify_batch59a_cognito_groups_settings_users.py
```

Expected backend route markers after local start and Admin login/token:

```text
GET /api/admin/users/health -> version: batch59a-cognito-groups-settings-users
GET /api/admin/users -> items/count/roles
```

Expected browser markers:

```text
window.RSA_BATCH59A_ROLE_GUARD_VERSION
window.RSA_BATCH59A_ADMIN_USERS_VERSION
Settings > Users panel visible for Admin
Settings hidden/restricted for Standard
```

## Notes

AWS Console setup instructions are intentionally kept outside this README and should be followed from the chat steps before runtime testing.
