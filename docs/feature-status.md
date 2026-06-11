# RSA CMS / Mini-CRM Feature Status

## Authority

This document is the authoritative implementation progress tracker. If status here conflicts with another document, this document controls implementation status.

Last updated: 2026-06-11  
Update scope: Phase 8 Batch 29 documentation/status update after full public/admin regression.

## Status Legend

| Status | Meaning |
|---|---|
| Complete | Complete for the current project phase |
| Established | Working foundation exists and should be reused |
| Current Active | The active work area |
| Planned | Approved but not implemented |
| Deferred | Approved but intentionally postponed |
| Open if Reopened | Not active now; only revisit if explicitly requested |
| Superseded | Older approach replaced by a newer approved decision |

## Current Implementation Status

| Feature | Status | Priority | Notes |
|---|---|---:|---|
| Homepage | Complete | High | Complete for current phase; do not reopen unless requested |
| Homepage Hero | Complete | High | Static/frontend layout implemented |
| Recommended Packages | Complete | High | Package cards are now backed by the approved product/package API path when using backend data |
| Featured Products Preview | Complete | High | Public API connection completed in Phase 8 |
| Products on Sale Preview | Complete | High | Uses sale products; sale is determined by `sale_price` |
| Homepage Top Brands | Complete | Medium | Public API connection completed in Phase 8 |
| Homepage Services Preview | Complete | High | Public API connection completed in Phase 8 |
| Products Page | Complete | High | Public page connected to backend API; existing catalog behavior preserved |
| Product Category Filters | Complete | High | API-backed category filtering supported |
| Products Brand Strip | Complete | High | API-backed brand filtering supported |
| Product Search | Complete | High | Search behavior preserved through frontend/API integration |
| Product Sorting | Complete | High | Sorting behavior preserved |
| Product Pagination | Complete | High | Paging behavior preserved |
| Product Quick View Modal | Complete | High | Existing public interaction preserved |
| Promotions Page | Complete | High | Complete for current phase |
| Promotions Sale Filter | Complete | High | Sale remains active and cannot be removed |
| Promotions All Products Behavior | Complete | High | Clears category while keeping Sale active |
| Brands Page | Complete | High | Complete for current phase; do not reopen unless requested |
| Brands Hero | Complete | High | Hero text, features, and logo grid direction established |
| Brands Brand Strip | Complete | High | One-row/two-row behavior resolved |
| About Us Page | Complete | High | Public page is complete for current phase and API-backed CMS content is supported |
| Services Page | Complete | Medium | Public page is complete for current phase and API-backed CMS content is supported |
| Contact Us Page | Complete | High | Public page is complete for current phase and inquiry API integration is supported |
| Booking Page | Complete | High | Public booking form API integration completed |
| Booking Form Validation / Submit | Complete | High | Public form posts to backend booking API |
| Inquiry CTA / Contact Inquiry Flow | Complete | High | Contact/inquiry form posts to backend inquiry API |
| Admin Panel Shell | Complete | High | Admin dashboard shell and page navigation implemented |
| Admin Dashboard | Complete | Medium | Dashboard shell and admin landing page implemented |
| Admin Lead Management | Complete | High | Bookings, inquiries, customers pages implemented with list/detail/update workflows |
| Product Management Admin | Complete | High | Create/update, filters, detail drawer, media field prep, product-name preview, feature suggestions |
| Category Management Admin | Complete | High | Create/update and display-sequence/show-flag management implemented |
| Brand Management Admin | Complete | High | Create/update and logo/media field prep implemented |
| Key Feature Management Admin | Complete | Medium | Create/update and reusable suggestions supported |
| CMS Management Admin | Complete | High | About, project gallery, services, and contact-us admin pages/actions implemented |
| Contact Person Photo Prep | Complete | Medium | Contact Person image/profile photo field uses the media prep workflow; Company Contact and Social Media do not add photo upload fields |
| Customer CRM | Complete for Phase 8 | High | Customers auto-created/linked from bookings and inquiries; admin customer list/detail available |
| User Roles / Permissions | Deferred | Medium | Full roles/permissions remain future work; Cognito prep exists |
| Audit Logs | Deferred | Medium | Future admin audit trail |
| Backend FastAPI | Complete | High | Local FastAPI backend, route modules, config, CORS, health endpoint, Swagger docs |
| Repository Layer | Complete | High | Mock/DynamoDB repository mode switch implemented; mock remains safe default |
| DynamoDB Integration | Complete | High | Approved 12 tables created in AWS `ap-southeast-1`; DynamoDB mode tested successfully |
| DynamoDB Seed Data | Complete | High | JSON seed data and safe seed loader implemented; null cleanup applied |
| DynamoDB Regression Tests | Complete | High | Public/admin DynamoDB regression tests passed |
| Cognito Auth Prep | Complete | High | Local admin auth prep and login shell implemented; real Cognito protection still deferred until deployment/security step |
| S3 / Image Upload Prep | Complete | Medium | Admin media upload controls prepared; binary upload/storage remains a later S3 enablement step |
| Excel/CSV Launch Data Templates | Complete | Medium | Company-friendly launch data templates created and validated |
| Launch Data Import Loader | Complete | Medium | Safe dry-run-first CSV/Excel import loader implemented; writes only with `--execute` |
| Full Public/Admin Regression | Complete | High | Batch 28 regression script/checklist passed in current testing |
| CloudFront / SSL | Planned | High | Required for production/domain launch |
| AWS EC2 Deployment | Planned | High | Required before external demo/public testing |
| Route 53 / Domain | Planned | Medium | Delayed until after EC2 public-IP testing/demo |
| AWS Billing Alerts | Planned | High | Required before public/external AWS testing |
| Free-Tier Deployment Review | Planned | High | Required before backend/admin public testing |
| SEO Metadata | Planned | High | Required before launch |
| Sitemap / robots.txt | Planned | High | Required before launch |
| Image Optimization | Planned | High | Required before launch |
| Analytics | Deferred | Low | Optional unless business requires |

## Phase 8 Batch Completion Snapshot

| Batch | Status | Notes |
|---|---|---|
| Batch 1 | Complete | Product catalog v5 mock APIs |
| Batch 2 | Complete | CMS content mock APIs |
| Batch 3 | Complete | ID service and repository foundation |
| Batch 4 | Complete | DynamoDB-ready CRM repository wiring |
| Batch 5 | Complete | DynamoDB table setup scripts |
| Batch 5A | Complete | Philippines contact-number cleanup |
| Batch 6 | Complete | JSON seed data and safe seed loader |
| Batch 7 | Complete | DynamoDB connection/repository prep |
| Batch 8 | Complete | Repository mode switch |
| Batch 9 | Complete | Public frontend API client preparation |
| Batch 10 | Complete | Public pages connected to backend APIs |
| Batch 11 | Complete | Public booking/inquiry form API integration |
| Batch 12 | Complete | AWS DynamoDB tables created and verified ACTIVE |
| Batch 13 / 13A | Complete | DynamoDB seed loader and null cleanup |
| Batch 14 | Complete | DynamoDB mode API test |
| Batch 15 | Complete | DynamoDB public API wiring |
| Batch 16 | Complete | Public website DynamoDB end-to-end regression |
| Batch 17 | Complete | Admin dashboard shell |
| Batch 18 | Complete | Admin lead management pages |
| Batch 19 | Complete | Admin catalog management pages |
| Batch 20 | Complete | Admin catalog CRUD backend/actions |
| Batch 21 | Complete | Admin CMS management pages/actions |
| Batch 22 | Complete | Admin DynamoDB regression tests |
| Batch 23 | Complete | Admin auth/Cognito prep |
| Batch 24 | Complete | S3/image upload preparation |
| Batch 24A | Complete | Contact Person photo upload preparation |
| Batch 25 | Complete | Excel/CSV launch data templates |
| Batch 26 | Complete | Launch data import loader |
| Batch 27 | Complete | Final admin UI polish |
| Batch 28 | Complete | Full public/admin regression checklist |
| Batch 29 | Current Active | Documentation/status update |

## Completed Features

- Public frontend pages for the current phase: Homepage, Products, Promotions, Brands, About Us, Services, Contact Us, and Booking.
- Public API-backed rendering for products, brands, categories, key features, package banners, CMS pages, services, contact information, booking, and inquiry.
- FastAPI backend foundation with public/admin route modules.
- Mock repository mode and DynamoDB repository mode.
- DynamoDB table creation scripts, seed data, seed loader, null cleanup, connection checks, and regression tests.
- Admin dashboard shell.
- Admin lead management for bookings, inquiries, and customers.
- Admin catalog management for products, categories, brands, and key features.
- Admin CMS management for About, Project Gallery, Services, and Contact Us.
- Admin media upload preparation, including Contact Person photo/profile-image field.
- Cognito/admin-auth preparation with auth disabled locally by default.
- Excel/CSV launch data templates and safe import loader.
- Full public/admin regression checklist and script.

## Current Active Work

| Feature | Notes |
|---|---|
| Phase 8 documentation/status update | Batch 29 updates source-of-truth Markdown files after completed implementation/regression |
| Next planning | Deployment/security/pre-launch phase planning should start after docs are committed |

## Planned Features

- EC2 public-IP backend/admin deployment test.
- Free-Tier deployment review.
- AWS billing alerts.
- Real Cognito admin protection before external/public admin testing.
- S3 binary upload/storage enablement for admin media fields.
- SEO metadata.
- sitemap.xml and robots.txt.
- Image optimization.
- CloudFront/SSL/domain planning after IP-based testing/demo.

## Deferred Features

| Feature | Reason |
|---|---|
| Online checkout | Business model is lead generation, not ecommerce |
| Product detail pages | Post-launch enhancement |
| Brand detail pages | Post-launch enhancement |
| Product image zoom | Deferred |
| Modal gallery | Deferred |
| Swipe-to-close modal gesture | Deferred |
| Quotation generator | Future CRM enhancement |
| Advanced analytics dashboard | Future enhancement |
| Full roles/permissions matrix | Future admin hardening after Cognito launch protection |
| Admin audit logs | Future compliance/traceability enhancement |
| `rsa_product_types` / managed subcategory table | Deferred; subcategory remains a manual field at launch |

## Known Gaps

- External/public deployment has not been completed.
- AWS billing alerts still need to be configured before external AWS testing.
- Free-Tier deployment review still needs to be completed before external demo/public testing.
- Real Cognito protection is not enabled yet; admin auth is prepared but disabled locally by default.
- S3 binary upload/storage is not enabled yet; admin media fields currently prepare/select resolved media paths/keys.
- SEO metadata, sitemap.xml, robots.txt, and image optimization remain pre-launch tasks.
- Product/promotions static markup duplication has been reduced by API integration, but full production data migration depends on final imported company content.

## Current Priorities

1. Commit Batch 29 documentation/status update.
2. Plan the next phase for deployment/security/pre-launch readiness.
3. Configure AWS billing alerts before any public/external AWS test.
4. Keep mock repository mode as the safe local default.
5. Use DynamoDB mode intentionally only for AWS-backed regression/import testing.
6. Keep completed public pages closed unless explicitly reopened.
7. Preserve the AWS Free-Tier-first architecture during deployment planning.
