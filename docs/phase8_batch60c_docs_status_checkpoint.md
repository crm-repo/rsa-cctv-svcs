# Phase 8 Batch 60C Documentation Status Checkpoint

Date: 2026-06-26

## Purpose

This checkpoint records the accepted Batch 60C status before starting Batch 60B backup/restore/production safety notes.

## Batch 60C status

Batch 60C is marked **Complete for now / accepted scope** by user decision.

### Completed or accepted areas

- Public/admin UI polish from the Batch 60C sequence is accepted for the current demo scope.
- Login/sidebar/logo polish is accepted and should not be reopened unless explicitly requested.
- Homepage Featured Products criteria was updated to use the existing `show_pack_flag` field for non-package products.
- The existing display limit, carousel per-page behavior, ordering behavior, and empty-state behavior are retained.
- Admin Products uses the same stored field with category-scoped labeling:
  - Packages/Kits: `Promote Package`.
  - Non-package products: `Featured Product`.
- Early risky inline scripts in `products.html` were removed/superseded by safer `admin-catalog.js` logic.

## `show_pack_flag` rule after Batch 60C

```text
Package/Kits products:
  show_pack_flag = Y means Promote Package.
  Used for recommended/package/promo placement.

Non-package products:
  show_pack_flag = Y means Featured Product.
  Used for the homepage Featured Products card.
```

Homepage Featured Products filter:

```text
show_flag = Y
category_key != packages
show_pack_flag = Y
```

No new DynamoDB product field is added.

## EC2 status note

The last pasted EC2 deploy output for the final safe 60C admin behavior verified the downloaded source files and confirmed the old risky/old package-only logic was absent, but the deploy stopped before release switch due to EC2 environment/tooling checks. Batch 60A must confirm the current EC2 active release and smoke-test the accepted Batch 60C behavior before declaring the public-IP demo ready.

## Next batch

Batch 60B should proceed next and should document:

- DynamoDB backup/export/restore procedure.
- S3 media backup/preservation procedure.
- Git commit/branch rollback rules.
- EC2 release rollback using `/opt/rsa-cms/releases` and `/opt/rsa-cms/current`.
- Nginx config backup/rollback.
- Import safety and dry-run-first rules.
- Secret/token/password handling rules.
- EC2 cost-safety reminders.
