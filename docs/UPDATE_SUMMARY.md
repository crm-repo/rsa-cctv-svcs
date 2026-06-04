# RSA CMS / Mini-CRM Documentation Update Summary

## Update Purpose

This package updates the primary Markdown project source files to explicitly document the AWS Free-Tier-first rule that has governed the project from the initial requirements and analysis phase.

## Core Rule Added

```text
First 12 months: AWS Free-Tier-first deployment
Expected paid exception: Route 53/domain, after IP-based testing/demo
Before Route 53: test/demo using EC2 public IP or another free AWS-provided endpoint
After Free Tier: continue as a low-cost AWS deployment
```

## Main Guardrails Documented

- Use one Free-Tier-eligible EC2 micro instance.
- Use DynamoDB with low provisioned capacity and minimal indexes.
- Use S3 for compressed/optimized images.
- Use Cognito admin-only authentication.
- Disable Cognito SMS/MFA/phone verification where possible.
- Store booking/inquiry requests in the admin panel; no required SMS/email notifications for launch.
- Avoid ALB, NAT Gateway, RDS, multiple always-on EC2 instances, paid notification workflows and unnecessary paid monitoring.
- Configure AWS billing alerts before public testing.

## Markdown Files Updated

- PRIMARY_architecture.md
- PRIMARY_requirements.md
- PRIMARY_decision-log.md
- PRIMARY_implementation-guidelines.md
- PRIMARY_open-issues.md
- PRIMARY_project-overview.md
- PRIMARY_feature-status.md

## Notes

The PDF handbook was not regenerated in this package. It should be regenerated from these updated Markdown source files when the project documentation PDF is refreshed.
