# Phase 8 Batch 48 — Full Authenticated Admin EC2 Regression

## Purpose

Batch 48 validates the live EC2 public-IP demo after Cognito-protected admin APIs are enabled.

It verifies:

- Public website pages load through Nginx.
- Public read APIs still work.
- Admin login UI and auth endpoints are reachable.
- Anonymous admin/CRM API requests return `401`.
- Developer surfaces stay blocked: `/docs`, `/redoc`, `/openapi.json`.
- Direct public access to FastAPI port `8000` remains blocked.
- Authenticated admin API reads work with a Cognito access token.
- Optional live write regression creates hidden/test records only when explicitly confirmed.

## Safety

- Passwords are prompted with hidden input and are never printed or stored.
- Token fields are redacted from error output.
- Write regression requires `--confirm-write-test` and creates small hidden/test records in DynamoDB.
- No delete operation is performed.

## Commands

Read-only support/anonymous checks:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_full_authenticated_admin_regression.py --base-url http://<PUBLIC_IPV4>
```

Authenticated read regression:

```powershell
python scripts\check_ec2_full_authenticated_admin_regression.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

Full authenticated read/write regression:

```powershell
python scripts\check_ec2_full_authenticated_admin_regression.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test `
  --confirm-write-test
```

## Expected result

```text
Batch 48 full authenticated admin EC2 regression PASSED.
```

## EC2 cost reminder

Keep EC2 running only while testing. Stop the instance when the batch is complete unless continuing immediately.
