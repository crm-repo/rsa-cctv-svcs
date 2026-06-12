# Phase 8 Batch 38 — Nginx public API exposure lockdown

## Purpose

Batch 37 made the public website available through Nginx on port 80. Batch 38 tightens that Nginx configuration so the browser-facing public site exposes only approved public routes.

This is needed because admin authentication is still disabled for the current local/demo phase. Until Cognito/JWT enforcement is enabled, Nginx must block public access to the admin UI and admin/CRM management APIs.

## What remains public

- Static public website pages under `/`
- Read-only public catalog/CMS APIs:
  - `/api/health`
  - `/api/products...`
  - `/api/brands...`
  - `/api/categories...`
  - `/api/key-features...`
  - `/api/package-banners...`
  - `/api/about...`
  - `/api/project-gallery...`
  - `/api/services...`
  - `/api/contact...`
  - `/api/contact-persons...`
  - `/api/social-media...`
  - `/api/pages/...`
- Public form creation only:
  - `POST /api/bookings`
  - `POST /api/inquiries`

## What is blocked publicly

- `/admin` and `/admin/`
- `/api/admin...`
- `/api/customers...`
- `GET/PUT/detail access` for `/api/bookings...`
- `GET/PUT/detail access` for `/api/inquiries...`
- `/docs`, `/redoc`, and `/openapi.json`
- Any unapproved `/api/...` route
- Direct public access to FastAPI port `8000`

## Safety rules

- Keep EC2 running only while configuring/testing.
- Keep security group inbound rules limited to your current IP `/32`.
- Keep SSH on port 22 limited to your current IP `/32`.
- Keep HTTP on port 80 limited to your current IP `/32` during demo smoke testing.
- Do not reopen port 8000 publicly.
- Do not expose `/admin` while `RSA_ADMIN_AUTH_MODE=disabled`.
- Do not create Elastic IP, ALB, NAT Gateway, RDS, Route 53, or paid SMS/MFA resources in this batch.

## Files

- `deploy/ec2/configure_rsa_cms_nginx_api_lockdown.sh`
- `deploy/ec2/check_rsa_cms_nginx_api_lockdown.sh`
- `backend/scripts/check_ec2_public_api_lockdown_status.py`

## Steps

### 1. Confirm EC2 is running and get the current public IP

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_demo_instance_status.py
```

Use the current `Public IPv4` shown by the script.

### 2. Copy Batch 38 scripts to EC2

From project root:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\configure_rsa_cms_nginx_api_lockdown.sh ubuntu@<PUBLIC_IPV4>:/tmp/configure_rsa_cms_nginx_api_lockdown.sh

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_nginx_api_lockdown.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_nginx_api_lockdown.sh
```

### 3. Apply the Nginx lockdown on EC2

```bash
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
chmod +x /tmp/configure_rsa_cms_nginx_api_lockdown.sh /tmp/check_rsa_cms_nginx_api_lockdown.sh
sudo /tmp/configure_rsa_cms_nginx_api_lockdown.sh
/tmp/check_rsa_cms_nginx_api_lockdown.sh
```

### 4. Run the local Batch 38 status check

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_public_api_lockdown_status.py
```

Expected results:

- Public pages return `200`.
- Public read APIs return `200`.
- `/admin/` returns `403`.
- `/api/admin/products` returns `403`.
- `/api/customers` returns `403`.
- `GET /api/bookings` returns `403`.
- `GET /api/inquiries` returns `403`.
- `/docs` and `/openapi.json` return `403`.
- `http://<PUBLIC_IPV4>:8000/api/health` is unreachable/blocked.

### 5. Optional public form write smoke test

Only run this when you intentionally want to create one test booking and one test inquiry in DynamoDB:

```powershell
python scripts\check_ec2_public_api_lockdown_status.py --execute-public-form-write --confirm-write-test
```

## End of batch

If not continuing immediately, stop EC2 to avoid running costs.
