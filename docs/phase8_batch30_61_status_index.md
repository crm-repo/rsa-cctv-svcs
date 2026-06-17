# Phase 8 Batch 30-61 Documentation Status Index

Last updated: 2026-06-16

## Current completed anchor

```text
Batch 56D — Promotions Hero Promoted Packages Only
Status: Complete and pushed to Git
```

## Deferred / planned demo-readiness path

```text
Batch 57  — SEO Metadata / Page Titles — Deferred until final domain
Batch 58  — Image Lazy Loading — Current Active / Prepared
Batch 59A — Cognito Groups + Settings > Users — Planned
Batch 59B — Admin-only Restricted/Delete Actions — Planned
Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass — Planned
Batch 60B — Backup / Restore / Production Safety Notes — Planned
Batch 61  — Domain / HTTPS / CloudFront / Route 53 — Planned / Deferred until customer domain approval
```

## Important scope mapping from earlier plan

```text
Earlier Batch 62 — Full Public + Admin Regression After Final Data
→ Current Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass

Earlier Batch 64 — Backup / Restore / Rollback Procedure
→ Current Batch 60B — Backup / Restore / Production Safety Notes

Earlier Batch 65 — CloudFront / SSL / Domain Planning
→ Current Batch 61 — Domain / HTTPS / CloudFront / Route 53
```

## Phase 8 README files in this folder

- `README_BATCH55B_ADMIN_CATEGORY_SUBCATEGORY_BRAND_PROTECTION.md`
- `README_BATCH55C_ADMIN_PAGE_OVERALL_POLISH.md`
- `README_BATCH55D_ADMIN_PAGE_FINALIZATION.md`
- `README_BATCH56A_MEDIA_UPLOAD_ENDPOINT.md`
- `README_BATCH56A_S3_MEDIA_STORAGE_SETUP.md`
- `README_BATCH56B_ADMIN_MEDIA_UPLOAD_INTEGRATION.md`
- `README_BATCH56C_PRODUCTS_BRANDS_S3_BACKFILL.md`
- `README_BATCH56D_PROMOTIONS_HERO.md`
- `README_BATCH57_SEO_DEFERRED.md`
- `README_BATCH58_IMAGE_LAZY_LOADING.md`
- `README_BATCH59A_COGNITO_GROUPS_USER_MANAGEMENT_PLANNED.md`
- `README_BATCH59B_ADMIN_ONLY_DELETE_RESTRICTED_ACTIONS_PLANNED.md`
- `README_BATCH60A_EC2_PUBLIC_IP_DEMO_SMOKE_CHECKLIST_PLANNED.md`
- `README_BATCH60B_BACKUP_RESTORE_PRODUCTION_SAFETY_PLANNED.md`
- `README_BATCH61_DOMAIN_HTTPS_CLOUDFRONT_ROUTE53_PLANNED.md`
- `README_FUTURE_DEFERRED_OPTIONAL_BATCHES.md`

## Cost-control reminder

Keep the EC2 demo instance stopped when not actively testing/deploying. Route 53/domain remains the approved paid exception later; avoid ALB, NAT Gateway, RDS, paid WAF, SMS workflows, extra always-on EC2 instances, and unnecessary paid services unless explicitly approved after cost review.
