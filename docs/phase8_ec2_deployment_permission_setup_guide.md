# Phase 8 Batch 33 — EC2 Deployment Permission Setup Guide

## Purpose

Prepare the exact IAM and AWS Console steps needed before the future EC2 public-IP deployment batch.

This batch is still a **guide/setup-prep batch only**.

Do not create EC2 yet unless a later deployment batch explicitly says to do so.

## Current project baseline

| Item | Current status |
|---|---|
| AWS account | `537765358118` |
| Region | `ap-southeast-1` |
| CLI user | `rsa-cms-cli-user` |
| DynamoDB tables | Created and tested |
| EC2 deployment | Not started |
| Billing/cost alert | Must be manually confirmed before EC2 creation |
| Admin auth | Prepared, but not publicly enforceable yet |
| S3 binary upload | Prepared, but not enabled yet |
| Deployment rule | EC2 public IP first; Route 53/domain later |

## Required manual confirmations before adding EC2 permissions

| Check | Required | Status |
|---|---:|---|
| AWS Budget/cost alert is enabled and email recipient is verified | Yes | Pending |
| Free Tier usage alert checked/enabled if available | Yes | Pending |
| Public IPv4 hourly charge accepted for temporary demo | Yes | Pending |
| No Elastic IP unless explicitly approved | Yes | Pending |
| Admin will not be exposed publicly until Cognito enforcement | Yes | Pending |
| SSH source will be your IP `/32` only | Yes | Pending |
| No ALB, NAT Gateway, RDS, SMS/MFA, or paid notification drift | Yes | Pending |

## IAM setup approach

Use two separate permission paths:

```text
Human deployment user
→ can create/read the EC2 demo resources only when deployment is approved

EC2 instance role
→ used by the FastAPI backend on the server
→ can access only approved rsa_ DynamoDB tables/indexes
```

Do **not** put AWS access keys on the EC2 server.

## Part A — Human deployment permission

The current CLI user is intentionally limited. For actual EC2 creation, either:

1. Temporarily attach a limited deployment policy to `rsa-cms-cli-user`, or
2. Create a separate deployment IAM user/group with the limited deployment policy.

Preferred for safety:

```text
Use a separate deployment group or user.
Avoid AdministratorAccess.
Detach deployment permissions after EC2 setup if no longer needed.
```

Template included:

```text
deploy/iam/rsa-cms-ec2-deployment-minimum-policy.template.json
```

This template is intended for the deployment operator, not the EC2 instance.

It includes permission for:

- read EC2/VPC resources
- create one security group
- authorize/revoke security group ingress
- launch one small EC2 instance
- create tags
- pass only the RSA CMS EC2 instance role

It intentionally does **not** include:

- `AdministratorAccess`
- `ec2:CreateNatGateway`
- `elasticloadbalancing:*`
- `rds:*`
- `route53:*`
- `sns:*`
- broad IAM admin actions
- default terminate permission

## Part B — EC2 instance role

The EC2 server should have an IAM role, not access keys.

Create this role later when deployment is approved:

Suggested role name:

```text
rsa-cms-ec2-backend-role
```

Suggested instance profile name:

```text
rsa-cms-ec2-backend-profile
```

Use templates already prepared in the deploy folder:

```text
deploy/iam/rsa-cms-ec2-instance-trust-policy.template.json
deploy/iam/rsa-cms-ec2-instance-dynamodb-policy.template.json
```

Before use, replace:

```text
<ACCOUNT_ID>
<REGION>
```

with:

```text
537765358118
ap-southeast-1
```

## Part C — Security group

Suggested security group name:

```text
rsa-cms-ec2-demo-sg
```

Initial inbound rules:

| Purpose | Port | Source |
|---|---:|---|
| SSH | 22 | Your current public IP `/32` only |
| Temporary FastAPI smoke test | 8000 | Your current public IP `/32` only |

Do not open:

```text
22 from 0.0.0.0/0
8000 from 0.0.0.0/0
3389 from 0.0.0.0/0
large open port ranges
```

## Part D — AWS Console setup steps

### 1. Confirm billing alert first

Go to:

```text
AWS Console → Billing and Cost Management → Budgets
```

Confirm a budget/cost alert exists and the owner receives the alert email.

### 2. Create the EC2 instance role

Go to:

```text
IAM → Roles → Create role
```

Choose:

```text
Trusted entity type: AWS service
Use case: EC2
```

Attach a customer-managed policy based on:

```text
deploy/iam/rsa-cms-ec2-instance-dynamodb-policy.template.json
```

Name:

```text
rsa-cms-ec2-backend-role
```

### 3. Prepare the deployment permission policy

Go to:

```text
IAM → Policies → Create policy → JSON
```

Paste the reviewed template:

```text
deploy/iam/rsa-cms-ec2-deployment-minimum-policy.template.json
```

Replace placeholders first:

```text
<ACCOUNT_ID> → 537765358118
<REGION> → ap-southeast-1
<INSTANCE_PROFILE_NAME> → rsa-cms-ec2-backend-profile
```

Attach it only to the deployment user/group that will create the EC2 demo.

### 4. Run readiness check again

After permissions are added, run:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_deployment_preflight.py
python scripts\check_ec2_iam_security_readiness.py
```

Expected improvement:

```text
EC2 DescribeInstances should no longer show UnauthorizedOperation.
```

## Go / No-Go before Batch 34

Proceed to actual EC2 creation only if:

- billing alert is confirmed
- EC2 read/create permission is ready
- EC2 instance role is ready
- security group source IP is known
- admin will remain protected/not public
- public IPv4 temporary cost is accepted
- no Elastic IP is being used unless explicitly approved
