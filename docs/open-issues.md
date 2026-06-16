# RSA CMS / Mini-CRM Open Issues

## Authority

This document tracks risks, unresolved questions, blockers, technical debt, and dependencies. Implementation status is controlled by [feature-status.md](./feature-status.md).

Last updated: 2026-06-11  
Update scope: Phase 8 Batch 29 documentation/status update.


## Current Open / Deferred Items After Batch 56D

| Item | Status | Notes |
|---|---|---|
| Batch 58 image lazy loading | Current Active / Prepared | Frontend-only browser loading hints; no image compression or S3 path changes. |
| Batch 59A Cognito Groups + Users | Planned | Settings > Users backed by Cognito admin APIs through FastAPI only. |
| Batch 59B Admin-only restricted/delete actions | Planned | Standard users hidden/blocked; leads remain non-delete. |
| Batch 60A EC2 public-IP demo readiness pass | Planned | Final EC2 smoke regression and demo data sanity check after Batch 58/59A/59B. |
| Batch 60B backup/restore/safety notes | Planned | Operational runbooks for DynamoDB/S3/Git/EC2/Nginx rollback safety. |
| Batch 61 domain/HTTPS/CloudFront/Route 53 | Deferred | Planned after customer demo/launch approval and final domain confirmation. |
| SEO metadata/page titles | Deferred | Defer until Route 53/final domain. |
| Canonical URLs/Open Graph URLs | Deferred | Do not use EC2 IP as canonical. |
| sitemap.xml/robots.txt | Deferred | Defer until final domain and launch URL. |
| Route 53/domain/SSL/CloudFront | Deferred | Batch 61 after final domain decision; approved direction is Route 53 + ACM + CloudFront + EC2 origin. |
| Admin audit logs | Optional future | Not required for launch; may be added for traceability later. |
| Email/SMS notifications | Optional future | Disabled by default for cost control. |
| Analytics dashboard | Optional future | Future enhancement only. |

## Resolved After Batch 29

| Item | Resolution |
|---|---|
| EC2 public-IP deployment | Completed for demo path in Batches 34-39. |
| Cognito admin protection | Completed for admin/login/API deployment path in Batches 40-48. |
| Public catalog/CMS API rendering | Completed through Batches 49/49B/50. |
| Static data extraction/import | Completed in Batches 54A/54B. |
| Package quotation optional price | Completed in Batch 54C. |
| Admin media path interim behavior | Completed in Batch 55A. |
| Category/subcategory/brand protection polish | Completed in Batch 55B. |
| Admin page polish/finalization | Completed in Batches 55C/55D. |
| S3 media upload/storage | Completed for current scope in Batches 56A/56B. |
| Products/Brands S3 backfill | Completed in Batch 56C. |
| Promotions hero promoted package filtering | Completed in Batch 56D. |

## Known Issues

| Issue | Severity | Impact | Status | Notes |
|---|---|---|---|---|
| Public/external deployment not completed | High | High | Open | EC2/IP-based deployment is the next major phase |
| AWS billing alerts not configured | High | High | Open | Must be configured before public/external AWS testing |
| Free-Tier deployment review pending | High | High | Open | Must verify no ALB, NAT Gateway, RDS, SMS/MFA cost drift, extra always-on instances, or unnecessary paid services |
| Real Cognito enforcement not enabled | High | High | Open | Auth prep exists, but local admin auth remains disabled by default until deployment/security phase |
| Real S3 binary upload/storage not enabled | Medium | Medium | Open | Admin media fields prepare/resolve paths/keys; actual upload/storage is later |
| SEO metadata incomplete | High | Medium | Open | Required before production launch |
| sitemap.xml and robots.txt missing/incomplete | High | Medium | Open | Required before production launch |
| Image optimization pending | Medium | High | Open | Needed for production/mobile performance |
| Production content import not completed | Medium | High | Open | Excel/CSV templates and import loader exist; final company data still needed |
| Product/promotions legacy static markup | Medium | Medium | Partially reduced | API integration exists; final cleanup depends on production data migration and launch readiness |
| GitHub Pages/backend split | Medium | Medium | Open | Public static site can run separately; backend/admin production hosting still needs deployment plan |

## Resolved / Completed Implementation Items

| Item | Status | Notes |
|---|---|---|
| Backend not implemented | Resolved | FastAPI backend and public/admin routes completed for Phase 8 |
| Admin panel not implemented | Resolved | Dashboard, lead management, catalog management, and CMS management completed for Phase 8 |
| Booking form not implemented | Resolved | Public booking form API integration completed |
| Inquiry/contact form not implemented | Resolved | Public inquiry form API integration completed |
| DynamoDB access pattern review | Resolved | Phase 8 Final v5 plan approved and implemented |
| DynamoDB resources not created | Resolved | 12 approved tables created and verified ACTIVE in AWS `ap-southeast-1` |
| Admin catalog CRUD missing | Resolved | Create/update workflows completed |
| Admin CMS CRUD missing | Resolved | Create/update workflows completed |
| Admin UI polish pending | Resolved | Batch 27 final admin UI polish completed |
| Launch data templates missing | Resolved | Excel/CSV templates completed |
| Launch data import loader missing | Resolved | Safe dry-run-first import loader completed |
| Full public/admin regression pending | Resolved | Batch 28 checklist/script passed |

## Technical Debt

| Item | Severity | Status | Notes |
|---|---|---|---|
| Delete/archive workflows absent | Medium | Deferred | Intentionally excluded from Phase 8 to avoid destructive behavior |
| Admin audit logs absent | Medium | Deferred | Future enhancement after launch/security baseline |
| Full role/permission matrix absent | Medium | Deferred | Cognito prep exists; fine-grained role control is future work |
| `rsa_product_types` absent | Low | Deferred | Subcategory remains manual at launch |
| Real image optimization pipeline absent | Medium | Open | Needed before production media rollout |
| Production backup/restore procedure absent | Medium | Open | Needed before real launch data is treated as production |
| Import overwrite behavior not finalized | Low | Open | Current safe behavior should skip existing by default unless explicit overwrite is approved later |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| AWS cost drift during deployment | High | Configure billing alerts; preserve Free-Tier-first design; avoid paid components |
| Admin exposed without Cognito enforcement | High | Do not publicly expose admin until Cognito JWT validation is enabled |
| Accidental DynamoDB writes from local testing | Medium | Keep mock mode default; require explicit DynamoDB mode and `--execute` for imports |
| Production data quality issues | Medium | Use templates, validation, dry-run import, and manual review |
| Image/media path inconsistency | Medium | Use shared admin media prep workflow and agreed media-key naming |
| SEO launch delay | Medium | Complete SEO/sitemap/robots after deployment planning |

## Blockers

| Blocker | Status | Notes |
|---|---|---|
| Billing alert setup | Open | Required before public/external AWS testing |
| EC2/IP-based deployment plan | Open | Required before live backend/admin demo |
| Cognito enforcement | Open | Required before external/public admin testing |
| S3 upload/storage enablement | Open | Required before real admin image upload |
| Final company launch data | Open | Needed before production demo/launch |
| SEO/sitemap/robots/image optimization | Open | Needed before production launch |

## Outstanding Decisions

| Decision | Status | Options / Notes |
|---|---|---|
| Production deployment cutover sequence | Open | EC2 public IP first, Route 53/domain later |
| S3 bucket naming and CloudFront path strategy | Open | Keep Free-Tier-first and simple |
| Cognito admin user setup | Open | Avoid SMS/MFA costs; email/password only unless explicitly changed |
| Production import overwrite behavior | Open | Keep skip-existing default unless an explicit overwrite process is approved |
| Whether product prices can be hidden as “Contact for Price” | Open | Current data supports price/sale_price; business may decide later |
| Whether assigned contact persons should be selectable from Contact Us records | Open | Current assigned person can be free text |
| Package banner click behavior | Deferred | Data source approved as products with `show_pack_flag`; UI behavior can be adjusted later |

## Dependencies

| Dependency | Required For |
|---|---|
| AWS billing alert configuration | Public/external testing |
| Free-Tier deployment review | Public/external testing |
| EC2 deployment | Backend/admin demo outside localhost |
| Cognito user pool/client/JWT enforcement | Public/external admin security |
| S3 bucket/storage policy | Real admin image uploads |
| Final product/content/image data | Production demo/launch |
| SEO metadata | Production launch |
| sitemap.xml / robots.txt | Production launch |
| Image optimization | Production/mobile performance |
| SSL/domain setup | Domain launch after IP-based testing/demo |

## Resolved Cost-Control Decisions

| Decision | Resolution | Notes |
|---|---|---|
| Booking request notifications | Disabled by default for launch | Requests only need to appear in the admin panel |
| Inquiry notifications | Disabled by default for launch | Inquiries only need to appear in the admin panel |
| Cognito SMS features | Disable where possible | Avoid SMS MFA and phone verification unless explicitly approved |
| Route 53/domain timing | Defer until after IP-based testing/demo | Route 53/domain is the expected paid exception |

## Resolved by Phase 8 Final v5

| Item | Resolution |
|---|---|
| DynamoDB table prefix | Use `rsa_` |
| DynamoDB design style | Use simple multi-table design |
| Launch table count | 12 tables |
| Launch GSI count | 5 GSIs |
| Package banner storage | No separate table; source package display from `rsa_products` |
| Package visibility | `show_flag` for normal public visibility; `show_pack_flag` for package hero/promo placement only |
| Product ordering field | Use `display_seq` |
| Product sale fields | No `old_price`; sale is determined by `sale_price` |
| Product ID generation | Category-based four-letter prefix with `rsa_id_counters` |
| Product category icons | Add `icon_code` to `rsa_categories` |
| Product features | Use `feature_01` through `feature_10`, minimum 3, plus `rsa_key_features` |
| Product name default | Default from `product_brand_name + feature_01 + subcategory`, editable before save |
| Product description | Manually managed; not auto-generated from product-name defaulting |
| Contact Us tables | Consolidate into `rsa_contact_us` with `contact_type` |
| Customer email GSI | Do not create at launch; store normalized email only |
| Product GSIs | Add category and brand product GSIs at launch |
| Product types | `rsa_product_types` deferred and not for launch |
