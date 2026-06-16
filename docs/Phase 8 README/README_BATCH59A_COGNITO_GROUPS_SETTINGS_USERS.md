# Batch 59A — Cognito Groups + Settings > Users

Status: implementation package prepared.

## Scope

- Use Cognito Groups for roles: `Admin` and `Standard`.
- Settings > Users reads and manages Cognito users through protected FastAPI backend routes.
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
docs/phase8/README_BATCH59A_COGNITO_GROUPS_SETTINGS_USERS.md
```

## Apply command

Run from the project root after extracting the package:

```powershell
python .\backend\scripts\apply_batch59a_cognito_groups_settings_users.py
```

## Local verification markers

Expected backend route markers after local start:

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

AWS Console setup instructions are intentionally not duplicated here. Follow the chat instructions for creating/verifying Cognito groups and assigning the current admin user to the Admin group.
