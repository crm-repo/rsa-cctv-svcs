# Phase 8 Batch 33 — EC2 Permission Setup Checklist

## Manual checklist

| Step | Status | Notes |
|---|---|---|
| Confirm AWS Budget/cost alert email | Pending | Required before EC2 |
| Confirm Free Tier usage alert if available | Pending | Required before public/external testing |
| Confirm current public IP for SSH source | Pending | Use `/32` |
| Review deployment minimum IAM policy | Pending | Do not use AdministratorAccess |
| Create/review EC2 instance role | Pending | Use role, not keys |
| Attach DynamoDB table policy to EC2 role | Pending | Approved `rsa_` tables only |
| Attach limited deployment policy to deployment user/group | Pending | Only when ready for EC2 |
| Confirm `ec2:DescribeInstances` works | Pending | Re-run Batch 31/32 checks |
| Confirm no public SSH rule exists | Pending | No `0.0.0.0/0` |
| Confirm no public admin exposure before Cognito | Pending | Required |
| Confirm no Elastic IP | Pending | Unless explicitly approved |
| Confirm no ALB/NAT/RDS/SMS | Pending | Required |

## After permission setup

Run:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_deployment_preflight.py
python scripts\check_ec2_iam_security_readiness.py
```

Expected:

```text
EC2 DescribeInstances: OK
Security group read check: OK
No risky public inbound rules
```

IAM read warnings are acceptable if the selected deployment identity is intentionally limited.
