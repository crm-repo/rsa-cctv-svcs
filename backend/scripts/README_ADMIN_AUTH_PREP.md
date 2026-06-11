# Phase 8 Batch 23 — Admin Auth / Cognito Preparation

This batch prepares the admin frontend/backend for Cognito protection without creating Cognito resources yet.

## Safe defaults

Default mode:

```powershell
RSA_ADMIN_AUTH_MODE=disabled
```

In disabled mode:

- Admin pages remain accessible for local development.
- No AWS Cognito calls are made.
- No SMS/MFA is enabled.
- `/api/admin/auth/config` returns safe local-preview config.

## Local mock mode

Optional local auth wiring test:

```powershell
$env:RSA_ADMIN_AUTH_MODE="mock"
$env:RSA_ADMIN_MOCK_TOKEN="local-dev-admin-token"
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:5500/admin/login.html
```

Use token:

```text
local-dev-admin-token
```

## Cognito mode later

Later, after Cognito is created:

```powershell
$env:RSA_ADMIN_AUTH_MODE="cognito"
$env:RSA_COGNITO_REGION="ap-southeast-1"
$env:RSA_COGNITO_USER_POOL_ID="<user-pool-id>"
$env:RSA_COGNITO_APP_CLIENT_ID="<app-client-id>"
```

Full JWT verification is not enabled in this batch. This is only preparation.

## Test commands

```powershell
python scripts\check_admin_auth_config.py
```

Browser/API checks:

```text
http://127.0.0.1:8000/api/admin/auth/config
http://127.0.0.1:8000/api/admin/auth/status
```
