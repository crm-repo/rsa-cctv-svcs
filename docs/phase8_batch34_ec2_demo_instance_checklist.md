# Phase 8 Batch 34 — EC2 Demo Instance Checklist

## Before launch

| Check | Status | Notes |
|---|---|---|
| Budget/cost alert manually confirmed | Pending | Required before EC2 |
| Public IPv4 cost/free-tier review accepted | Pending | Keep instance online only when needed |
| Current public IP copied with `/32` | Pending | Do not use `0.0.0.0/0` |
| Key pair `rsa-cms-demo-key` created and stored outside repo | Pending | Never commit `.pem` |
| Security group `rsa-cms-demo-backend-sg` created | Pending | SSH and 8000 from your IP only |
| EC2 role `rsa-cms-ec2-backend-role` exists | Done/Pending | Should already be done from Batch 33 |
| Deployment preflight passed | Done/Pending | Batch 31/32 checks |

## Launch values

| Field | Required value |
|---|---|
| Name tag | `rsa-cms-demo-backend` |
| Region | `ap-southeast-1` |
| AMI | Ubuntu Server LTS, Free-Tier-labeled |
| Instance type | Free-Tier-labeled micro instance |
| Public IP | Auto-assign enabled |
| IAM role/profile | `rsa-cms-ec2-backend-role` |
| Security group | `rsa-cms-demo-backend-sg` |
| Storage | `8 GiB`, one root volume only |
| Elastic IP | Do not allocate |

## Security group rules

| Rule | Required source |
|---|---|
| SSH `22` | Your public IP `/32` only |
| FastAPI temporary `8000` | Your public IP `/32` only |
| HTTP `80` | Not yet |
| HTTPS `443` | Not yet |
| RDP `3389` | Not allowed |
| All traffic | Not allowed from public internet |

## After launch

Run locally:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_demo_instance_status.py
```

SSH test:

```powershell
ssh -i "$env:USERPROFILE\.ssh\rsa-cms-demo-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

Inside EC2:

```bash
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Expected:

```text
rsa-cms-ec2-backend-role
```

## Stop when not testing

```text
EC2 → Instances → rsa-cms-demo-backend → Instance state → Stop instance
```
