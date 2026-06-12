# Phase 8 Batch 40 — Cognito Admin Auth Activation Plan and Preflight

## Purpose

Batch 40 prepares the RSA CMS admin authentication path before admin access is exposed from EC2.

The goal is to keep the public website working while admin pages, admin APIs, customer/lead management APIs, and API documentation remain blocked until Cognito/JWT enforcement is verified.

## Current safe state

Before Batch 41, the EC2 deployment should remain in this state:

- Public frontend: available through Nginx on port 80.
- Public read APIs: available through Nginx.
- Public booking/inquiry POST APIs: available through Nginx.
- Direct backend port 8000: blocked from public internet.
- `/admin/`: blocked by Nginx.
- `/api/admin/*`: blocked by Nginx.
- `/api/customers`, `/api/bookings`, `/api/inquiries`: blocked by Nginx for public GET/admin surfaces.
- `/docs`, `/redoc`, `/openapi.json`: blocked by Nginx.
- `RSA_ADMIN_AUTH_MODE=disabled` on EC2 until Batch 41.

## Free-Tier-first constraints

Do not enable SMS, phone-number login, phone verification, SMS MFA, paid notification workflows, ALB, NAT Gateway, RDS, Route 53, or Elastic IP as part of this batch.

Preferred Cognito setup for this project:

- Email/password admin login.
- Email verification only if needed.
- No phone number as required sign-in attribute.
- No SMS MFA.
- No Cognito hosted domain unless explicitly required later.
- One admin app client for the static admin login flow.

## Required Cognito values for Batch 41

After manual Cognito setup, record these values locally, but do not commit real secrets or production `.env` files:

```text
RSA_ADMIN_AUTH_MODE=cognito
RSA_COGNITO_REGION=ap-southeast-1
RSA_COGNITO_USER_POOL_ID=<user-pool-id>
RSA_COGNITO_APP_CLIENT_ID=<app-client-id>
```

For Batch 40, keep EC2 runtime as:

```text
RSA_ADMIN_AUTH_MODE=disabled
```

## Preflight command

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_cognito_admin_auth_preflight.py
```

If EC2 is running and you want to verify public lockdown remains intact:

```powershell
python scripts\check_cognito_admin_auth_preflight.py --base-url http://<EC2_PUBLIC_IPV4>
```

Expected public lockdown results:

```text
GET / -> HTTP 200
GET /api/health -> HTTP 200
GET /admin/ -> HTTP 403
GET /api/admin/products -> HTTP 403
GET /api/customers -> HTTP 403
GET /api/bookings -> HTTP 403
GET /api/inquiries -> HTTP 403
GET /docs -> HTTP 403
GET /redoc -> HTTP 403
GET /openapi.json -> HTTP 403
```

## Rollback/safety notes

If anything looks wrong during Batch 40:

1. Do not expose `/admin/`.
2. Keep `RSA_ADMIN_AUTH_MODE=disabled` on EC2.
3. Keep Nginx Batch 38 lockdown active.
4. Stop EC2 if no further testing is needed.

## Exit criteria

Batch 40 is complete when:

- Cognito setup checklist is available.
- Admin-auth environment example is available.
- Preflight script runs locally.
- If EC2 is running, public lockdown check confirms admin/management routes remain blocked.
- No new paid AWS resources outside the Cognito prep scope were created.
