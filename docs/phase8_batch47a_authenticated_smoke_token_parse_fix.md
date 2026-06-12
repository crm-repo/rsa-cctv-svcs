# Phase 8 Batch 47A — Authenticated Smoke Token Parse Fix

## Purpose

Batch 47A fixes the authenticated admin API smoke script after a real Cognito login returned a response larger than the script's previous 1600-byte response read limit.

## Fixes

- Reads the full HTTP response body before JSON parsing.
- Redacts `access_token`, `id_token`, and `refresh_token` values from script output if an error occurs.
- Keeps the original Batch 47 behavior and test scope.

## Important security note

Do not paste Cognito tokens in chat, tickets, commits, screenshots, or logs. If a token was pasted accidentally, log out from the admin browser session and wait for token expiry before continuing, or use Cognito global sign-out for the admin user if needed.

## Test

Run:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_authenticated_admin_api_smoke.py `
  --base-url http://13.229.227.89 `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

Expected result:

```text
Batch 47 authenticated admin API/browser smoke check PASSED.
```
