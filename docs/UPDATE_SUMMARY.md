# RSA CMS / Mini-CRM Documentation Cleanup and Latest Status Update

Update batch: Phase 8 Batch 62A release artifact / GitHub decoupling planning update  
Date: 2026-06-26

## Purpose

This package updates the project documentation to formally add **Batch 62A — Release Artifact / GitHub Decoupling Safety** to the post-demo / pre-launch pipeline.

GitHub remains the source-control system, but the production runtime should not depend on GitHub downloads, raw GitHub URLs, moving branches, or GitHub credentials. Production go-live should use a tagged release artifact and preserve EC2 release-folder rollback.

## Latest status captured

```text
Batch 56D — Promotions Hero Promoted Packages Only — Complete / pushed
Batch 57  — SEO metadata/page titles — Deferred until final domain
Batch 58  — Image Lazy Loading — Complete / local testing passed
Batch 59A — Cognito Groups + Settings > Users — Complete / local testing passed for current scope
Batch 59B — Admin-only Restricted/Delete Actions — Complete / user-confirmed
Batch 60C — Public/Admin Polish — Complete / Git-pushed, EC2-deployed, browser-tested by user
Batch 60B — Backup / Restore / Production Safety Notes — Complete / documentation-procedure only
Batch 60A — EC2 Public-IP Demo Readiness — Complete / demo-ready accepted by user
Batch 62A — Release Artifact / GitHub Decoupling Safety — Deferred / post-demo pre-launch
Batch 61  — Route 53 + ACM + CloudFront + EC2 origin — Deferred until customer/domain approval
Batch 62  — Final launch/cutover checklist — Deferred / later
```

## Batch 62A deliverable added

```text
docs/phase8_batch62a_release_artifact_github_decoupling.md
```

The new runbook covers:

- Why GitHub should not be a runtime dependency.
- Tagged release and artifact packaging guidance.
- Release artifact checksum guidance.
- Private S3 or controlled local/offline artifact storage.
- Manual/S3 release deployment model.
- Runtime checks for GitHub URLs and GitHub tokens.
- Secret exclusion rules for artifacts.
- EC2 rollback using `/opt/rsa-cms/releases/*` and `/opt/rsa-cms/current`.
- Batch 62A acceptance checklist.

## Updated post-demo pipeline

```text
1. Targeted demo feedback/hotfixes, if any
2. Batch 62A — Release Artifact / GitHub Decoupling Safety
3. Batch 57 — SEO metadata/page titles/canonical/Open Graph/sitemap/robots after final domain is known
4. Batch 61 — Route 53 + ACM + CloudFront + EC2 Nginx origin
5. Batch 62 — Final launch/cutover checklist
```

## Files updated in this package

```text
docs/feature-status.md
docs/project-overview.md
docs/open-issues.md
docs/implementation-guidelines.md
docs/architecture.md
docs/decision-log.md
docs/requirements.md
docs/UPDATE_SUMMARY.md
docs/phase8_batch62a_release_artifact_github_decoupling.md
docs/phase8_batch60a_demo_readiness_acceptance.md
docs/phase8_batch60b_backup_restore_safety.md
docs/phase8_batch60c_docs_status_checkpoint.md
```

## Cost-safety reminder

Batch 62A is documentation/planning only for now. It must not add paid CI/CD, ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, or paid deployment tooling unless separately approved after cost review. EC2 should remain stopped when not actively preparing, testing, deploying, or demoing.
