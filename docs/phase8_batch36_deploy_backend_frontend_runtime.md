# Phase 8 Batch 36 — Deploy Backend/Frontend Files to EC2 and Configure Runtime

## Goal

Batch 36 deploys the current Git-tracked RSA CMS project files to the Batch 34/35 EC2 demo instance, installs backend dependencies, creates a safe runtime environment file, starts the FastAPI backend with systemd, and verifies `/api/health`.

This batch uses the existing EC2 instance. It does **not** create new AWS resources.

## Safety rules

- Start EC2 only while actively working on this batch.
- Do not store AWS access keys on EC2.
- Use the EC2 instance profile `rsa-cms-ec2-backend-role` for DynamoDB access.
- Do not commit `.pem`, `.env`, or server secrets.
- Do not open SSH or port `8000` to `0.0.0.0/0`.
- Do not create Elastic IP, Route 53, ALB, NAT Gateway, RDS, SMS, or paid notification resources.
- Admin auth may still be disabled, so keep port `8000` restricted to your IP only.

## Expected EC2 details

| Item | Expected value |
|---|---|
| Region | `ap-southeast-1` |
| Instance name | `rsa-cms-demo-backend` |
| SSH user | `ubuntu` |
| IAM instance profile | `rsa-cms-ec2-backend-role` |
| Security group | `rsa-cms-demo-backend-sg` |
| Backend port | `8000`, your IP only |
| Runtime mode | `RSA_REPOSITORY_MODE=dynamodb` |

## Step 1 — Start EC2 and get current public IP

Since the project is not using Elastic IP, the public IPv4 may change after stopping/starting.

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_demo_instance_status.py
```

Copy the current `Public IPv4` value.

## Step 2 — Run Batch 36 status check before deploy

```powershell
python scripts\check_ec2_app_runtime_status.py
```

Before deployment, the public `/api/health` may fail. That is normal.

## Step 3 — Deploy the Git-tracked project release to EC2

From local PowerShell project root, replace `<PUBLIC_IPV4>` with the current public IP:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

powershell -ExecutionPolicy Bypass -File .\deploy\ec2\deploy_rsa_cms_release_to_ec2.ps1 `
  -KeyPath "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" `
  -HostName "<PUBLIC_IPV4>" `
  -SshUser "ubuntu"
```

The deployment script creates a clean `git archive` zip from `HEAD`, uploads it to `/tmp/rsa-cms-release.zip`, installs it under `/opt/rsa-cms/releases/<timestamp>`, points `/opt/rsa-cms/current` to that release, installs backend Python requirements into `/opt/rsa-cms/venv`, creates `/opt/rsa-cms/runtime/backend.env` if missing, and starts `rsa-cms-backend.service`.

## Step 4 — Check runtime on EC2

SSH into the server:

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
```

Then run:

```bash
/tmp/check_rsa_cms_app_runtime.sh
```

Send the output back for review.

## Step 5 — Check public API from local PowerShell

```powershell
curl http://<PUBLIC_IPV4>:8000/api/health
```

Optional:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_app_runtime_status.py --check-public-health
```

## Useful server commands

Check service:

```bash
sudo systemctl status rsa-cms-backend --no-pager
```

Restart service:

```bash
sudo systemctl restart rsa-cms-backend
```

View logs:

```bash
sudo journalctl -u rsa-cms-backend -n 120 --no-pager
```

View runtime environment file:

```bash
sudo cat /opt/rsa-cms/runtime/backend.env
```

## End of Batch 36

When Batch 36 passes, stop the EC2 instance unless Batch 37 starts immediately.
