# RSA CMS EC2 Deployment Permission Setup — AWS Console Steps

## 1. Create EC2 backend instance role

AWS Console:

```text
IAM → Roles → Create role
```

Choose:

```text
Trusted entity: AWS service
Use case: EC2
```

Role name:

```text
rsa-cms-ec2-backend-role
```

Attach DynamoDB policy based on:

```text
deploy/iam/rsa-cms-ec2-instance-dynamodb-policy.template.json
```

Replace placeholders first.

## 2. Confirm or create instance profile

Normally, the AWS Console creates the matching instance profile for an EC2 role.

Expected role/profile relationship:

```text
Role: rsa-cms-ec2-backend-role
Instance profile: rsa-cms-ec2-backend-role
```

If using CLI later, confirm the actual instance profile name before using `iam:PassRole`.

## 3. Create limited deployment policy

AWS Console:

```text
IAM → Policies → Create policy → JSON
```

Use:

```text
deploy/iam/rsa-cms-ec2-deployment-minimum-policy.template.json
```

Replace:

```text
<ACCOUNT_ID>
<REGION>
```

Recommended policy name:

```text
rsa-cms-ec2-deployment-minimum-policy
```

## 4. Attach deployment policy

Attach only to the deployment user/group.

Suggested user/group:

```text
rsa-cms-cli-user
```

or a separate deployment group:

```text
rsa-cms-deployers
```

## 5. Re-run local checks

```powershell
python scripts\check_ec2_deployment_preflight.py
python scripts\check_ec2_iam_security_readiness.py
```

Proceed to EC2 creation only after checks are acceptable and billing alerts are confirmed.
