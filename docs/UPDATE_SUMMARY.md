# RSA CMS / Mini-CRM Documentation Cleanup and Latest Status Update

Update batch: Phase 8 Batch 60B backup/restore/production safety notes  
Date: 2026-06-26

## Purpose

This package completes Batch 60B by adding the backup/restore/production safety runbook and updating the source-of-truth Markdown documentation before the final EC2 public-IP demo readiness pass.

## Latest status captured

```text
Batch 56D — Promotions Hero Promoted Packages Only — Complete / pushed
Batch 57  — SEO metadata/page titles — Deferred until final domain
Batch 58  — Image Lazy Loading — Complete / local testing passed
Batch 59A — Cognito Groups + Settings > Users — Complete / local testing passed for current scope
Batch 59B — Admin-only Restricted/Delete Actions — Planned / confirm before demo
Batch 60C — Public/Admin Polish — Complete for now / accepted scope
Batch 60B — Backup / Restore / Production Safety Notes — Complete / documentation-procedure only
Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass — Planned / next final demo gate
Batch 61  — Route 53 + ACM + CloudFront + EC2 origin — Deferred until customer/domain approval
```

## Batch 60B deliverable

```text
docs/phase8_batch60b_backup_restore_safety.md
```

The runbook covers:

- DynamoDB backup/export/restore approach.
- `rsa_id_counters` safety and no-downward-reset rule.
- S3 media backup/preservation/restore procedure.
- Git rollback rules.
- EC2 release rollback using `/opt/rsa-cms/releases` and `/opt/rsa-cms/current`.
- Nginx config backup/rollback, including `/api/media/` and `client_max_body_size 8m` preservation.
- Import rollback, dry-run-first, no table deletion, and no unapproved overwrite rules.
- Secret/token/password handling rules.
- EC2 and AWS Free-Tier-first cost-safety reminders.
- Batch 60A handoff checklist.

## Batch 60B safety decision

Batch 60B is documentation/procedure only. It does not add paid backup services, DynamoDB PITR, AWS Backup plans, new infrastructure, or automation scripts unless separately approved after cost review.

## Next recommended order

```text
1. Confirm/run Batch 59B if not already completed
2. Batch 60A — Final EC2 public-IP demo readiness pass
3. Post-demo/domain-dependent work: Batch 57, Batch 61, Batch 62
```

## Files updated in this package

```text
docs/feature-status.md
docs/open-issues.md
docs/decision-log.md
docs/architecture.md
docs/project-overview.md
docs/implementation-guidelines.md
docs/requirements.md
docs/UPDATE_SUMMARY.md
docs/phase8_batch60b_backup_restore_safety.md
docs/phase8_batch60c_docs_status_checkpoint.md
```
