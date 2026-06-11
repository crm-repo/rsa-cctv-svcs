# Phase 8 Batch 30 — AWS Cost Safety and Billing Alerts Checklist

## Purpose

Before public/external AWS testing, the project must have cost-safety controls in place.

This checklist keeps the RSA CMS / Mini-CRM aligned with the AWS Free-Tier-first rule:

- Avoid ALB.
- Avoid NAT Gateway.
- Avoid RDS.
- Avoid multiple always-on EC2 instances.
- Avoid SMS, phone verification, and SMS MFA unless explicitly approved.
- Avoid unnecessary paid notifications.
- Delay Route 53/domain until after EC2 public-IP testing/demo.

## Required before public/external AWS testing

| Item | Required | Status |
|---|---:|---|
| AWS Budget or cost alert configured | Yes | Pending manual confirmation |
| Free Tier usage alert checked/enabled if available | Yes | Pending manual confirmation |
| Billing email recipient verified | Yes | Pending manual confirmation |
| Free-Tier deployment review completed | Yes | Pending |
| EC2 public-IP deployment plan reviewed | Yes | Pending |
| Admin is not publicly exposed without Cognito enforcement | Yes | Pending |
| Mock repository mode remains default locally | Yes | Complete |
| DynamoDB mode only used intentionally | Yes | Complete |

## Recommended AWS Budget setup

Create a monthly cost budget with email alerts.

Suggested thresholds for this project:

| Alert | Type | Suggested threshold |
|---|---|---:|
| Early warning | Actual cost | 50% |
| Strong warning | Actual cost | 80% |
| Hard warning | Actual cost | 100% |
| Forecast warning | Forecasted cost | 100% |

Use a low project budget amount that the owner is comfortable with. For a Free-Tier-first demo, this should normally be a small amount because Route 53/domain is expected to be the main planned paid exception later.

## Recommended Free Tier usage check

In AWS Billing and Cost Management, check whether Free Tier usage alerts are enabled/available for the account and confirm the owner receives the alert email.

## Optional CloudWatch billing alarm

A CloudWatch estimated-charge billing alarm is optional. If used, remember:

- Billing metric data is in `us-east-1`.
- Billing alerts must be enabled first.
- This should only be added if the owner approves the additional monitoring setup.

## Read-only script

Run:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_aws_cost_safety.py
```

The script does not create, update, or delete AWS resources.

It checks:

- AWS CLI identity.
- CLI region vs project region.
- Approved DynamoDB table presence.
- Whether Budgets can be listed with the current IAM user.

If Budgets cannot be listed, use the AWS console/root/management account or a billing-enabled IAM user to confirm manually.
