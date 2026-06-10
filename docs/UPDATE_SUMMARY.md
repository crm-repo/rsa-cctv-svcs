# RSA CMS / Mini-CRM Documentation Update Summary

## Update Purpose

This package updates the primary Markdown project source files to record the approved Phase 8 Final v5 DynamoDB/API implementation plan.

## Main Updates Added

- Added `PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md` as the clean approved implementation plan.
- Updated architecture source with the v5 approved table set, GSI set, product/package rules, Contact Us consolidation, and API mapping summary.
- Updated requirements source with approved backend/CMS requirements for products, packages, categories, key features, Contact Us, and page APIs.
- Updated decision log with new ADRs for Phase 8 v5, package products, Contact Us consolidation, product schema/naming, and category/product GSI decisions.
- Updated feature status to show current local backend skeleton progress and next Phase 8 implementation tasks.
- Updated open issues to mark DynamoDB access-pattern review as resolved and record v5-resolved items.
- Updated implementation guidelines with Phase 8 v5 coding guardrails.
- Updated project overview with the approved backend/data direction.

## Approved Phase 8 v5 Summary

```text
Launch tables: 12
Launch GSIs: 5
Simplified minimum count: 17 RCU + 17 WCU
Table prefix: rsa_
Design style: simple multi-table DynamoDB
```

Approved launch tables:

```text
rsa_products
rsa_brands
rsa_categories
rsa_key_features
rsa_customers
rsa_bookings
rsa_inquiries
rsa_about
rsa_project_gallery
rsa_services
rsa_contact_us
rsa_id_counters
```

Approved launch GSIs:

```text
rsa_products:
- category_key-display_seq-index
- product_brand_key-display_seq-index

rsa_customers:
- contact_number_normalized-index

rsa_bookings:
- status-created_at-index

rsa_inquiries:
- status-created_at-index
```

## Markdown Files Updated

- PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md
- PRIMARY_architecture.md
- PRIMARY_requirements.md
- PRIMARY_decision-log.md
- PRIMARY_feature-status.md
- PRIMARY_open-issues.md
- PRIMARY_implementation-guidelines.md
- PRIMARY_project-overview.md
- UPDATE_SUMMARY.md

## Notes

The PDF handbook was not regenerated in this package. Regenerate the PDF from the Markdown source files later if a refreshed reference PDF is needed.
