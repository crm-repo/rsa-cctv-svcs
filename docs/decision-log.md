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
| Impact | Do not create `rsa_package_banners` for launch. `show_flag` controls normal catalog/promotions grid visibility. `show_pack_flag` controls homepage/promo hero placement only. |

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
