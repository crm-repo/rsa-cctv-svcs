# Batch 42 — Cognito local admin-auth wiring

Use this batch after Batch 41 Cognito user pool creation has passed.

## Files

```text
backend/app/auth/admin_auth.py
backend/app/routes/admin_auth.py
backend/scripts/check_cognito_admin_login_local.py
frontend/admin/assets/js/admin-auth.js
frontend/admin/assets/css/admin-auth.css
frontend/admin/login.html
docs/phase8_batch42_cognito_local_auth_wiring.md
docs/phase8_batch42_cognito_local_auth_checklist.md
deploy/cognito/admin-auth.local.env.example
```

## Main test

Start backend locally with Cognito env vars, then run:

```powershell
python scripts\check_cognito_admin_login_local.py `
  --base-url http://127.0.0.1:8000 `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

Do not commit passwords or secrets.

EC2 can stay stopped for this batch.
