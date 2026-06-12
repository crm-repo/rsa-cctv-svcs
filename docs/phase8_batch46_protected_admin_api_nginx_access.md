# Phase 8 Batch 46 — Protected Admin API Access Through Nginx

## Goal

Expose admin/CRM management API routes through Nginx only after backend Cognito bearer-token enforcement is active.

This batch changes the deployment from:

- `/admin/` reachable
- `/api/admin/auth/*` reachable
- admin/CRM data APIs blocked by Nginx

To:

- `/admin/` reachable
- `/api/admin/auth/*` reachable
- `/api/admin/*`, `/api/customers`, `/api/bookings`, and `/api/inquiries` reachable through Nginx
- anonymous admin/CRM API requests rejected by backend with `401`
- authenticated admin requests accepted using Cognito access tokens
- `/docs`, `/redoc`, and `/openapi.json` still blocked publicly

## Safety notes

- Do not expose direct port `8000` publicly.
- Do not enable `/docs`, `/redoc`, or `/openapi.json` publicly.
- Do not store AWS access keys on EC2.
- Public POST `/api/bookings` and POST `/api/inquiries` remain available for public forms.
- Anonymous GET/list/admin access must return `401`.

## Files

- `backend/app/middleware/admin_route_auth.py`
- `backend/app/main.py`
- `backend/scripts/check_ec2_protected_admin_api_smoke.py`
- `deploy/ec2/configure_rsa_cms_nginx_protected_admin_api_access.sh`
- `deploy/ec2/check_rsa_cms_nginx_protected_admin_api_access.sh`

## Validation

1. Deploy latest code to EC2.
2. Apply the Batch 46 Nginx config.
3. Run the EC2-side check script.
4. Run the local read-only smoke check.
5. Optionally run the local authenticated Cognito smoke check.

Expected result:

- Public pages/API: `200`
- Admin login/auth endpoints: `200`
- Anonymous protected admin/CRM APIs: `401`
- Authenticated protected admin/CRM APIs: `200`
- Developer docs: `403`
