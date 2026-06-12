# RSA CMS Batch 40 — Cognito Admin Auth Preflight

This batch prepares the Cognito admin-auth activation path without exposing the admin UI publicly.

## What this batch does

- Documents the Free-Tier-safe Cognito setup approach.
- Adds a read-only preflight script.
- Adds an EC2 admin-auth environment example.
- Keeps `/admin/`, admin APIs, CRM APIs, `/docs`, `/redoc`, and `/openapi.json` blocked through Nginx.

## What this batch does not do

- It does not create Cognito resources automatically.
- It does not expose `/admin/` publicly.
- It does not enable `RSA_ADMIN_AUTH_MODE=cognito` on EC2.
- It does not create SMS, MFA, Route 53, ALB, NAT Gateway, RDS, SNS, or paid notification workflows.

## Safe sequence

1. Keep EC2 stopped while preparing docs/files unless you are testing the public lockdown check.
2. Create Cognito manually using the checklist.
3. Keep admin blocked in Nginx.
4. Run the preflight script.
5. Commit/push Batch 40.
6. Use Batch 41 to enable protected admin access only after Cognito values are confirmed.
