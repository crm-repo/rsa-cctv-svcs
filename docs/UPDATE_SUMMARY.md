# RSA CMS / Mini-CRM Documentation Cleanup and Latest Status Update

Update batch: Phase 8 Batch 60C documentation checkpoint before Batch 60B  
Date: 2026-06-26

## Purpose

This package updates the source-of-truth Markdown docs after the inserted Batch 60C public/admin polish work and before starting Batch 60B backup/restore/safety notes.

## Latest status captured

```text
Batch 56D — Promotions Hero Promoted Packages Only — Complete / pushed
Batch 57  — SEO metadata/page titles — Deferred until final domain
Batch 58  — Image Lazy Loading — Complete / local testing passed
Batch 59A — Cognito Groups + Settings > Users — Complete / local testing passed for current scope
Batch 59B — Admin-only Restricted/Delete Actions — Planned / confirm before demo
Batch 60C — Public/Admin Polish — Complete for now / accepted scope
Batch 60B — Backup / Restore / Production Safety Notes — Planned / next
Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass — Planned / final demo gate
Batch 61  — Route 53 + ACM + CloudFront + EC2 origin — Deferred until customer/domain approval
```

## Batch 60C notes

- Batch 60C was inserted after the original before-demo sequence for public/admin polish.
- Public/admin polish is accepted as complete for now by user decision.
- The existing `show_pack_flag` field is now category-scoped:
  - Packages/Kits: admin label is `Promote Package` and the field controls package/recommended/promo placement.
  - Non-package products: admin label is `Featured Product` and the field controls homepage Featured Products inclusion.
- Homepage Featured Products now filters non-package products with `show_flag=Y` and `show_pack_flag=Y`.
- Existing total limit, carousel per-page behavior, sort behavior, and empty-state behavior are retained.
- The risky inline `products.html` scripts from early 60C-4A/4B attempts were superseded by a safer `admin-catalog.js` approach.
- EC2 deploy verification for the final safe 60C admin behavior was interrupted by EC2 environment/tooling checks in the pasted output; Batch 60A should confirm the current active release and smoke 60C behavior before demo.

## Next recommended order

```text
1. Batch 60B — Backup / Restore / Production Safety Notes
2. Confirm/run Batch 59B if not already completed
3. Batch 60A — Final EC2 public-IP demo readiness pass
4. Post-demo/domain-dependent work: Batch 57, Batch 61, Batch 62
```

## Files updated in this package

```text
docs/feature-status.md
docs/open-issues.md
docs/decision-log.md
docs/architecture.md
docs/project-overview.md
docs/implementation-guidelines.md
docs/UPDATE_SUMMARY.md
docs/phase8_batch60c_docs_status_checkpoint.md
```
