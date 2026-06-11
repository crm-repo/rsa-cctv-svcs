# Phase 8 Batch 32 — EC2 Deployment IAM and Security Checklist

## Purpose

Prepare the IAM and network security rules for the future EC2 public-IP deployment without creating or changing AWS resources in this batch.

This checklist follows the project rule:

```text
Free-Tier-first
One small EC2 instance
DynamoDB low-capacity tables
No ALB
No NAT Gateway
No RDS
No SMS/MFA/phone verification cost
No public admin without Cognito enforcement
```

## Current preflight result

The Batch 31 preflight passed locally.

Known current state:

- AWS account: `537765358118`
- Project region: `ap-southeast-1`
- Current CLI user: `rsa-cms-cli-user`
- DynamoDB tables: already created and tested
- EC2 `DescribeInstances`: not currently allowed for `rsa-cms-cli-user`
- Security groups can be read
- No RSA-specific security group exists yet

## IAM design

### 1. Human/deployment operator

Do not use broad `AdministratorAccess` for normal project deployment work.

The deployment operator should have only the permissions needed for the current step.

For preflight/readiness, the user only needs read-only EC2/VPC visibility:

- `ec2:DescribeInstances`
- `ec2:DescribeSecurityGroups`
- `ec2:DescribeVpcs`
- `ec2:DescribeSubnets`
- `ec2:DescribeImages`
- `ec2:DescribeKeyPairs`
- `ec2:DescribeInstanceTypes`
- `ec2:DescribeAvailabilityZones`

Actual EC2 create/run permissions should be added later only when the deployment batch is approved.

### 2. EC2 instance role

The EC2 server should not use hard-coded AWS access keys.

Use an EC2 IAM role/instance profile for the backend app.

The EC2 instance role should grant only the DynamoDB actions required by the app:

- read public/admin records
- write booking/inquiry/customer records
- update admin records
- update ID counters

Use the template:

```text
deploy/iam/rsa-cms-ec2-instance-dynamodb-policy.template.json
```

Replace:

```text
<ACCOUNT_ID>
<REGION>
```

before use.

### 3. Trust policy

Use the EC2 trust policy template:

```text
deploy/iam/rsa-cms-ec2-instance-trust-policy.template.json
```

This allows EC2 to assume the role.

## Security group design

### Minimum inbound rules for first private smoke test

| Purpose | Port | Source |
|---|---:|---|
| SSH | 22 | Your current public IP `/32` only |
| Temporary FastAPI smoke test | 8000 | Your current public IP `/32` only |

### Later web test through nginx

| Purpose | Port | Source |
|---|---:|---|
| HTTP | 80 | Public only when public web test is approved |
| HTTPS | 443 | Public only when SSL/domain/CloudFront path is approved |

Do not open SSH or port 8000 to:

```text
0.0.0.0/0
::/0
```

## Admin exposure rule

Admin pages/routes must not be exposed publicly until Cognito JWT enforcement is enabled.

Allowed before Cognito enforcement:

- localhost testing
- private/IP-restricted smoke testing from your own IP only

Not allowed before Cognito enforcement:

- public admin access
- public unauthenticated admin API
- open admin route from `0.0.0.0/0`

## Secrets rule

Never commit:

- `.env`
- AWS access keys
- Cognito secrets
- admin passwords
- private keys
- SSH `.pem` files

The EC2 `.env` file should live on the server only.

## Public IPv4 cost reminder

Keep public-IP testing short and monitored. Do not allocate Elastic IP unless explicitly approved.

## Go / No-Go

Before actual EC2 creation:

| Check | Required | Status |
|---|---:|---|
| Billing alert confirmed manually | Yes | Pending |
| EC2 read permissions confirmed | Yes | Pending |
| Security group plan reviewed | Yes | Pending |
| EC2 instance role policy reviewed | Yes | Pending |
| No AWS keys planned on EC2 | Yes | Pending |
| Admin public exposure blocked until Cognito enforcement | Yes | Pending |
| Public IPv4 temporary cost accepted | Yes | Pending |
