# Phase 8 Batch 60B — Backup / Restore / Production Safety Notes

Project: RSA CMS / Mini-CRM  
Status: Planned  
Current anchor: Runs after Batch 60A demo-readiness pass or before treating data as production  
Prepared: 2026-06-16

## Purpose

Batch 60B creates the backup, restore, and rollback safety procedures required before the project is treated as production-like.

This batch replaces the earlier idea named:

```text
Batch 64 — Backup / Restore / Rollback Procedure
```

The scope is the same safety workstream, moved earlier and renamed to follow Batch 60A.

## Why this batch is needed

The project now uses real AWS-backed resources for the current scope:

```text
DynamoDB tables for CMS/CRM/catalog data
S3 bucket for uploaded media
EC2 deployment for backend/public/admin demo
Cognito for admin authentication
Git repository for code rollback
```

Before customer launch or production-like usage, the project needs clear recovery steps that avoid accidental data loss and avoid unnecessary AWS cost.

## Backup procedure scope

Document and verify the approach for:

```text
DynamoDB table export/backup
S3 media backup/listing
Reviewed import files preservation
Git source-code rollback
EC2 release/deployment rollback
Nginx config rollback
Environment/config snapshot notes
```

## DynamoDB safety notes

The project must preserve these rules:

```text
Do not delete DynamoDB tables during normal import/update flows.
Do not reset rsa_id_counters downward.
Use dry-run-first import behavior.
Use explicit --execute or equivalent only after review.
Keep launch/demo import files for traceability.
```

Recommended documented procedures:

```text
How to export or snapshot current DynamoDB data.
How to review table item counts before and after import.
How to restore from saved export/review data when practical.
How to avoid overwriting current production-like data accidentally.
```

## S3 media safety notes

Document:

```text
Current bucket name and region.
Approved media path patterns.
How to list S3 media objects by prefix.
How to identify uploaded Product/Brand/Gallery/Contact Person files.
How to preserve S3 media before large backfills/imports.
How to avoid deleting media objects unless explicitly approved.
```

The S3 bucket should remain private. Public display continues through the backend `/api/media/...` route and Nginx proxy path.

## Git rollback procedure

Document:

```text
How to identify the last known-good commit.
How to create a rollback branch.
How to revert a bad commit safely.
How to redeploy the known-good release to EC2.
How to preserve uncommitted local work before rollback.
```

Do not use destructive Git commands in a production-like branch unless the rollback plan explicitly requires and the user approves it.

## EC2 deployment rollback procedure

Document the known project deployment path:

```text
deploy/ec2/deploy_rsa_cms_release_to_ec2.ps1
/opt/rsa-cms/current
rsa-cms-backend systemd service
Nginx public/admin/API/media proxy config
```

Rollback notes should include:

```text
How to redeploy a previous known-good release.
How to restart rsa-cms-backend.
How to test Nginx config.
How to reload/restart Nginx.
How to verify /api/media/ route and client_max_body_size 8m still exist.
How to run a minimum public/admin smoke test after rollback.
```

## Configuration safety checklist

Record current important settings without exposing secrets:

```text
AWS region
DynamoDB repository mode expectation
S3 media mode expectation
S3 bucket name
Cognito user pool/client identifiers, without secrets
Nginx route requirements
EC2 service names
Security group intent
```

Do not commit secrets, passwords, bearer tokens, refresh tokens, Cognito client secrets, AWS access keys, or temporary passwords.

## Cost guardrails

This batch should be documentation/procedure only and should not add paid infrastructure.

Continue avoiding by default:

```text
ALB
NAT Gateway
RDS
Paid WAF rules
Extra always-on EC2 instances
SMS/email notification workflows
Large unoptimized media storage
High-retention/expensive logging
```

## Acceptance criteria

Batch 60B is complete when the repository contains clear docs for:

```text
DynamoDB backup/export/restore approach
S3 media preservation approach
Import rollback approach
Git rollback approach
EC2 deploy rollback approach
Nginx/media route preservation
Post-rollback smoke test checklist
Cost-control reminders
Secret-handling rules
```

## Out of scope

Do not include:

```text
Route 53/domain/CloudFront/HTTPS implementation
Paid backup products unless separately approved
Automated cross-region backup unless separately approved
DynamoDB PITR unless separately approved after cost review
S3 versioning unless separately approved after cost review
Audit logs table implementation
New admin UI features
```

## EC2 cost reminder

Stop the EC2 demo instance after procedure testing if it is not actively needed.
