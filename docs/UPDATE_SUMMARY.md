# RSA CMS / Mini-CRM Documentation Cleanup and Latest Status Update

Update batch: Phase 8 documentation cleanup after Batch 58 local testing and before Batch 59A implementation  
Date: 2026-06-17

## Purpose

This cleaned `docs/` package restores a consistent documentation layout after several recent packages used mixed README locations.

## Folder cleanup decisions

- Main project Markdown files remain directly under `docs/`.
- Phase 8 batch Markdown files are also directly under `docs/` using normal filenames such as `phase8_batch58_image_lazy_loading.md`.
- The nested `docs/Phase 8 README/` folder is removed.
- The nested `docs/phase8/` folder is removed.
- Root-level README `.txt` files are not kept; the Batch 29 text note was converted to `phase8_batch29_documentation_status_update.md`.
- The old single Batch 60 README is replaced by `phase8_batch60_superseded_by_60a_60b.md`; active planning uses Batch 60A and Batch 60B.

## Latest status captured

```text
Batch 56D â€” Promotions Hero Promoted Packages Only â€” Complete / pushed
Batch 57  â€” SEO metadata/page titles â€” Deferred until final domain
Batch 58  â€” Image Lazy Loading â€” Local testing passed
Batch 59A â€” Cognito Groups + Settings > Users â€” Current Active
Batch 59B â€” Admin-only Restricted/Delete Actions â€” Planned
Batch 60A â€” EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass â€” Planned
Batch 60B â€” Backup / Restore / Production Safety Notes â€” Planned
Batch 61  â€” Route 53 + ACM + CloudFront + EC2 origin â€” Deferred until customer/domain approval
```

## Batch 58 local note

Batch 58 testing passed after the local backend was started with S3 media mode and the approved S3 bucket. Local tests that load current DynamoDB media paths should use:

```powershell
$env:RSA_MEDIA_STORAGE_MODE="s3"
$env:RSA_MEDIA_S3_BUCKET="rsa-cms-media-537765358118-ap-southeast-1"
$env:RSA_MEDIA_MAX_UPLOAD_MB="5"
```

## Cost-control reminder

AWS Free-Tier-first remains mandatory. Keep EC2 stopped when not actively deploying/testing. Continue avoiding ALB, NAT Gateway, RDS, paid WAF, multiple always-on EC2 instances, SMS/MFA costs, unnecessary paid notifications, and high-cost logging unless explicitly approved after cost review.

