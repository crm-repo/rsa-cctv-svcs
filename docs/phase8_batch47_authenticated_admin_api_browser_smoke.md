# Phase 8 Batch 47 — Authenticated Admin API Browser Smoke Test on EC2

## Goal

Verify that the EC2 deployment now supports protected admin access end to end:

- public website pages still load through Nginx;
- public read APIs still work;
- admin login page is reachable;
- anonymous admin/CRM API requests return `401`;
- authenticated admin/CRM API requests return `200` with a Cognito bearer token;
- `/docs`, `/redoc`, and `/openapi.json` remain blocked;
- direct public port `8000` remains blocked by the EC2 security group.

## Scope

This batch is a smoke-test/checklist batch. It does not change AWS resources and does not change Nginx by itself.

## Files

- `backend/scripts/check_ec2_authenticated_admin_api_smoke.py`
- `docs/phase8_batch47_authenticated_admin_api_browser_smoke.md`
- `docs/phase8_batch47_authenticated_admin_api_browser_checklist.md`
- `deploy/ec2/README_BATCH47_AUTHENTICATED_ADMIN_API_BROWSER_SMOKE.md`

## Required current state

Batch 46 must already be passing:

- `/admin/` and `/admin/login.html` are reachable.
- `/api/admin/auth/config` and `/api/admin/auth/status` are reachable.
- anonymous protected admin/CRM APIs return `401`.
- public pages and public APIs return `200`.
- developer docs stay blocked with `403`.

## Run read-only support check

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_authenticated_admin_api_smoke.py --base-url http://<PUBLIC_IPV4>
```

## Run authenticated check

Only run this after the browser login works.

```powershell
python scripts\check_ec2_authenticated_admin_api_smoke.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

The script prompts for the Cognito password using hidden input. Do not paste passwords into chat, logs, or Git.

## Manual browser check

Open:

```text
http://<PUBLIC_IPV4>/admin/login.html
```

Verify:

- login succeeds;
- no SMS or phone verification is requested;
- admin dashboard loads;
- product/brand/category/admin lists load data;
- customer, booking, and inquiry admin pages load data;
- logout clears the session and returns to login.

## Expected result

- Read-only support check passes.
- Authenticated check passes.
- Manual browser check passes.

## Rollback

If authenticated admin APIs fail, do not expose additional public routes. Reapply Batch 46 known-good Nginx configuration and confirm anonymous protected APIs return `401` rather than `200`.
