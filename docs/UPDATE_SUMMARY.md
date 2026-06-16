# RSA CMS / Mini-CRM Documentation Update Summary

Update batch: Phase 8 documentation clarification for Batch 59A, Batch 60A/60B, and Batch 61  
Date: 2026-06-16

## Purpose

This package updates the main Markdown project source files and Phase 8 README files after the detailed planning decisions made after the previous Batch 30-60 documentation package.

It keeps the Batch 56D completion anchor, Batch 57 deferral, and Batch 58 current/prepared status, then adds the finalized planned behavior for:

```text
Batch 59A — Cognito Groups + Settings > Users
Batch 59B — Admin-only Restricted/Delete Actions
Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass
Batch 60B — Backup / Restore / Production Safety Notes
Batch 61  — Domain / HTTPS / CloudFront / Route 53 Planning
```

## Main Documentation Updates

- Updated `feature-status.md` with Batch 60A/60B split and Batch 61 planned/deferred domain path.
- Updated `requirements.md` with detailed Batch 59A onboarding/user-field requirements, Batch 60A demo-readiness requirements, Batch 60B safety requirements, and Batch 61 domain/HTTPS requirements.
- Updated `implementation-guidelines.md` with user-management guardrails, demo readiness/safety batch split, and domain/CloudFront planning guardrails.
- Updated `decision-log.md` with ADR-057 through ADR-060.
- Updated `project-overview.md`, `architecture.md`, and `open-issues.md` to reflect the finalized near-term/demo-ready plan.
- Added/updated Phase 8 README files for Batch 59A, Batch 60A, Batch 60B, and Batch 61.

## Current Completed Anchor

```text
Batch 56D — Promotions Hero Promoted Packages Only
Status: Complete and pushed to Git
```

## Current / Planned Demo-Ready Path

```text
Batch 58  — Image Lazy Loading — Current Active / Prepared
Batch 59A — Cognito Groups + Settings > Users — Planned
Batch 59B — Admin-only Restricted/Delete Actions — Planned
Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass — Planned
Batch 60B — Backup / Restore / Production Safety Notes — Planned
Batch 61  — Domain / HTTPS / CloudFront / Route 53 — Planned / Deferred until customer domain approval
```

## Key New Decisions Captured

- Batch 59A uses Cognito Groups: `Admin` and `Standard`.
- Do not use Cognito `profile` for roles and do not add a DynamoDB users table for launch.
- Use Option A onboarding: suppress Cognito invitation email and show backend-generated temporary password once after create/reset.
- Temporary passwords are not stored, logged, or re-viewable. If lost, Admin resets/generates a new temporary password.
- First-login password change must happen in the browser, not command line.
- Create and view/edit user modal use First Name and Last Name.
- Main Users table shows generated Full Name.
- Batch 60A replaces the earlier Batch 62 regression concept for demo readiness.
- Batch 60B replaces the earlier Batch 64 backup/restore/rollback concept.
- Batch 61 replaces the earlier Batch 65 domain/SSL/CloudFront concept.
- Batch 61 approved direction is Route 53 + ACM + CloudFront + EC2 Nginx origin.
- Route 53/domain cost plan is approved: roughly USD 20-25/year for normal `.com` domain registration/renewal plus hosted zone planning, with tiny DNS query charges expected for small traffic.
- SEO canonical/Open Graph/sitemap/robots remain deferred until final domain confirmation.

## Cost-Control Reminder

AWS Free-Tier-first remains mandatory. Keep EC2 stopped when not actively deploying/testing. Continue avoiding ALB, NAT Gateway, RDS, paid WAF, multiple always-on EC2 instances, SMS/MFA costs, unnecessary paid notifications, and high-cost logging unless explicitly approved after cost review.
