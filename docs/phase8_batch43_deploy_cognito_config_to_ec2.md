# Phase 8 Batch 43 — Deploy Cognito Auth Config to EC2 While Keeping Admin Blocked

## Goal

Deploy the latest backend/frontend code to the EC2 demo instance, update the EC2 backend runtime environment to Cognito mode, and verify the backend can read Cognito configuration locally on the instance.

This batch must **not** expose the admin UI or admin APIs publicly yet. Nginx must continue to return `403` for `/admin/`, `/api/admin/*`, CRM/admin management APIs, `/docs`, and `/openapi.json`.

## Known Cognito values for this environment

Use the values from Batch 41:

```text
RSA_ADMIN_AUTH_MODE=cognito
RSA_COGNITO_REGION=ap-southeast-1
RSA_COGNITO_USER_POOL_ID=ap-southeast-1_BNvYFNmw9
RSA_COGNITO_CLIENT_ID=3r13vplp8agjigm3e52ficsm1e
```

Do not store or commit the Cognito admin user's password.

## EC2 cost reminder

Start EC2 only when deploying/testing this batch. Stop it after the batch if not continuing immediately.

## Steps

### 1. Start EC2 and confirm current public IP

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_demo_instance_status.py
```

Use the current `Public IPv4` in the commands below.

### 2. Deploy the latest project release to EC2

This is required because Batch 42 changed backend/admin auth code locally and must be deployed to EC2 before Cognito mode can work there.

From project root:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

powershell -ExecutionPolicy Bypass -File .\deploy\ec2\deploy_rsa_cms_release_to_ec2.ps1 `
  -ProjectRoot "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project" `
  -KeyPath "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" `
  -HostName "<PUBLIC_IPV4>" `
  -SshUser "ubuntu"
```

### 3. Copy Batch 43 scripts to EC2

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\update_rsa_cms_cognito_env.sh ubuntu@<PUBLIC_IPV4>:/tmp/update_rsa_cms_cognito_env.sh

scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_cognito_runtime.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_cognito_runtime.sh
```

### 4. SSH into EC2

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
```

### 5. Apply Cognito env values and restart backend

Inside the EC2 SSH session:

```bash
chmod +x /tmp/update_rsa_cms_cognito_env.sh /tmp/check_rsa_cms_cognito_runtime.sh

sudo RSA_COGNITO_REGION="ap-southeast-1" \
  RSA_COGNITO_USER_POOL_ID="ap-southeast-1_BNvYFNmw9" \
  RSA_COGNITO_CLIENT_ID="3r13vplp8agjigm3e52ficsm1e" \
  /tmp/update_rsa_cms_cognito_env.sh

/tmp/check_rsa_cms_cognito_runtime.sh
```

Expected: `Batch 43 Cognito backend runtime check PASSED.`

### 6. Public lockdown check from local PowerShell

Exit SSH first if desired:

```bash
exit
```

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_cognito_public_lockdown.py --base-url http://<PUBLIC_IPV4>
```

Expected: public website/API endpoints return `200`; `/admin/`, `/api/admin/*`, CRM/admin management APIs, `/docs`, and `/openapi.json` return `403`; direct port `8000` is unreachable.

## Pass criteria

- Latest app release deployed to EC2.
- `/opt/rsa-cms/runtime/backend.env` has Cognito mode and correct Cognito IDs.
- No AWS access keys are stored in `backend.env`.
- `rsa-cms-backend.service` is active.
- EC2-local backend `/api/admin/auth/config` returns Cognito mode.
- Nginx still blocks admin/auth/management routes publicly.
- Direct public port `8000` remains blocked.
