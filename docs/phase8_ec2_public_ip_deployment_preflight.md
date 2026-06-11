# Phase 8 Batch 31 — EC2 Public-IP Deployment Preflight Plan

## Purpose

Prepare for a safe EC2 public-IP demo/deployment without creating resources yet.

This is a planning/preflight batch only. Do not expose the admin panel publicly until Cognito enforcement is enabled.

## Deployment principle

Use the simplest Free-Tier-first style path:

```text
GitHub/local project
→ one small EC2 instance
→ backend FastAPI via Uvicorn/systemd
→ static frontend served locally or by nginx later
→ test by EC2 public IP first
→ Route 53/domain only after demo is approved
```

## Hard cost guardrails

Do not use these for the initial demo:

- Application Load Balancer
- NAT Gateway
- RDS
- Multiple always-on EC2 instances
- SMS/MFA/phone verification
- Paid notifications
- Route 53/domain before IP-based testing
- Elastic IP unless explicitly approved

## Important public IPv4 note

AWS charges for public IPv4 addresses. The preflight decision is therefore:

- Public IP testing is acceptable for a short controlled demo.
- Avoid Elastic IP unless explicitly approved.
- Stop or terminate the instance when not needed.
- Monitor Billing/Cost Management.

## Required manual confirmations before creating EC2

| Check | Required | Status |
|---|---:|---|
| AWS Budget/cost alert exists and email recipient is verified | Yes | Pending |
| Free Tier usage alert checked/enabled if available | Yes | Pending |
| Account region confirmed as `ap-southeast-1` for app resources | Yes | Pending |
| EC2 instance type selected from the console's current Free Tier eligible choices | Yes | Pending |
| Storage volume size kept small | Yes | Pending |
| No Elastic IP unless explicitly approved | Yes | Pending |
| Security group allows SSH only from your IP | Yes | Pending |
| Security group does not expose admin until Cognito enforcement | Yes | Pending |
| DynamoDB tables already verified ACTIVE | Yes | Complete |
| Mock mode remains local default | Yes | Complete |
| DynamoDB mode used only intentionally | Yes | Complete |

## Suggested security group for first backend smoke test

Use minimum inbound exposure.

| Purpose | Port | Source |
|---|---:|---|
| SSH | 22 | Your current public IP only |
| Temporary FastAPI smoke test | 8000 | Your current public IP only |

Do not open SSH or admin ports to `0.0.0.0/0`.

After nginx/Cognito/hardening, public web traffic can move to standard ports, but that is not part of this preflight batch.

## Backend environment plan

Prepare an EC2 `.env` file from `deploy/ec2/backend.ec2.env.example`.

Rules:

- Never commit real `.env`.
- Do not put AWS access keys in `.env` for EC2.
- Prefer an IAM role attached to the EC2 instance for AWS access.
- Keep `RSA_REPOSITORY_MODE=dynamodb` only on the EC2 deployment when AWS-backed data is intended.
- Keep notifications disabled unless explicitly approved.

## EC2 folder plan

Suggested folder:

```text
/opt/rsa-cms/
├── backend/
├── frontend/
├── venv/
├── logs/
└── .env
```

## Preflight script

Run from local backend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_deployment_preflight.py
```

The script is read-only. It does not create EC2 instances, security groups, IAM roles, or any other AWS resources.
