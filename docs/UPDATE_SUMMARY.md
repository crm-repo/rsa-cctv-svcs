# RSA CMS / Mini-CRM Documentation Update Summary

Update batch: Phase 8 documentation continuation update through Batch 56D, Batch 57 deferral, and Batch 58-60 planning  
Date: 2026-06-16

## Purpose

This package updates the main Markdown project source files that previously reflected the Batch 29 documentation baseline. It incorporates the completed Phase 8 continuation batches, the current/future batch plan, and the latest user-management/authorization decisions.

## Main Documentation Updates

- Updated `feature-status.md` through Batch 56D and added the Batch 58-60 forward plan.
- Updated `architecture.md` with current EC2/Cognito/DynamoDB/S3/Nginx/media architecture.
- Updated `requirements.md` with promoted package hero rules, media upload/display requirements, Cognito Groups requirements, and non-delete lead requirements.
- Updated `implementation-guidelines.md` with project-structure patch delivery rules, runtime-proof-before-patch guardrails, local DynamoDB/S3/proxy expectations, and role/delete rules.
- Updated `decision-log.md` with ADR-043 through ADR-056.
- Updated `open-issues.md` to resolve post-Batch-29 completed items and keep the remaining deferred/planned items clear.
- Added batch-level docs under `docs/phase8/` for 55B-60 planning/status.

## Current Completed Anchor

```text
Batch 56D — Promotions Hero Promoted Packages Only
Status: Complete and pushed to Git
```

## Deferred Batch

```text
Batch 57 — SEO Metadata / Page Titles
Status: Deferred until Route 53/final domain is ready
Reason: Avoid duplicate canonical/Open Graph/sitemap/robots work and avoid using EC2 public IP as canonical URL.
```

## Current / Planned Next Batches

```text
Batch 58  — Image Optimization / Lazy Loading — Current Active / Prepared
Batch 59A — Cognito Groups + Settings Users Management — Planned
Batch 59B — Admin-only Delete / Restricted Actions — Planned
Batch 60  — Backup / Restore / Production Safety Notes — Planned
```

## Key New Decisions Captured

- Use Cognito Groups (`Admin`, `Standard`) for admin authorization.
- Do not use Cognito `profile` attribute as a role field.
- Do not add a DynamoDB users table for launch user management.
- Settings > Users is Admin-only and goes through FastAPI backend routes to Cognito.
- Standard users should not see Settings and backend must return 403 for restricted routes.
- Delete controls are Admin-only only for approved records.
- Leads (`bookings`, `inquiries`, customer/lead records) are non-delete for both Admin and Standard users.
- Batch 57 SEO/canonical/sitemap/robots work is deferred until final domain.
- Future patch zips should use project structure and avoid root-level batch folders.

## Cost-Control Reminder

AWS Free-Tier-first remains mandatory. Keep EC2 stopped when not actively deploying/testing. Continue avoiding ALB, NAT Gateway, RDS, multiple always-on EC2 instances, SMS/MFA costs, and unnecessary paid services unless explicitly approved after cost review.
