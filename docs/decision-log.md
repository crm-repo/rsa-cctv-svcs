# RSA CMS / Mini-CRM Decision Log

## Purpose

This document records significant project decisions and their rationale. For implementation status, use [feature-status.md](./feature-status.md). For technical architecture, use [architecture.md](./architecture.md). For business requirements, use [requirements.md](./requirements.md).

## ADR-001: Use Lead-Generation Model Instead of Ecommerce Checkout

| Field | Value |
|---|---|
| Date | Approved before current documentation baseline |
| Status | Accepted |
| Context | CCTV installation requires consultation, site visit, installation planning, and quotation. |
| Decision | The website will not include ecommerce checkout for launch. |
| Reasoning | Lead capture better matches the business process than online payment. |
| Impact | CTAs focus on Request Site Visit, Book Appointment, contact, and inquiry workflows. |

## ADR-002: Use Static Frontend First, Backend Later

| Field | Value |
|---|---|
| Date | Phase 1 |
| Status | Accepted |
| Context | The project is being built page-by-page with frontend polishing first. |
| Decision | Use static HTML, Tailwind CSS, custom CSS, and JavaScript for the current phase. |
| Reasoning | Enables faster UI development and approval before backend/admin complexity. |
| Impact | Product data currently lives in HTML/data attributes but must remain backend-ready. |

## ADR-003: Future Backend Stack

| Field | Value |
|---|---|
| Date | Phase 1 setup |
| Status | Accepted |
| Context | The project needs backend APIs, admin authentication, image storage, and database support. |
| Decision | Use Python FastAPI, AWS DynamoDB, AWS Cognito, AWS S3, AWS CloudFront, and AWS EC2. |
| Reasoning | AWS stack supports low-cost scalable hosting and future CMS/CRM needs. |
| Impact | Future backend structure and deployment planning are based on AWS services. |

## ADR-004: Products Page Is the Master Catalog Architecture

| Field | Value |
|---|---|
| Date | Products implementation phase |
| Status | Accepted |
| Context | Products, Promotions, and Brands require similar catalog behavior. |
| Decision | Products page is the master catalog implementation. |
| Reasoning | Reusing search, filters, sorting, pagination, modal, and cards reduces duplication. |
| Impact | Promotions and Brands should reuse Products logic where possible. |

## ADR-005: Promotions Page Reuses Products Architecture

| Field | Value |
|---|---|
| Date | Promotions implementation phase |
| Status | Accepted |
| Context | Promotions page needs product-grid behavior for sale items and packages. |
| Decision | Promotions page is based on Products page catalog architecture. |
| Reasoning | Avoids duplicated UI and logic. |
| Impact | Sale filter, category filter, brand filter, search, sort, pagination, and modal are reused. |

## ADR-006: Promotions Sale Is a Hard Filter

| Field | Value |
|---|---|
| Date | Promotions implementation phase |
| Status | Accepted |
| Context | Promotions page should show promotional/sale items only. |
| Decision | Sale is always active on Promotions and cannot be removed. |
| Reasoning | Prevents non-sale products from appearing on Promotions. |
| Impact | All category, brand, search, and sort behavior operates within sale-only results. |

## ADR-007: Promotions All Products Behavior Superseded

| Field | Value |
|---|---|
| Date | Latest Promotions decision |
| Status | Accepted current decision; old redirect behavior superseded |
| Context | Earlier SRS stated All Products redirects to Products page. Later implementation decision changed this. |
| Decision | On Promotions, All Products clears category filtering while keeping Sale active. |
| Reasoning | Users expect All Products on Promotions to mean all sale products, not all catalog products. |
| Impact | The old redirect behavior is no longer authoritative. |

## ADR-008: Packages Are Products With `category = packages`

| Field | Value |
|---|---|
| Date | Package requirements phase |
| Status | Accepted |
| Context | Packages need to appear in catalog, promotions, and modal workflows. |
| Decision | A package is identified by `category = packages`; no separate `is_package` field is required for launch. |
| Reasoning | Simplifies schema and allows package modal reuse. |
| Impact | Package banners and package catalog items use normal product fields. |

## ADR-009: Use `show_flag` for Public Visibility

| Field | Value |
|---|---|
| Date | Requirements baseline v1.2 |
| Status | Accepted |
| Context | Public content records need a simple visible/hidden rule. |
| Decision | Use `show_flag = Y` for visible and `show_flag = N` for hidden. |
| Reasoning | Simple and consistent across public content tables. |
| Impact | Applies to Products, Brands, Services, Package Banners, and public content records. |

## ADR-010: `show_flag` Is Different From `status`

| Field | Value |
|---|---|
| Date | Requirements baseline v1.2 |
| Status | Accepted |
| Context | CRM/admin records also need workflow states. |
| Decision | `show_flag` controls public visibility; `status` controls workflow/internal state. |
| Reasoning | Avoids mixing public display rules with operational workflows. |
| Impact | Admin forms and backend validation must keep these fields distinct. |

## ADR-011: Homepage Recommended Packages Above Featured Products

| Field | Value |
|---|---|
| Date | Homepage polishing phase |
| Status | Accepted |
| Context | Packages are important business offerings. |
| Decision | Recommended Packages appear above Featured Products. |
| Reasoning | Package offers are more relevant to lead generation and customer decision-making. |
| Impact | Homepage order is Hero, Feature Strip, Recommended Packages, Featured Products, Products on Sale, About/Top Brands/Why Choose Us, Services, CTA, Footer. |

## ADR-012: Homepage Products on Sale Naming

| Field | Value |
|---|---|
| Date | Homepage polishing phase |
| Status | Accepted |
| Context | Older label “Promotions Preview” was less clear. |
| Decision | Use “Products on Sale.” |
| Reasoning | More direct and customer-friendly. |
| Impact | Homepage sale section naming updated. |

## ADR-013: Services Preview Uses Non-Square Images

| Field | Value |
|---|---|
| Date | Homepage responsive polishing |
| Status | Accepted |
| Context | Square/aspect ratio changes caused text overlap and layout issues. |
| Decision | Use `height: 300px`, `width: 100%`, `object-fit: cover` for service preview images. |
| Reasoning | Maintains better visual proportion and avoids text overlap. |
| Impact | Square service image layout was rejected. |

## ADR-014: Small Phone Landscape Uses One-Item Sliders

| Field | Value |
|---|---|
| Date | Homepage responsive polishing |
| Status | Accepted |
| Context | iPhone SE/small landscape layouts were cramped. |
| Decision | Recommended Packages and Our Services use one item per row/slide on small phone landscape. |
| Reasoning | Improves readability and prevents broken layout. |
| Impact | Special responsive rules exist for small landscape devices. |

## ADR-015: iPad Air/Pro Portrait Services Uses Desktop-Like Horizontal Layout

| Field | Value |
|---|---|
| Date | Homepage responsive polishing |
| Status | Accepted |
| Context | iPad Air/Pro portrait had enough width to support desktop-like layout. |
| Decision | Our Services displays horizontally like desktop on iPad Air/Pro portrait. |
| Reasoning | Better use of tablet screen width. |
| Impact | Tablet-specific responsive CSS applies. |

## ADR-016: Brands Page Is Brand-First

| Field | Value |
|---|---|
| Date | Brands page planning |
| Status | Accepted |
| Context | Products page already supports category-first browsing. |
| Decision | Brands page prioritizes brand selection as the primary filter. |
| Reasoning | Gives users a distinct browsing route by manufacturer. |
| Impact | Brand strip appears first in body; categories become secondary filters. |

## ADR-017: Brands Page Reuses Products Catalog Logic

| Field | Value |
|---|---|
| Date | Brands page planning |
| Status | Accepted |
| Context | Brands page still shows products and needs search/sort/filter behavior. |
| Decision | Reuse Products page catalog architecture. |
| Reasoning | Maintains consistency and reduces implementation effort. |
| Impact | Brand, category, search, sort, pagination, and product cards remain aligned. |

## ADR-018: Brands Page Category Buttons Exclude All Products and Sale

| Field | Value |
|---|---|
| Date | Brands page planning |
| Status | Accepted |
| Context | Brands page filter hierarchy differs from Products. |
| Decision | Reuse category buttons but remove All Products and Sale. |
| Reasoning | Brand is the primary filter; Sale is not the page focus. |
| Impact | Category filters narrow selected brand results. |

## ADR-019: Brand Strip One-Row / Two-Row Threshold

| Field | Value |
|---|---|
| Date | Brands page implementation |
| Status | Accepted |
| Context | Category strip behavior was tested and found to switch at 16. |
| Decision | Brand strip uses one row for 1–15 brands and two rows for 16+ brands. |
| Reasoning | Matches category strip behavior. |
| Impact | Brands page JS balances rows with `Math.ceil(totalBrands / 2)`. |

## ADR-020: Odd Brand Counts Put Extra Brand in First Row

| Field | Value |
|---|---|
| Date | Brands page implementation |
| Status | Accepted |
| Context | Two-row brand distribution needed a deterministic rule. |
| Decision | First/top row receives the extra brand for odd counts. |
| Reasoning | Keeps row balance predictable. |
| Impact | Example: 21 brands means 11 top row and 10 bottom row. |

## ADR-021: Brands Hero Logo Cards Should Not Be Transparent

| Field | Value |
|---|---|
| Date | Brands hero polish |
| Status | Accepted |
| Context | Transparent cards made black logo text unreadable on dark hero background. |
| Decision | Use darker off-white/light gray logo cards instead of transparent. |
| Reasoning | Preserves logo readability while reducing harsh full-white contrast. |
| Impact | Candidate colors include `#d1d5db`, `#cbd5e1`, and `#bfc7d1`. |

## ADR-022: Products Active Brand Border Uses Pseudo-Element

| Field | Value |
|---|---|
| Date | Brands active state troubleshooting |
| Status | Accepted as implementation fact |
| Context | Attempts to style Brands active state created double indicators. |
| Decision | Products active brand indicator is controlled by `.brand-strip-item.active::after`. |
| Reasoning | The visible border is not the element border but a pseudo-element. |
| Impact | Brands page must override the pseudo-element before applying custom active styling. |

## ADR-023: Brands Page Disables Products Active Pseudo-Element

| Field | Value |
|---|---|
| Date | Brands active state troubleshooting |
| Status | Accepted |
| Context | Brands page needed different active styling and larger logos. |
| Decision | Use `.brands-page .brand-strip-item.active::after { display: none !important; }`. |
| Reasoning | Prevents duplicate or conflicting active indicators. |
| Impact | Brands page can use its own active outline or highlight. |

## ADR-024: Brands Page Two-Row Gap Fixed at `16px 16px`

| Field | Value |
|---|---|
| Date | Brands strip polish |
| Status | Accepted |
| Context | Smaller gaps caused active indicator clipping. |
| Decision | Use `gap: 16px 16px` for two-row Brands strip. |
| Reasoning | Prevents clipping while preserving reasonable spacing. |
| Impact | This value should not be reduced without retesting active indicator behavior. |

## ADR-025: Completed Pages Should Not Be Reopened Unless Requested

| Field | Value |
|---|---|
| Date | Current project workflow decision |
| Status | Accepted |
| Context | Reopening completed pages causes repeated polish cycles and regression risk. |
| Decision | Homepage, Promotions, and Brands are closed for current phase unless specifically reopened. |
| Reasoning | Keeps progress moving to the next page. |
| Impact | Current active work should move to About Us page. |

## ADR-026: Future Admin Includes CMS and CRM

| Field | Value |
|---|---|
| Date | Admin planning |
| Status | Accepted |
| Context | The project is not only a public website; it requires customer and lead management. |
| Decision | Future admin includes Products, Brands, Promotions, Customers, Bookings, Inquiries, Contents, Services, Settings, and Users. |
| Reasoning | Supports long-term maintenance and lead follow-up. |
| Impact | Backend schema and admin menu include CMS and CRM modules. |

## ADR-027: Booking and Inquiry Auto-Create Customers

| Field | Value |
|---|---|
| Date | CRM planning |
| Status | Accepted |
| Context | Leads from forms should become customer records automatically. |
| Decision | Booking and inquiry submissions auto-create customers if not existing. |
| Reasoning | Prevents lead loss and supports CRM follow-up. |
| Impact | Customer Status defaults to Prospect; source is Booking Request or Inquiries. |

## ADR-028: Feature Status Is the Authoritative Implementation Tracker

| Field | Value |
|---|---|
| Date | Documentation v2 audit |
| Status | Accepted |
| Context | Multiple documents reference project status, which can drift over time. |
| Decision | `feature-status.md` is the authoritative implementation progress tracker. |
| Reasoning | Centralizes status and reduces contradictions. |
| Impact | Other docs should reference status at a high level and defer to `feature-status.md`. |

## ADR-029: Architecture and Requirements Authorities Are Separated

| Field | Value |
|---|---|
| Date | Documentation v2 audit |
| Status | Accepted |
| Context | Technical design and business requirements were previously mixed across documents. |
| Decision | `architecture.md` controls technical design; `requirements.md` controls business/functional requirements. |
| Reasoning | Improves maintainability and AI-agent usability. |
| Impact | Future updates should place information in the correct document and cross-reference related docs. |

## ADR-030: AWS Free-Tier-First Deployment Strategy

| Field | Value |
|---|---|
| Date | Current documentation baseline |
| Status | Accepted |
| Context | From the start of the project, RSA CMS / Mini-CRM was intended to fit AWS Free Tier as much as practical during the first 12 months, then continue as a low-cost AWS deployment after the free-tier window. |
| Decision | The completed project must use a Free-Tier-first AWS architecture: one eligible EC2 micro instance, DynamoDB with low provisioned capacity, S3 for compressed assets, Cognito admin-only authentication, and CloudFront/ACM where applicable. Route 53/domain is the expected paid exception when domain-based launch is approved. Before Route 53, testing/demo should use the EC2 public IP or other free AWS-provided endpoint. |
| Reasoning | The business goal is to keep first-year AWS cost near zero except domain/DNS, while still supporting the public website, backend API, admin CMS, Mini-CRM, image storage and authentication. |
| Impact | Avoid ALB, NAT Gateway, RDS, multiple always-on EC2 instances, SMS workflows, unnecessary paid notifications, excessive CloudWatch retention and large unoptimized media storage unless explicitly approved after cost review. |

## ADR-031: Booking and Inquiry Notifications Are Optional for Launch

| Field | Value |
|---|---|
| Date | Current documentation baseline |
| Status | Accepted |
| Context | Booking and inquiry workflows are required for lead generation, but automatic SMS/email notifications can create extra AWS cost. |
| Decision | Booking and inquiry submissions must be stored and visible in the admin panel. SMS/email notifications are not required for launch and should be disabled by default for the Free-Tier-first deployment. |
| Reasoning | Admin-panel visibility satisfies the lead-capture requirement without introducing paid notification dependencies. |
| Impact | Future notification workflows may be added later only after cost review and explicit approval. |


## ADR-032: Phase 8 Final v5 DynamoDB/API Plan

| Field | Value |
|---|---|
| Date | Phase 8 backend planning |
| Status | Accepted |
| Context | The backend/admin CMS/CRM moved from mock in-memory API skeletons toward DynamoDB implementation planning. The project requires a Free-Tier-first DynamoDB design that avoids unnecessary tables and indexes while supporting product catalog performance and lead management. |
| Decision | Approve the Phase 8 Final v5 DynamoDB/API plan using `rsa_` table prefix, 12 launch tables, 5 launch GSIs, simple multi-table design, consolidated Contact Us table, product category/brand GSIs, customer contact-number GSI, booking/inquiry status GSIs, and `rsa_id_counters` for backend-generated sequential IDs. |
| Reasoning | The plan keeps the simplified launch capacity count at 17 RCU + 17 WCU minimum while optimizing the product table for category and brand filtering. It avoids unnecessary package-banner, contact-split, email, sale, show-pack, and CMS-content GSIs. |
| Impact | Backend implementation should follow `PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md`. Older assumptions about `rsa_package_banners`, split contact tables, customer email GSI, `old_price`, `display_order`, and product types for launch are superseded. |

## ADR-033: Package Products Reuse Products Table

| Field | Value |
|---|---|
| Date | Phase 8 backend planning |
| Status | Accepted |
| Context | Package products are already part of the product catalog and do not need duplicate banner records for launch. |
| Decision | Store packages in `rsa_products` using `category_key = packages`. Keep `GET /api/package-banners` as an API endpoint if useful, but source it from `rsa_products` filtered by `show_flag = Y`, `category_key = packages`, and `show_pack_flag = Y`. |
| Reasoning | Reduces table count, removes duplicate data, and keeps package management in product admin. |
| Impact | Do not create `rsa_package_banners` for launch. `show_flag` controls normal catalog/promotions grid visibility. `show_pack_flag` originally controlled package homepage/promo placement; Batch 60C later extends it as a category-scoped flag for non-package homepage Featured Products without adding a new database field. |

## ADR-034: Consolidated Contact Us Table

| Field | Value |
|---|---|
| Date | Phase 8 backend planning |
| Status | Accepted |
| Context | Contact Us content belongs to one RSA company, but the admin UI should remain organized into Company Contact, Contact Person, and Social Media sections. |
| Decision | Use one table, `rsa_contact_us`, with `contact_type` values `Company Contact`, `Contact Person`, and `Social Media`. Keep the admin UI split into 3 sections. Use fixed/default Company Contact record `CONT-0000001`. |
| Reasoning | Reduces DynamoDB table count while preserving a clean admin workflow. Contact Us records are small, so a `contact_type` GSI is not needed for launch. |
| Impact | Do not create `rsa_contact_company`, `rsa_contact_persons`, or `rsa_social_media` for launch. |

## ADR-035: Product Schema and Naming Rules

| Field | Value |
|---|---|
| Date | Phase 8 backend planning |
| Status | Accepted |
| Context | Product admin entry should be efficient while preserving manual control over product names and descriptions. |
| Decision | Use `display_seq`, remove `old_price`, determine sale status from `sale_price`, support `feature_01` through `feature_10` with minimum 3 features, use `rsa_key_features`, and default product name from `product_brand_name + feature_01 + subcategory` while keeping it editable. Do not auto-generate description and do not add `auto_name_flag`. |
| Reasoning | Improves admin data entry and keeps the database schema simple. |
| Impact | Product model/services/admin forms must be updated to match the approved schema. |

## ADR-036: Product Category Icons and Product GSIs

| Field | Value |
|---|---|
| Date | Phase 8 backend planning |
| Status | Accepted |
| Context | Product category buttons need Font Awesome icons, and products can become heavier than other CMS tables. |
| Decision | Add `icon_code` to `rsa_categories`. Add two launch product GSIs: `category_key-display_seq-index` and `product_brand_key-display_seq-index`. |
| Reasoning | `icon_code` avoids building a full icon picker for launch. Product GSIs optimize the most important catalog browsing paths while keeping the launch capacity plan within Free-Tier-first guardrails. |
| Impact | Category and product services must expose the approved fields and query paths. |


## ADR-037: Keep Mock Repository Mode as the Safe Local Default

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | The project now supports both mock and DynamoDB repository modes. Developers need a safe default that avoids accidental AWS writes/costs during normal local work. |
| Decision | Keep mock mode as the default. Use DynamoDB mode only when explicitly setting `RSA_REPOSITORY_MODE=dynamodb` for AWS-backed tests/imports. |
| Reasoning | Preserves Free-Tier-first safety and prevents accidental cloud writes during local development. |
| Impact | Test instructions must clearly identify when DynamoDB mode is being used and should remind developers to clear the environment variable afterward. |

## ADR-038: Use Excel/CSV as the Business-Facing Launch Data Format

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | JSON seed data is developer-friendly but not the best format for company-provided launch content. |
| Decision | Use Excel/CSV templates for business-facing launch data collection and keep JSON seed data for development/testing. |
| Reasoning | Excel/CSV is easier for the company to fill in and review. JSON remains useful for repeatable developer fixtures. |
| Impact | Import tooling must validate Excel/CSV data and write to DynamoDB only after explicit confirmation. |

## ADR-039: Keep Launch Data Import Dry-Run-First

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | Launch import can affect DynamoDB records and ID counters. |
| Decision | Import scripts must default to dry run and require explicit `--execute` for writes. |
| Reasoning | Prevents accidental data changes and supports safe review before import. |
| Impact | Documentation and scripts must show dry-run commands before execute commands. |

## ADR-040: Admin Media Fields Use Choose File Preparation Before Real S3 Upload

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | Admin users should not type folder paths manually, but real S3 binary upload/storage is not enabled yet. |
| Decision | Use Browse/Choose File controls to prepare/display resolved media paths or keys. Enable real S3 binary upload/storage in a later deployment/storage step. |
| Reasoning | Improves admin usability now while keeping storage implementation Free-Tier-first and controlled. |
| Impact | Product, brand, CMS image, and Contact Person photo fields should use the shared media prep workflow. |

## ADR-041: Contact Person Photo Field Scope

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | Contact Us admin records are consolidated into `rsa_contact_us`, but only Contact Person records need a profile/photo image field. |
| Decision | Add photo/profile image preparation only for Contact Person records. Do not add photo upload fields for Company Contact or Social Media in this phase. |
| Reasoning | Matches the actual content need and avoids unnecessary fields in other Contact Us sections. |
| Impact | Contact Person records may store/display a resolved photo path/key. Company Contact and Social Media remain text/link/contact records. |

## ADR-042: Phase 8 Local Backend/Admin Baseline Is Complete Before Deployment/Security Work

| Field | Value |
|---|---|
| Date | Phase 8 Batch 29 |
| Status | Accepted |
| Context | Public APIs, admin pages, CRUD actions, DynamoDB mode, data templates/import, media prep, auth prep, UI polish, and full regression are now complete for the local/current phase. |
| Decision | Treat Phase 8 local backend/admin implementation as complete for the current phase after Batch 28 regression and Batch 29 documentation update. |
| Reasoning | The next meaningful work area is deployment/security/pre-launch readiness rather than more local feature expansion. |
| Impact | New work should move toward billing alerts, EC2/IP-based deployment, Cognito enforcement, S3 enablement, SEO, and launch readiness unless the user explicitly reopens a completed feature. |


## ADR-043: EC2 Demo Deployment Uses One Free-Tier-First Instance

| Field | Value |
|---|---|
| Date | Phase 8 Batches 30-39 |
| Status | Accepted |
| Context | The project needs public-IP demo/testing without early domain cost or complex paid AWS services. |
| Decision | Use one locked-down Free-Tier-first EC2 instance with Nginx and FastAPI systemd runtime. Avoid ALB, NAT Gateway, RDS, Route 53, and multiple instances for demo. |
| Impact | Test/demo through EC2 public IP until final domain planning. Stop EC2 when not actively testing. |

## ADR-044: Cognito Protects Admin/API Access Before Public Admin Exposure

| Field | Value |
|---|---|
| Date | Phase 8 Batches 40-48 |
| Status | Accepted |
| Context | Admin pages and admin/CRM APIs must not be exposed publicly without authentication. |
| Decision | Use Cognito login/JWT flow and backend bearer-token middleware for protected admin/API routes. |
| Impact | Admin exposure through Nginx requires token-based backend enforcement. |

## ADR-045: Public Catalog/CMS Pages Render From APIs While Preserving Static Fallback Layouts

| Field | Value |
|---|---|
| Date | Phase 8 Batches 49-50 |
| Status | Accepted |
| Context | Public frontend must move from hardcoded static content toward backend/CMS data without redesigning completed pages. |
| Decision | Bind public catalog/CMS/lead pages to APIs using JavaScript renderers while preserving page layout and fallback markup where useful. |
| Impact | Products, Promotions, Brands, Homepage, About, Services, Contact, and Booking can show backend/DynamoDB content. |

## ADR-046: Safe Static Data Import Does Not Delete DynamoDB Tables or Reset Counters Downward

| Field | Value |
|---|---|
| Date | Phase 8 Batches 54A-54B |
| Status | Accepted |
| Context | Static HTML data needed review/import into existing DynamoDB tables. |
| Decision | Use dry-run-first review/import; wipe/reseed approved records without deleting tables and without resetting `rsa_id_counters` downward. |
| Impact | Production-like data can be imported safely while preserving table infrastructure and ID safety. |

## ADR-047: Package Products May Omit Fixed Price and Display Get Quotation

| Field | Value |
|---|---|
| Date | Phase 8 Batch 54C |
| Status | Accepted |
| Context | Package products may not have a fixed full price before consultation/site visit. |
| Decision | Allow package product price to be optional. Public display should show `Get Quotation` and link users to Contact Us/request flow. |
| Impact | Do not force package price to zero. Treat quotation display as valid product/package behavior. |

## ADR-048: Category/Subcategory/Brand Admin Protection Rules

| Field | Value |
|---|---|
| Date | Phase 8 Batch 55B |
| Status | Accepted |
| Context | Admin users need to manage categories, subcategories, and brands without breaking active products. |
| Decision | Block category hide/delete if active products use it; block subcategory delete if products use it; block brand hide/delete when products depend on it; preserve current hidden values when editing existing records. |
| Impact | Products store category and subcategory snapshots; dependency checks protect catalog integrity. |

## ADR-049: Admin Settings Finalization Does Not Add User Management Yet

| Field | Value |
|---|---|
| Date | Phase 8 Batch 55D |
| Status | Accepted |
| Context | Settings, notification bell, and user menu were needed before user-management scope was ready. |
| Decision | Finalize Settings page/user menu/bell/dropdown using existing data only. Defer profile editing, password reset, and user management. |
| Impact | User management becomes a separate later batch with Cognito Groups. |

## ADR-050: Private S3 Media Storage With Backend Media Display Route

| Field | Value |
|---|---|
| Date | Phase 8 Batches 56A-56B |
| Status | Accepted |
| Context | Admin uploads should not rely on public S3 bucket access or local project-folder path typing. |
| Decision | Use private S3 bucket storage and serve media through backend `/api/media/...` route, proxied by Nginx before generic `/api/` blocking rules. |
| Impact | Admin upload fields store `/api/media/...` paths. Nginx must allow `/api/media/` and set upload size limit. |

## ADR-051: Products/Brands S3 Backfill Scope Is Limited

| Field | Value |
|---|---|
| Date | Phase 8 Batch 56C |
| Status | Accepted |
| Context | Existing static Product/Brand media paths needed backfill to S3, while few Project Gallery/Contact Person assets can be handled manually. |
| Decision | Backfill Products and Brands only. Skip Project Gallery and Contact Person bulk backfill. Use approved D-Link record mapping and skip missing local files. |
| Impact | Products/Brands media paths point to S3-backed `/api/media/...`; remaining small sets can be manually uploaded. |

## ADR-052: Promotions Hero Uses Promoted Package Products Only

| Field | Value |
|---|---|
| Date | Phase 8 Batch 56D |
| Status | Accepted |
| Context | Promotions hero must not show package records where Promote Package is disabled. Brands hero was already dynamic and should not be touched. |
| Decision | Render Promotions hero from already-loaded products filtered by package/kits category, `show_flag=Y`, and `show_pack_flag=Y`. Leave Brands hero dynamic renderer unchanged. |
| Impact | Promotions hero respects admin Promote Package setting and avoids duplicate Brands renderer risk. |

## ADR-053: Defer SEO Metadata Until Final Domain / Route 53

| Field | Value |
|---|---|
| Date | Phase 8 Batch 57 Planning |
| Status | Accepted |
| Context | Canonical URLs, Open Graph URLs, sitemap.xml, and robots.txt depend on the final public domain. |
| Decision | Defer Batch 57 SEO metadata/page titles and related files until Route 53/final domain is ready. Do not use EC2 public IP as canonical URL. |
| Impact | Avoids duplicate SEO work and wrong launch signals. |

## ADR-054: Use Cognito Groups for Admin/Standard Authorization

| Field | Value |
|---|---|
| Date | Phase 8 Batch 59A Planning |
| Status | Accepted |
| Context | Admin page needs Admin vs Standard user capabilities without creating a DynamoDB users table. |
| Decision | Use Cognito Groups named `Admin` and `Standard`. Do not use the Cognito `profile` attribute for roles. Manage users through FastAPI backend routes only. |
| Impact | Settings > Users is Admin-only; Standard users are restricted by UI and backend 403 checks. |

## ADR-055: Leads Are Non-Delete Records

| Field | Value |
|---|---|
| Date | Phase 8 Batch 59B Planning |
| Status | Accepted |
| Context | Booking/inquiry/customer lead records are operational history and should remain available for traceability. |
| Decision | Do not enable delete for leads even for Admin users. Use status workflows/archive-style behavior instead of destructive delete for leads. |
| Impact | Batch 59B delete controls apply only to approved non-lead record types. |

## ADR-056: Project-Structure Patch Zips Are Preferred

| Field | Value |
|---|---|
| Date | Phase 8 Continuation |
| Status | Accepted |
| Context | Root-level batch folders created repo clutter and diverged from earlier Phase 8 delivery style. |
| Decision | Deliver patches in project-structure zips (`frontend/`, `backend/`, `docs/`, etc.) and avoid committing temporary root batch folders. |
| Impact | Cleaner repository, fewer accidental commits, and easier file review. |

## ADR-057: Batch 59A User Onboarding Uses One-Time Temporary Passwords

| Field | Value |
|---|---|
| Date | Phase 8 Batch 59A Planning |
| Status | Accepted |
| Context | Admin-created Cognito users need a practical onboarding path without command-line password reset and without adding SES/email invitation dependency for launch. |
| Decision | Use Option A: suppress Cognito invitation email, generate a temporary password server-side, show it once in Settings > Users after create/reset, and require the user to change it through the browser first-login password-change flow. Do not store, log, or re-display temporary passwords. If lost, Admin resets/generates a new temporary password. |
| Impact | Batch 59A must add first-login password-change UI support and reset temporary password behavior. No DynamoDB users table or password storage is added. |

## ADR-058: Batch 59A User Fields Use First/Last Name With Generated Full Name

| Field | Value |
|---|---|
| Date | Phase 8 Batch 59A Planning |
| Status | Accepted |
| Context | Cognito exposes separate standard name attributes and the admin Users table should remain compact. |
| Decision | User creation and view/edit modal use First Name and Last Name, mapped to Cognito `given_name` and `family_name`. The main Settings > Users table shows one system-generated Full Name column built from First Name + Last Name. Role remains Cognito Group membership (`Admin` / `Standard`). |
| Impact | Admin UI table stays clean while preserving editable first/last name fields. Role is not stored in `profile`, `name`, or a custom role field. |

## ADR-059: Demo Readiness and Backup Batches Split Into 60A and 60B

| Field | Value |
|---|---|
| Date | Phase 8 Demo Readiness Planning |
| Status | Accepted |
| Context | Earlier plans included a full public/admin regression after final data and a separate backup/restore/rollback procedure. These need to happen before demo/production handoff. |
| Decision | Use Batch 60A for EC2 public-IP demo smoke checklist / demo readiness pass, including final EC2 smoke regression and demo data sanity check. Use Batch 60B for backup/restore/production safety notes. |
| Impact | Earlier Batch 62 maps to Batch 60A. Earlier Batch 64 maps to Batch 60B. Batch 60A should remind the user of the full demo checklist before execution. |

## ADR-060: Batch 61 Domain HTTPS Launch Uses Route 53 + ACM + CloudFront + EC2 Origin

| Field | Value |
|---|---|
| Date | Phase 8 Batch 61 Planning |
| Status | Accepted / Deferred until final domain approval |
| Context | The current demo uses EC2 public-IP HTTP, but launch needs domain-based HTTPS without adding high-cost infrastructure. |
| Decision | After customer/demo approval and final domain confirmation, use Route 53 + ACM + CloudFront + EC2 Nginx origin. Keep `/admin/` under the main domain by default. Route 53/domain is the approved paid exception. Cost planning assumes normal `.com` domain registration/renewal around USD 15/year plus Route 53 hosted zone around USD 0.50/month, about USD 20-25/year plus tiny DNS query charges. |
| Impact | CloudFront/ACM/domain setup is Batch 61. SEO canonical/Open Graph/sitemap/robots remain deferred until domain confirmation. Avoid ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, and unnecessary paid services unless separately approved. |



## ADR-061: Phase 8 Documentation Files Stay Flat Under docs Root

| Field | Value |
|---|---|
| Date | Phase 8 Batch 59A documentation cleanup |
| Status | Accepted |
| Context | Recent batch packages inconsistently placed README text files at the zip/project root and Markdown README files under nested `docs/Phase 8 README` or `docs/phase8` folders, creating project-folder clutter and documentation drift. |
| Decision | Keep main project Markdown docs and Phase 8 batch Markdown files directly under the root `docs/` folder. Use normal filenames such as `phase8_batch58_image_lazy_loading.md`. Keep apply/verify/cleanup scripts under `backend/scripts/`. Do not create root-level README/TXT files or nested Phase 8 README folders for new batch packages. |
| Reasoning | A flat docs folder matches the current project expectation, keeps batch documentation easy to find, and prevents duplicate README files from drifting out of sync. |
| Impact | Batch 59A and later packages must follow the cleaned docs/package structure. Existing nested README files should be consolidated into normal root `docs/phase8_*.md` files. |

## ADR-062: Reuse show_pack_flag for Non-Package Featured Products

| Field | Value |
|---|---|
| Date | Phase 8 Batch 60C |
| Status | Accepted |
| Context | The homepage Featured Products card previously used the first visible products by `display_seq` and had no dedicated featured flag. The existing `show_pack_flag` field was already used by package records for Promote Package placement. |
| Decision | Reuse the same stored `show_pack_flag` field as a category-scoped UI/business flag. For Packages/Kits, the admin label remains `Promote Package` and continues to control package/recommended/promo placement. For non-package products, the admin label becomes `Featured Product`, and the homepage Featured Products card filters non-package products where `show_flag=Y` and `show_pack_flag=Y`. |
| Reasoning | Avoids a DynamoDB schema/data migration and keeps the admin UI simple while still giving the business explicit control over homepage Featured Products. |
| Impact | No new database attribute is added. Existing display limits, carousel page-size behavior, sort behavior, and empty-state behavior are preserved. Batch 60A must confirm the current EC2 active release and smoke this behavior before demo. |

## ADR-063: Batch 60B Backup/Restore Safety Is Documentation-Only and Free-Tier-First

| Field | Value |
|---|---|
| Date | Phase 8 Batch 60B |
| Status | Accepted |
| Context | Before final public-IP demo readiness and production data handling, the project needs practical operational safety procedures for data backup, media preservation, deployment rollback, import safety, and secret handling. |
| Decision | Complete Batch 60B as documentation/procedure only. Document DynamoDB backup/export/restore, S3 media backup/restore, Git rollback, EC2 release rollback, Nginx config rollback, import dry-run rules, `rsa_id_counters` safety, secret handling, and EC2/cost-safety reminders. Do not add paid backup services, PITR, AWS Backup plans, or extra infrastructure without separate cost review and approval. |
| Reasoning | The current demo/pre-launch stage needs reliable operator guidance while preserving the AWS Free-Tier-first constraint and avoiding unnecessary paid services. |
| Impact | Batch 60B becomes the operational safety reference for Batch 60A and launch planning. Future backup automation or paid backup services remain optional and require separate approval. |


## ADR-064: Release Artifacts Decouple Production Runtime From GitHub

| Field | Value |
|---|---|
| Date | Phase 8 Post-Demo / Pre-Launch Planning |
| Status | Accepted / Deferred to Batch 62A |
| Context | Development and demo deployments sometimes used GitHub commit hashes, branch archives, or raw GitHub file downloads to put updated files onto EC2. This is useful for reproducibility during development, but the production runtime should not depend on GitHub availability, moving branch state, or GitHub credentials. |
| Decision | Add Batch 62A — Release Artifact / GitHub Decoupling Safety — to the post-demo/pre-launch pipeline. Production go-live should use a tagged release artifact zip/tarball and a controlled artifact copy, such as private S3 or local/offline backup. EC2 must continue to run from `/opt/rsa-cms/releases/*` with `/opt/rsa-cms/current` pointing to the active release. Runtime files must not require `github.com`, `raw.githubusercontent.com`, or GitHub tokens. |
| Reasoning | The live website/admin should continue running even if GitHub is unavailable, a branch changes, or deployment credentials rotate. Tagged artifacts, checksums, and local EC2 release folders make launches and rollbacks more reproducible. |
| Impact | Batch 62A is inserted before final launch/cutover. GitHub remains source control, but production runtime and rollback should use deployed release artifacts and local EC2 release folders. No paid CI/CD, ALB, NAT Gateway, RDS, paid WAF, or extra always-on infrastructure is added by default. |

## ADR-065: Keep Consolidated Contact Us Storage and Split the Admin Presentation

| Field | Value |
|---|---|
| Date | Phase 8 Batch 60E |
| Status | Accepted / locally implemented and browser-tested |
| Context | `rsa_contact_us` correctly consolidates Company Contact, Contact Person, and Social Media records, but one combined admin table showed many non-applicable fields as `---` and made operational review harder. |
| Decision | Keep the single `rsa_contact_us` table and existing APIs. In the Contact Us admin page, render three separate tables filtered by `contact_type`: Company Contact, Contact Persons, and Social Media. Each table must show only fields applicable to that type. Keep the shared search/sort/refresh/add/view-edit workflows and existing conditional drawer forms. |
| Reasoning | Improves readability and admin workflow without adding DynamoDB tables, GSIs, API routes, or data migration risk. |
| Impact | This is a frontend/admin presentation change only. Company Contact remains the fixed/default company record, Contact Person photo scope is unchanged, and public Contact Us rendering remains unchanged. |

## ADR-066: Dashboard Quick Actions Use Three Equal Desktop Add Buttons

| Field | Value |
|---|---|
| Date | Phase 8 Batch 60F-1 |
| Status | Accepted / locally implemented and browser-tested |
| Context | The dashboard has exactly three Quick Actions, but the older two-column grid placed the third action on a second row and reduced visual balance. |
| Decision | Render Add Product, Add Category, and Add Brand as three equal desktop columns on one row. Each action includes a boxed `+` indicator to emphasize that it opens an add/create workflow. On small screens, stack the actions in one column. |
| Reasoning | Uses the available dashboard width better, makes the add intent immediately visible, and preserves responsive usability. |
| Impact | Batch 60F initial selector-scoped CSS is superseded by Batch 60F-1's dedicated Quick Actions class and override. No route, API, or drawer behavior changes. |

## ADR-067: Reserve the Emphasized Login Status Area for Real Errors

| Field | Value |
|---|---|
| Date | Phase 8 Batch 60G |
| Status | Accepted / locally implemented and browser-tested |
| Context | The login page already has a normal instruction note, while the emphasized red status area also displayed routine guidance and progress messages before any error occurred. This made normal page state look like an error. |
| Decision | Keep normal email/password guidance in the information note and increase that note to `16px`. Keep the emphasized status area empty/hidden during normal page load, submission progress, and successful redirect. Show it only for actual login/authentication/configuration errors, using friendly non-technical wording. |
| Reasoning | Establishes a clear visual hierarchy: instructions are informational; the emphasized red area signals a real problem only. |
| Impact | Cognito flow, JWT behavior, first-login password challenge, and backend security are unchanged. The status element keeps accessible alert/live-region attributes. |
