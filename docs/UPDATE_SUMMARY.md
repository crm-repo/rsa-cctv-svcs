# RSA CMS / Mini-CRM Documentation Status Update

Update batch: Phase 8 Batch 60C integration recovery and Batches 60E-60G admin polish  
Date: 2026-07-22

## Purpose

This package updates the authoritative project documentation after the local recovery of the previously separate Batch 60C branch and completion of the next targeted admin polish batches.

## Latest status captured

```text
Batch 60C   — Public/Admin Polish — Complete previously; recovered into current local main and locally regression-tested
Batch 60E   — Admin Contact Us Split Tables — Complete / local browser-tested
Batch 60F   — Initial Dashboard Quick Actions One-Row Patch — Superseded by 60F-1
Batch 60F-1 — Dashboard Quick Actions Row Fix — Complete / local browser-tested
Batch 60G   — Login Status Error-Only Polish — Complete / local browser-tested
Git/EC2 sync of consolidated current local version — Pending confirmation
Batch 57    — SEO metadata/page titles — Deferred until final domain
Batch 61    — Route 53 + ACM + CloudFront + HTTPS — Deferred until domain approval
Batch 62A   — Release Artifact / GitHub Decoupling Safety — Deferred / pre-launch
Batch 62    — Final launch/cutover checklist — Deferred / later
```

## Completed behavior documented

### Batch 60C integration recovery

- Recovered the accepted Batch 60C branch changes into the current local `main` baseline.
- Preserved newer database-driven public phone/email headers, Promotions mobile hero rotation, Admin Sale Products sorting, Services CTA cleanup, and friendly login error handling.
- Local JavaScript syntax checks and browser checks passed during integration.

### Batch 60E — Contact Us admin split tables

- Replaced the single combined Contact Us list with three admin tables:
  - Company Contact
  - Contact Persons
  - Social Media
- Removed non-applicable display columns instead of showing repeated `---` values.
- Preserved one consolidated `rsa_contact_us` table, existing APIs, public rendering, search/sort/refresh/add/view-edit workflows, and conditional drawer forms.

### Batch 60F-1 — Dashboard Quick Actions

- Shows Add Product, Add Category, and Add Brand as three equal desktop buttons on one row.
- Adds boxed `+` indicators to emphasize create/add actions.
- Keeps one-column mobile stacking.
- Supersedes the initial Batch 60F selector scope that allowed an older odd-item grid rule to remain active.

### Batch 60G — Login status presentation

- Keeps the emphasized status area hidden during normal page load, progress, and successful redirect.
- Shows the emphasized area only for real authentication/configuration errors.
- Keeps normal email/password guidance in the information note and increases that note to `16px`.
- Preserves friendly non-technical login error wording and accessible alert/live-region behavior.

## Immediate next operational step

The current consolidated local `main` version should be:

1. committed and pushed to GitHub;
2. deployed through the existing `deploy/ec2/deploy_rsa_cms_release_to_ec2.ps1` release-folder flow;
3. smoke-tested for API health, login, dashboard Quick Actions, Contact Us split tables, and recovered Batch 60C behavior;
4. followed by stopping EC2 unless testing/demo continues.

## Files updated in this package

```text
docs/feature-status.md
docs/project-overview.md
docs/open-issues.md
docs/decision-log.md
docs/requirements.md
docs/architecture.md
docs/implementation-guidelines.md
docs/UPDATE_SUMMARY.md
docs/phase8_batch60e_60g_admin_polish_checkpoint.md
```

## Cost-safety reminder

These completed polish changes do not add DynamoDB tables, GSIs, backend routes, S3 buckets, Cognito resources, or paid infrastructure. Preserve the single-instance AWS Free-Tier-first deployment and keep EC2 stopped when not actively deploying, testing, or demoing.
