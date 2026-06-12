# Phase 8 Batch 37 — Nginx public-site proxy on EC2

## Purpose

Configure the EC2 demo instance so the public website is served through Nginx on port 80 and public API calls are proxied to the local FastAPI backend on port 8000.

This keeps FastAPI running locally behind Nginx and blocks the admin UI from public access until Cognito/JWT enforcement is enabled.

## Safety rules

- Keep EC2 running only while configuring/testing.
- Do not use Elastic IP yet.
- Do not use ALB, NAT Gateway, RDS, Route 53, or paid notification services.
- Do not store AWS access keys on EC2.
- Do not expose `/admin` publicly while `RSA_ADMIN_AUTH_MODE=disabled`.
- Open port 80 only to your current IP `/32` for this smoke test.
- After Nginx works, remove direct public access to port 8000.

## Files

- `deploy/ec2/configure_rsa_cms_nginx.sh`
- `deploy/ec2/check_rsa_cms_nginx_public_site.sh`
- `backend/scripts/check_ec2_public_site_status.py`

## Steps

### 1. Start EC2 and confirm current public IP

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_demo_instance_status.py
```

Use the current `Public IPv4` shown by the script.

### 2. Copy scripts to EC2

From project root:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\configure_rsa_cms_nginx.sh ubuntu@<PUBLIC_IPV4>:/tmp/configure_rsa_cms_nginx.sh

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_nginx_public_site.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_nginx_public_site.sh
```

### 3. Run Nginx configuration on EC2

```bash
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
chmod +x /tmp/configure_rsa_cms_nginx.sh /tmp/check_rsa_cms_nginx_public_site.sh
sudo /tmp/configure_rsa_cms_nginx.sh
/tmp/check_rsa_cms_nginx_public_site.sh
```

### 4. Update security group for browser smoke test

In AWS Console:

```text
EC2 → Security Groups → rsa-cms-demo-backend-sg → Inbound rules → Edit inbound rules
```

Keep:

```text
SSH TCP 22 Source: your current IP /32
```

Add:

```text
HTTP TCP 80 Source: your current IP /32
```

After Nginx/API proxy checks pass, remove direct public backend access:

```text
Custom TCP 8000 Source: your current IP /32
```

Do not add `0.0.0.0/0` yet for Batch 37.

### 5. Verify from local PowerShell

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_public_site_status.py
```

Expected:

- `/` returns 200
- `/api/health` returns 200
- `/api/products` returns 200
- `/admin/` returns 403

## End of batch

If not continuing immediately, stop EC2 to avoid running costs.
