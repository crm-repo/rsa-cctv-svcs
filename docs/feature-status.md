# RSA CMS / Mini-CRM Feature Status

## Authority

This document is the authoritative implementation progress tracker. If status here conflicts with another document, this document controls implementation status.

Last updated: 2026-06-26  
Update scope: Phase 8 Batch 60B backup/restore/production safety notes completed, Batch 60A final demo-readiness pass next, Batch 59B confirmation still pending, and Batch 61/domain deferral preserved.


## Phase 8 Continuation Status — Batches 30 to 60C

This section supersedes older Batch 29-only planning notes for deployment/security/media/admin continuation work.

### Completed / closed batches after Batch 29

| Batch | Status | Summary |
|---|---|---|
| Batch 30 | Complete | AWS cost-safety and billing-alert checklist/script prepared. |
| Batch 31 | Complete | EC2 public-IP deployment preflight prepared. |
| Batch 32 | Complete | EC2 IAM/security checklist prepared. |
| Batch 33 | Complete | EC2 deployment permission setup guide prepared. |
| Batch 34 | Complete | EC2 demo instance setup using one locked-down Free-Tier-first instance; no ALB/NAT/RDS/Route 53. |
| Batch 35 | Complete | EC2 SSH/connect and server environment preparation. |
| Batch 36 | Complete | Backend/frontend runtime deployed to EC2; FastAPI systemd service in DynamoDB mode. |
| Batch 37 | Complete | Nginx public-site proxy on port 80 with admin initially blocked. |
| Batch 38 | Complete | Nginx public API exposure lockdown; admin/CRM and direct port access blocked. |
| Batch 39 | Complete | Public EC2 smoke regression. |
| Batch 40 | Complete | Cognito admin-auth preflight. |
| Batch 41 | Complete | Cognito admin user pool setup/templates. |
| Batch 42 | Complete | Local Cognito admin-auth wiring with login/auth routes. |
| Batch 43 | Complete | Cognito config deployed to EC2 while admin remained blocked. |
| Batch 44 | Complete | Admin static/login and auth endpoint exposure through Nginx. |
| Batch 46 | Complete | Protected admin/CRM API exposure through Nginx with backend bearer-token middleware. |
| Batch 47 | Complete | Authenticated admin API/browser smoke. |
| Batch 47A | Complete | Auth smoke token parse/redaction fix. |
| Batch 48 | Complete | Full authenticated admin EC2 regression. |
| Batch 49 | Complete | Dynamic API-rendered public Products/Promotions/Brands catalog. |
| Batch 49B | Complete | Public catalog API pagination limit fix using `per_page=50` and all pages. |
| Batch 50 | Complete | Homepage/About/Services/Contact/Booking CMS and lead pages bound to APIs. |
| Batch 54A | Complete | Static HTML data extraction review: 7 categories, 22 brands, 28 products, 188 key features, 1 about, 4 gallery, 12 services, 10 contact records. |
| Batch 54B | Complete | Safe DynamoDB wipe/reimport from reviewed static data without deleting tables or resetting counters downward. |
| Batch 54C | Complete | Optional product price/package quotation hotfix; package products may show Get Quotation. |
| Batch 55A | Complete | Admin media path interim fix; Browse/Choose File does not overwrite existing paths unless upload is prepared. |
| Batch 55B | Complete | Admin category/subcategory/brand protection polish; product category/subcategory dropdowns and dependency protections verified. |
| Batch 55C | Complete | Admin page overall polish; navigation, labels, login theme, media picker repair, required markers, and UI cleanup. |
| Batch 55D | Complete | Admin Settings page finalization, notification bell dropdown, user menu dropdown, Settings link enablement, logout/session utility reuse. |
| Batch 56A | Complete | Backend media upload/display endpoints plus private S3 media bucket/runtime setup and EC2 S3 smoke. |
| Batch 56B | Complete | Admin media upload integration for Products, Brands, Project Gallery, and Contact Person photos; EC2 media display/upload smoke passed after Nginx fixes. |
| Batch 56C | Complete | Products/Brands S3 image backfill; Project Gallery and Contact Person backfill intentionally skipped/manual. |
| Batch 56D | Complete | Promotions hero fixed to show promoted package products only; Brands left unchanged because already dynamic. Pushed to Git. |

### Deferred / current / planned batches after Batch 56D

| Batch | Status | Summary |
|---|---|---|
| Batch 57 | Deferred | SEO metadata/page titles deferred until Route 53/final domain is ready to avoid duplicate canonical/Open Graph/sitemap/robots work. |
| Batch 58 | Complete / Local testing passed | Image lazy loading applied and locally tested; no backend/S3 path changes. Local backend must use S3 media mode when validating `/api/media/...` paths. |
| Batch 59A | Complete / Local testing passed | Cognito Groups + Settings > Users management completed for the current local/admin scope, including Admin/Standard roles, one-time temporary password handling, and first-login password-change UI. EC2 role/user smoke remains part of Batch 60A. |
| Batch 59B | Planned / confirm before demo | Admin-only restricted actions/delete controls. Standard users should not see Settings/delete controls; backend should still enforce 403. Leads remain non-delete. Confirm completion or run before Batch 60A if not already applied. |
| Batch 60C | Complete for now / accepted scope | Inserted public/admin polish batch. Includes public contact/social polish, admin logo/product UI polish, login/sidebar logo polish, and homepage Featured Products criteria update using `show_pack_flag` for non-package featured products. Code was committed; EC2 final active release must be confirmed during Batch 60A. |
| Batch 60B | Complete | Backup/restore/production safety notes and operational runbooks documented. Supersedes earlier Batch 64 backup/rollback idea. Documentation/procedure only; no paid backup services added. |
| Batch 60A | Planned / next final demo gate | EC2 public-IP demo smoke checklist / demo readiness pass, including final EC2 smoke regression, active-release confirmation, admin smoke, media display/upload checks, and demo data sanity check. Supersedes earlier Batch 62 regression idea for demo readiness. |
| Batch 61 | Deferred / Later | Route 53/domain, ACM, SSL/HTTPS, CloudFront, and EC2 origin planning after final customer domain/cost approval. Supersedes earlier Batch 65 domain planning idea. |
| Batch 62 | Deferred / Later | Final launch checklist after domain/security/backup readiness, if needed. |

### Current authorization and user-management decision

- Use Cognito Groups for admin authorization roles: `Admin` and `Standard`.
- Do not use the Cognito `profile` attribute for role/permission decisions.
- Do not add a DynamoDB users table for launch user management.
- Settings > Users reads/manages Cognito users only through protected FastAPI backend routes.
- User viewing/add/update/enable/disable/group assignment is Admin-only.
- Standard users should not see Settings and must receive backend 403 for protected user-management routes.
- Admin-created users use Option A onboarding: Cognito invitation email suppressed; backend generates a temporary password; admin UI shows it once only after create/reset.
- Temporary passwords must not be stored, logged, or re-viewable. If lost, Admin resets/generates a new temporary password.
- First login must support browser-based password change for Cognito's new-password-required challenge; real users must not use CLI/command prompt.
- Create/view/edit forms use First Name and Last Name separately, mapped to Cognito `given_name` and `family_name`.
- Main Settings > Users table shows generated `Full Name = First Name + " " + Last Name`.
- Role comes from Cognito Group membership only, not `profile`, `name`, or a custom role attribute.
- Delete controls should be Admin-only for supported records.
- Leads (`bookings`, `inquiries`, customer/lead records) should not expose delete controls even for Admin; keep those records for traceability.

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
| Featured Products Preview | Complete | High | Public API connection completed in Phase 8; Batch 60C updates homepage Featured Products to show only non-package products with `show_flag=Y` and `show_pack_flag=Y`, retaining existing display limit/page-size behavior and empty-state behavior. |
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
| User Roles / Permissions | Complete / Local testing passed | Medium | Cognito Groups (`Admin`, `Standard`) and Settings > Users were implemented in Batch 59A; no DynamoDB users table for launch. EC2 role smoke remains part of Batch 60A. |
| Audit Logs | Deferred | Medium | Future admin audit trail |
| Backend FastAPI | Complete | High | Local FastAPI backend, route modules, config, CORS, health endpoint, Swagger docs |
| Repository Layer | Complete | High | Mock/DynamoDB repository mode switch implemented; mock remains safe default |
| DynamoDB Integration | Complete | High | Approved 12 tables created in AWS `ap-southeast-1`; DynamoDB mode tested successfully |
| DynamoDB Seed Data | Complete | High | JSON seed data and safe seed loader implemented; null cleanup applied |
| DynamoDB Regression Tests | Complete | High | Public/admin DynamoDB regression tests passed |
| Cognito Admin Auth | Complete | High | Cognito login/JWT protection deployed for admin/API access; Batch 59A adds Cognito Groups-based Admin/Standard user management for the current scope. |
| S3 / Image Upload | Complete | High | Private S3 media storage, backend upload/display routes, admin upload integration, and EC2 smoke completed in Batches 56A/56B |
| Excel/CSV Launch Data Templates | Complete | Medium | Company-friendly launch data templates created and validated |
| Launch Data Import Loader | Complete | Medium | Safe dry-run-first CSV/Excel import loader implemented; writes only with `--execute` |
| Full Public/Admin Regression | Complete | High | Batch 28 regression script/checklist passed in current testing |
| CloudFront / SSL | Planned | High | Required for production/domain launch |
| AWS EC2 Deployment | Complete for demo | High | Single Free-Tier-first EC2 public-IP deployment path implemented and tested; keep instance stopped unless actively testing |
| Route 53 / Domain | Planned | Medium | Delayed until after EC2 public-IP testing/demo |
| AWS Billing Alerts | Planned | High | Required before public/external AWS testing |
| Free-Tier Deployment Review | Planned | High | Required before backend/admin public testing |
| SEO Metadata | Deferred | High | Deferred until final Route 53/domain to avoid duplicate canonical/Open Graph work |
| Sitemap / robots.txt | Deferred | High | Deferred until final domain and launch URL are ready |
| Image Optimization / Lazy Loading | Complete / Local testing passed | High | Batch 58 lazy loading completed locally; image compression remains optional/future only if reopened. |
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
| Batch 60B backup/restore/safety notes | Completed documentation/procedure package; use as the operational safety reference before 60A. |
| Batch 60A demo-readiness pass | Next final gate after Batch 60B and any required Batch 59B confirmation; must verify current EC2 active release, public/admin smoke, roles, media, lead capture, and demo data. |

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

- Batch 60A final EC2 public-IP demo readiness pass is still pending.
- Batch 59B Admin-only restricted/delete action completion should be confirmed before the final demo pass.
- Batch 60C code was committed and accepted for the current scope; the final EC2 active release should be confirmed during Batch 60A because the last pasted EC2 deploy attempt stopped at an environment/tooling check before release switch.
- SEO metadata, canonical URLs, Open Graph URLs, sitemap.xml, and robots.txt remain deferred until the final domain is confirmed.
- Route 53/domain, ACM, CloudFront, and HTTPS remain deferred until customer demo/launch approval and final domain confirmation.
- Production backup/restore procedure is documented by Batch 60B; future automation remains optional and requires separate approval.
- Final company launch data still requires review/import before production launch.

## Current Priorities

1. Confirm whether Batch 59B restricted/delete actions are complete or still need to run before demo.
2. Run Batch 60A as the final EC2 public-IP demo readiness gate.
3. Use Batch 60B backup/restore/production safety notes as the operational safety reference during 60A and launch planning.
4. Confirm the current EC2 active release and smoke-test the accepted Batch 60C behavior during Batch 60A.
5. Keep EC2 stopped unless actively testing or deploying.
6. Keep SEO/domain/HTTPS work deferred until the final customer domain is approved.
7. Preserve the AWS Free-Tier-first architecture during all remaining demo and launch planning.
