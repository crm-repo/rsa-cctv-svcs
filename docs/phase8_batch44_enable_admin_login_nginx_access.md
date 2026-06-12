# Phase 8 Batch 44 — Enable Protected Admin Login Access Through Nginx

## Purpose

Batch 44 opens the admin **login/static UI surface** through Nginx while keeping admin data and CRM management APIs blocked until the next protected API exposure batch.

This is intentionally conservative:

- Public website pages remain available.
- Approved public read APIs remain available.
- Public booking/inquiry POST endpoints remain available.
- `/admin/` and `/admin/login.html` become reachable so the browser can load the admin login experience.
- `/api/admin/auth/*` becomes reachable so login/config/status calls can reach the Cognito-enabled backend.
- `/api/admin/products`, `/api/customers`, `GET /api/bookings`, `GET /api/inquiries`, `/docs`, `/redoc`, and `/openapi.json` remain blocked by Nginx.

## Prerequisites

- Batch 41 Cognito user pool check passed.
- Batch 42 local Cognito admin login check passed.
- Batch 43 EC2 backend Cognito runtime check passed.
- EC2 backend runtime has `RSA_ADMIN_AUTH_MODE=cognito`.
- Nginx Batch 38 lockdown is already active.

## EC2 Cost Reminder

Start EC2 only while applying and testing this batch. Stop it when the batch is complete unless continuing immediately.

## Apply

From local PowerShell, copy scripts to EC2 using the current public IP:

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\configure_rsa_cms_nginx_admin_login_access.sh ubuntu@<PUBLIC_IPV4>:/tmp/configure_rsa_cms_nginx_admin_login_access.sh

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_nginx_admin_login_access.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_nginx_admin_login_access.sh
```

SSH to EC2:

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
```

Run:

```bash
chmod +x /tmp/configure_rsa_cms_nginx_admin_login_access.sh /tmp/check_rsa_cms_nginx_admin_login_access.sh
sudo /tmp/configure_rsa_cms_nginx_admin_login_access.sh
/tmp/check_rsa_cms_nginx_admin_login_access.sh
```

## Expected Result

Allowed through Nginx:

- `/`
- `/products.html`
- `/booking.html`
- `/api/health`
- `/api/products`
- `/api/brands`
- `/admin/`
- `/admin/login.html`
- `/api/admin/auth/config`
- `/api/admin/auth/status`
- `POST /api/admin/auth/cognito-login`

Blocked through Nginx:

- `/api/admin/products`
- `/api/customers`
- `GET /api/bookings`
- `GET /api/inquiries`
- `/docs`
- `/redoc`
- `/openapi.json`

## Local Public Smoke Check

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_admin_login_public_smoke.py --base-url http://<PUBLIC_IPV4>
```

Optional real Cognito login test:

```powershell
python scripts\check_ec2_admin_login_public_smoke.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

Do not paste passwords into chat or commit them to Git.

## Rollback

The configure script backs up the previous Nginx config under:

```text
/opt/rsa-cms/backups/nginx/
```

To rollback, copy the latest pre-Batch-44 backup to `/etc/nginx/sites-available/rsa-cms.conf`, then run:

```bash
sudo nginx -t
sudo systemctl reload nginx
```
