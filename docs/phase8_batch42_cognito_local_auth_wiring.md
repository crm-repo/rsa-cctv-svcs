# Phase 8 Batch 42 — Cognito local admin-auth wiring

## Purpose

Batch 42 wires the Cognito values from Batch 41 into the local backend and admin login page so Cognito username/password login can be tested before public admin exposure.

This batch does **not** expose `/admin/` publicly on EC2. Nginx should continue blocking `/admin/`, `/api/admin/*`, `/api/customers`, `/api/bookings`, `/api/inquiries`, `/docs`, `/redoc`, and `/openapi.json` until a later protected-admin exposure batch.

## Approved Batch 41 values

```text
RSA_ADMIN_AUTH_MODE=cognito
RSA_COGNITO_REGION=ap-southeast-1
RSA_COGNITO_USER_POOL_ID=ap-southeast-1_BNvYFNmw9
RSA_COGNITO_CLIENT_ID=3r13vplp8agjigm3e52ficsm1e
Admin email: jhannbernas@gmail.com
```

Do not store or commit the admin password.

## Important Cognito app-client setting

Batch 42 uses the backend endpoint `/api/admin/auth/cognito-login`, which calls Cognito `InitiateAuth` with `USER_PASSWORD_AUTH`. The Cognito app client must enable username/password auth for this test.

In AWS Console:

```text
Amazon Cognito
→ User pools
→ rsa-cms-admin-users
→ Applications
→ App clients
→ rsa-cms-admin-web-client
→ Edit
→ Authentication flows
```

Enable:

```text
Sign in with username and password / ALLOW_USER_PASSWORD_AUTH
```

Keep:

```text
No client secret
MFA off
No SMS
Self-registration disabled
Email-only account recovery
```

## Local backend test flow

Open PowerShell 1:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

$env:RSA_ADMIN_AUTH_MODE="cognito"
$env:RSA_COGNITO_REGION="ap-southeast-1"
$env:RSA_COGNITO_USER_POOL_ID="ap-southeast-1_BNvYFNmw9"
$env:RSA_COGNITO_CLIENT_ID="3r13vplp8agjigm3e52ficsm1e"

uvicorn app.main:app --reload
```

Open PowerShell 2:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_cognito_admin_login_local.py `
  --base-url http://127.0.0.1:8000 `
  --admin-email "jhannbernas@gmail.com"
```

Then run the execute login test:

```powershell
python scripts\check_cognito_admin_login_local.py `
  --base-url http://127.0.0.1:8000 `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

The script will ask for the temporary/current Cognito password. Input is hidden. If Cognito returns `NEW_PASSWORD_REQUIRED`, the script will ask for a new permanent password and complete the challenge.

## Local browser check

With the local backend still running in Cognito mode, open the admin login page from the local frontend:

```text
frontend/admin/login.html
```

or through your local static server if you are using one.

Expected behavior:

- The login page should say Cognito admin login is enabled.
- Login with `jhannbernas@gmail.com` and the Cognito password should store a Cognito access token in browser local storage.
- Admin pages should redirect to login if no valid token is present.

## Reset local backend mode after testing

When done, stop Uvicorn with `Ctrl+C`, then clear the PowerShell environment variables if needed:

```powershell
Remove-Item Env:RSA_ADMIN_AUTH_MODE -ErrorAction SilentlyContinue
Remove-Item Env:RSA_COGNITO_REGION -ErrorAction SilentlyContinue
Remove-Item Env:RSA_COGNITO_USER_POOL_ID -ErrorAction SilentlyContinue
Remove-Item Env:RSA_COGNITO_CLIENT_ID -ErrorAction SilentlyContinue
```

## What this batch intentionally does not do

- Does not expose `/admin/` publicly on EC2.
- Does not change EC2 Nginx lockdown.
- Does not require SMS, phone verification, or MFA.
- Does not commit passwords or secrets.
- Does not create new Cognito resources.

## Success criteria

- Local backend `/api/admin/auth/config` returns Cognito mode with user pool/client configured.
- Anonymous `/api/admin/auth/status` is not authenticated.
- Cognito login returns an access token.
- Authenticated `/api/admin/auth/status` returns authenticated `true`.
- Public EC2 admin surface remains blocked until the later enablement batch.
