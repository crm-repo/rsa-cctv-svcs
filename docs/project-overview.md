# RSA CMS / Mini-CRM Project Overview

## Current Project Status — Phase 8 Continuation Through Batch 56D

The project has progressed beyond the original Batch 29 documentation baseline.

Current completed state:

- Public website pages are effectively complete for the current phase.
- Public catalog/CMS/lead pages are API-backed where implemented.
- Backend FastAPI, DynamoDB mode, Cognito admin auth, EC2 demo deployment, Nginx routing, and S3 media storage are implemented for the current scope.
- Admin catalog/CMS/lead pages are operational with Cognito-protected access.
- Admin media upload works for Products, Brands, Project Gallery, and Contact Person images.
- Products/Brands media backfill to S3 is complete for Batch 56C scope.
- Promotions hero now uses promoted package products only.
- Batch 57 SEO work is intentionally deferred until Route 53/final domain.

Current active/planned work:

- Batch 58: image lazy loading local testing passed.
- Batch 59A: Cognito Groups + Settings > Users management, including Option A onboarding, one-time temporary passwords, first-login password change, First Name/Last Name forms, and generated Full Name table display.
- Batch 59B: Admin-only restricted/delete actions; Standard users do not see Settings/delete controls; no delete for lead records.
- Batch 60A: EC2 public-IP demo smoke checklist / demo readiness pass, including final EC2 smoke regression and demo data sanity check.
- Batch 60B: backup/restore/production safety notes.
- Batch 61: Route 53 + ACM + CloudFront + EC2 origin planning, deferred until customer domain approval.

Deferred until later/final launch planning:

- SEO metadata, canonical URLs, Open Graph URLs, sitemap.xml, robots.txt until the final domain is confirmed.
- Route 53/domain, SSL/HTTPS, and CloudFront implementation until customer/domain approval.
- Final launch checklist after demo readiness, backup/safety notes, and domain readiness.

## Document Purpose

This document is the entry point for the RSA CMS / Mini-CRM documentation set. It explains the project purpose, business goals, scope, high-level architecture, current implementation status, and where to find authoritative details.

For detailed requirements, see [requirements.md](./requirements.md).  
For technical design, see [architecture.md](./architecture.md).  
For implementation progress, see [feature-status.md](./feature-status.md).

## Project Purpose

RSA CMS / Mini-CRM is the public website, product catalog, promotions platform, content management system, and future lightweight CRM for **R.S.A. CCTV Installation Services**.

The public website is a **lead-generation catalog platform**, not an ecommerce checkout platform. It showcases CCTV installation services, maintenance services, CCTV packages, security products, trusted brands, promotional offers, and company credibility while guiding visitors toward inquiry and Request Site Visit actions.

The future platform will support website content management, customer records, booking requests, product/package inquiries, admin users, role permissions, image storage, and API/database-driven content.

## Business Objectives

1. Present R.S.A. CCTV Installation Services as a trusted CCTV/security installation and maintenance provider.
2. Promote recommended CCTV packages early in the customer journey.
3. Showcase CCTV products, packages, services, promotions, and trusted brands.
4. Generate leads through Request Site Visit, Book Appointment, product inquiry, package inquiry, and contact actions.
5. Support product discovery through category filters, brand filters, search, sorting, pagination, and quick view modals.
6. Build the current frontend in a way that can later connect to backend APIs, DynamoDB, S3 image storage, Cognito authentication, and an admin CMS/CRM.
7. Keep the first 12 months of the completed AWS deployment within Free Tier as much as practical, with Route 53/domain as the expected paid exception.
8. Provide a long-term maintainable foundation for future staff/admin workflows.

## Project Scope

### Current Public Website Scope

The public website includes or plans to include:

- Homepage
- Products page
- Promotions page
- Brands page
- About Us page
- Services page
- Contact Us page
- Booking / Request Site Visit page

### Future Admin / CMS Scope

The future admin panel will manage:

- Products
- Brands
- Categories
- Product types (deferred; `rsa_product_types` not for launch)
- Promotions
- Package product display / package promo placement sourced from `rsa_products`
- Services
- About Us content
- Project gallery
- Contact details
- Contact persons
- Social media links
- Site settings

### Future Mini-CRM Scope

The future CRM will manage:

- Customers
- Customer contacts
- Customer notes
- Related bookings
- Product/package inquiries
- Booking status workflow
- Inquiry status workflow
- Sales person assignment
- Customer source tracking
- Repeat customer flag

### Out of Scope for Current Frontend Phase

The following are deferred unless explicitly reopened:

- Online checkout
- Payment processing
- Product detail pages
- Brand detail pages
- Product comparison pages
- Full quotation generator
- Live backend integration
- Admin panel implementation
- CRM implementation
- User authentication implementation
- Product image gallery
- Product image zoom
- Swipe-to-close modal gesture
- Brand modal popups
- Separate Brands-specific CTA
- Scrolling logo strip under “Why We Use These Brands”

## High-Level Architecture Summary

The current implementation is static frontend.

| Layer | Current / Planned Technology | Status |
|---|---|---|
| Frontend | HTML, Tailwind CSS, custom CSS, JavaScript | Current |
| Backend API | Python FastAPI | Planned |
| Database | AWS DynamoDB | Planned |
| Authentication | AWS Cognito | Planned |
| Image/File Storage | AWS S3 | Planned |
| CDN / HTTPS | AWS CloudFront | Planned |
| Backend Hosting | AWS EC2 | Planned |
| Admin CMS / CRM | Custom admin interface | Planned |


## Cost and Deployment Constraint

RSA CMS / Mini-CRM was designed as an AWS Free-Tier-first project.

First 12 months target:

- Completed public website, backend, admin CMS, Mini-CRM, database, authentication and image storage should fit AWS Free Tier as much as practical.
- Route 53/domain is the expected paid exception once the project is ready for domain-based deployment.
- Before Route 53/domain setup, testing and demo should use the EC2 public IP or other free AWS-provided endpoint.
- After the free-tier window, the architecture should continue as a low-cost AWS deployment.

Default cost guardrails:

- One Free-Tier-eligible EC2 micro instance.
- DynamoDB with low provisioned capacity.
- S3 with optimized/compressed images.
- Cognito admin-only authentication with SMS disabled where possible.
- Booking and inquiry records visible in admin panel; no required SMS/email notifications for launch.
- No ALB, NAT Gateway, RDS, multiple always-on EC2 instances or unnecessary paid notification services unless explicitly approved.

## Key Stakeholders

| Stakeholder | Role |
|---|---|
| Business Owner | Approves business requirements, page content, visual direction, and lead-generation workflows |
| Frontend Developer / AI Agent | Implements public website, responsive behavior, catalog UI, filters, page polish, and static frontend logic |
| Backend Developer / AI Agent | Future FastAPI, DynamoDB, Cognito, API, admin, and CRM implementation |
| Admin / Staff Users | Future CMS/CRM users managing products, content, bookings, inquiries, and customer records |
| Customers / Website Visitors | Public users browsing products, packages, services, brands, and submitting inquiries/bookings |

## Success Criteria

The project is successful when:

1. Visitors can quickly understand the company’s CCTV services, products, packages, and value proposition.
2. Recommended CCTV packages are immediately visible on the homepage.
3. Products can be browsed by category, brand, sale status, search, and sorting.
4. Promotions page shows sale/promotional items only.
5. Brands page supports brand-first product browsing.
6. Product/package modals display correct information.
7. Mobile, tablet, and desktop layouts are polished and usable.
8. Customers can submit booking and inquiry requests.
9. Future admin users can manage content, catalog records, and CRM records.
10. Public records can be shown or hidden using `show_flag`.

## Latest Authoritative Project Status

`feature-status.md` is the authoritative implementation tracker. The summary below reflects the latest known state after Phase 8 Batch 28 regression and Batch 29 documentation/status update.

| Area | Latest Status | Notes |
|---|---|---|
| Public Website | Complete for current phase | Homepage, Products, Promotions, Brands, About Us, Services, Contact Us, and Booking are complete unless reopened |
| Public API Integration | Complete | Public pages and public booking/inquiry forms are connected to backend APIs |
| Backend / FastAPI | Complete for Phase 8 | Local FastAPI backend, public/admin routes, repository layer, mock mode, and DynamoDB mode are implemented |
| DynamoDB | Complete for Phase 8 | 12 approved `rsa_` tables were created in AWS `ap-southeast-1` and regression-tested |
| Admin Dashboard | Complete for Phase 8 | Admin dashboard shell and navigation are implemented |
| Admin Lead Management | Complete for Phase 8 | Bookings, inquiries, and customers can be listed/viewed/updated |
| Admin Catalog Management | Complete for Phase 8 | Products, categories, brands, and key features support create/update workflows |
| Admin CMS Management | Complete for Phase 8 | About, project gallery, services, and contact-us records support create/update workflows |
| Admin UI Polish | Complete for Phase 8 | Product-name preview, key-feature suggestions, media-field presentation, and drawer/toolbar polish completed |
| Admin Auth | Prepared | Cognito/admin-auth preparation exists; real protection remains disabled locally until deployment/security phase |
| Media Upload | Prepared | Choose File/media-key prep exists; real S3 binary upload/storage remains a later enablement step |
| Launch Data Templates / Import | Complete for Phase 8 | Excel/CSV templates and safe dry-run-first import loader are implemented |
| Regression Testing | Complete for Phase 8 | Full public/admin regression checklist and script passed in current testing |
| SEO / Deployment | Planned | Required before production launch |

## Current Authoritative Updates

1. **Phase 8 backend/admin implementation is complete for the current local/regression phase.** Older statements that backend/admin are only planned are superseded by `feature-status.md`.
2. **Mock repository mode remains the safe default.** DynamoDB mode is used intentionally for AWS-backed regression/import testing.
3. **The approved Phase 8 Final v5 DynamoDB/API plan remains the technical baseline.** The launch table set is 12 DynamoDB tables with 5 approved GSIs.
4. **Admin auth is prepared but not externally enabled.** Cognito protection must be completed before public/external admin testing.
5. **Admin media fields use Browse/Choose File preparation.** Real S3 binary upload/storage remains a later deployment/storage task.
6. **Launch data should be collected through Excel/CSV templates, not manual JSON editing.** JSON seed data remains useful for developer testing.
7. **Completed public pages should not be reopened unless explicitly requested.**
8. **AWS Free-Tier-first remains mandatory.** Avoid ALB, NAT Gateway, RDS, multiple always-on EC2 instances, SMS/MFA costs, and unnecessary paid features.

## Documentation Map

| Document | Purpose |
|---|---|
| [architecture.md](./architecture.md) | Authoritative technical design reference |
| [requirements.md](./requirements.md) | Authoritative business and functional requirements specification |
| [feature-status.md](./feature-status.md) | Authoritative implementation progress tracker |
| [open-issues.md](./open-issues.md) | Risks, blockers, technical debt, unresolved decisions, dependencies |
| [implementation-guidelines.md](./implementation-guidelines.md) | Development, coding, testing, and AI-agent implementation guidance |
| [decision-log.md](./decision-log.md) | Significant project decisions and rationale |


## Phase 8 Final v5 Backend/Data Plan

The Phase 8 DynamoDB/API access-pattern plan is approved for implementation. The approved plan uses a Free-Tier-first simple multi-table DynamoDB approach with 12 launch tables and 5 launch GSIs.

Main approved backend direction:

- Product catalog and package products are stored in `rsa_products`.
- Package homepage/promo placement uses `show_pack_flag`.
- Contact Us content is consolidated into `rsa_contact_us`.
- Customer matching at launch uses contact number GSI only.
- Product category and brand filtering are optimized with two product GSIs.
- CMS content for About Us, Project Gallery, Services, and Contact Us will become API/database-driven while preserving the current public page layouts.

See [PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md](./PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md) for the approved implementation plan.


## Phase 8 Current Implemented Baseline

As of Batch 29, Phase 8 has completed the local backend/admin/CMS/Mini-CRM implementation and regression baseline.

Implemented baseline:

- FastAPI backend with public and admin route modules.
- Mock repository mode as the safe default.
- DynamoDB repository mode for AWS-backed testing.
- Approved `rsa_` DynamoDB tables created and verified ACTIVE in `ap-southeast-1`.
- Public website pages connected to backend APIs.
- Public booking and inquiry form submission connected to backend APIs.
- Admin dashboard, lead management, catalog management, CMS management, auth prep, and media prep.
- Excel/CSV launch templates and safe import loader.
- Full public/admin regression script and manual checklist.

Still outside this completed baseline:

- Production deployment.
- Real Cognito enforcement.
- Real S3 binary upload/storage.
- CloudFront/SSL/domain.
- SEO/sitemap/robots/image optimization.
- Billing-alert and Free-Tier deployment readiness verification.
