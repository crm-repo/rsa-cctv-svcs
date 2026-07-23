# RSA CMS / Mini-CRM Project Overview

## Current Project Status — Phase 8 Continuation Through Batch 60G Local Polish

The project has progressed beyond the original Batch 29 documentation baseline.

Current completed state:

- Public website pages are effectively complete for the current phase.
- Public catalog/CMS/lead pages are API-backed where implemented.
- Backend FastAPI, DynamoDB mode, Cognito admin auth, EC2 demo deployment, Nginx routing, and private S3 media storage are implemented for the current scope.
- Admin catalog/CMS/lead pages are operational with Cognito-protected access.
- Batch 60C public/admin polish was previously deployed and browser-tested; its separate-branch changes have now also been recovered into the current local `main` baseline and locally regression-tested.
- Batch 60E is complete in local browser testing: Contact Us admin records are shown in three type-specific tables while remaining stored in the single consolidated `rsa_contact_us` table.
- Batch 60F-1 is complete in local browser testing: Dashboard Quick Actions show Add Product, Add Category, and Add Brand as three equal one-row desktop actions with boxed `+` indicators.
- Batch 60G is complete in local browser testing: the emphasized login status is error-only, the normal instruction remains in a larger information note, and friendly error wording is preserved.
- Batch 60B backup/restore/production safety notes remain the operational safety reference.
- Batch 60A demo readiness remains accepted complete for the previously deployed EC2 public-IP demo state.
- Batch 57 SEO work remains deferred until Route 53/final domain.
- Batch 62A Release Artifact / GitHub Decoupling Safety remains in the post-demo/pre-launch pipeline.

Current active work:

- Commit and push the consolidated current local `main` version.
- Deploy that exact version to EC2 using the existing release-folder deployment flow.
- Smoke the login page, dashboard shortcuts, Contact Us split tables, recovered Batch 60C behavior, API health, and protected admin access.
- Stop EC2 after deployment/browser verification unless continuing directly with testing or demo activity.

Deferred until later/final launch planning:

- Release artifact / GitHub deployment decoupling safety before final launch/cutover.
- SEO metadata, canonical URLs, Open Graph URLs, sitemap.xml, and robots.txt until the final domain is confirmed.
- Route 53/domain, SSL/HTTPS, and CloudFront implementation until customer/domain approval.
- Final launch checklist after demo feedback, release artifact safety, backup/safety notes, and domain readiness.

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

`feature-status.md` is the authoritative implementation tracker. The summary below reflects the latest known state through the Batch 60C integration recovery and locally tested Batches 60E, 60F-1, and 60G.

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
| Admin UI Polish | Complete / current local polish tested | Includes Batch 60C recovery, Batch 60E Contact Us split tables, Batch 60F-1 dashboard Quick Actions, and Batch 60G login status polish |
| Admin Auth | Complete for current demo scope | Cognito JWT protection and Admin/Standard groups are implemented; Batch 60G refines login status presentation without changing auth security |
| Media Upload | Complete for approved scope | Private S3 upload/display is implemented for Products, Brands, Project Gallery, and Contact Person images |
| Launch Data Templates / Import | Complete for Phase 8 | Excel/CSV templates and safe dry-run-first import loader are implemented |
| Regression Testing | Complete for Phase 8 | Full public/admin regression checklist and script passed in current testing |
| EC2 Demo Deployment | Complete for prior demo release; current sync pending | Existing release-folder deployment path is proven. The consolidated current local version still needs confirmed GitHub push and EC2 deploy/smoke. |
| SEO / Domain Launch | Deferred | SEO, canonical URLs, sitemap/robots, Route 53, ACM, CloudFront, and HTTPS wait for the final approved domain |

## Current Authoritative Updates

1. **The current local `main` baseline includes the recovered Batch 60C changes and locally tested Batches 60E, 60F-1, and 60G.**
2. **Contact Us remains one consolidated DynamoDB table.** Batch 60E changes only the admin presentation into three type-specific tables and removes non-applicable display columns.
3. **Dashboard Quick Actions use one desktop row.** Batch 60F-1 provides three equal add actions with boxed `+` emphasis and mobile one-column fallback.
4. **The emphasized login status area is error-only.** Normal email/password guidance remains in the smaller information note, now slightly larger; friendly non-technical errors remain required.
5. **Cognito, DynamoDB, EC2, Nginx, and private S3 media are implemented for the current demo scope.**
6. **Mock mode remains useful for safe development, but current local validation of real project data should use DynamoDB and S3 media mode through the local proxy.**
7. **GitHub push and EC2 deployment of the consolidated current local version remain pending confirmation at this checkpoint.**
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
- Category-scoped homepage placement uses `show_pack_flag`: Packages/Kits = Promote Package; non-package products = Featured Product for the homepage Featured Products card.
- Contact Us content is consolidated into `rsa_contact_us`.
- Customer matching at launch uses contact number GSI only.
- Product category and brand filtering are optimized with two product GSIs.
- CMS content for About Us, Project Gallery, Services, and Contact Us will become API/database-driven while preserving the current public page layouts.

See [PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md](./PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md) for the approved implementation plan.


## Phase 8 Current Implemented Baseline

As of 2026-07-22, Phase 8 includes the deployed backend/admin/CMS/Mini-CRM foundation plus the current locally tested Batch 60C recovery and Batches 60E, 60F-1, and 60G polish.

Implemented baseline:

- FastAPI backend with public and protected admin route modules.
- Mock repository mode for safe development and DynamoDB repository mode for current AWS-backed data.
- Approved `rsa_` DynamoDB tables created and verified ACTIVE in `ap-southeast-1`.
- Public website pages connected to backend APIs.
- Public booking and inquiry submissions connected to backend APIs.
- Cognito-protected admin dashboard, lead management, catalog management, CMS management, and Settings > Users.
- Private S3 media upload/display for the approved admin media scope.
- Excel/CSV launch templates and safe import loader.
- EC2/Nginx release-folder deployment and rollback model.
- Batch 60E type-specific Contact Us admin tables using the consolidated Contact Us API/data model.
- Batch 60F-1 one-row dashboard Quick Actions with boxed add indicators.
- Batch 60G login error-only emphasized status behavior.
- Full public/admin regression and demo-readiness procedures.

Still outside the completed launch baseline:

- Confirmed GitHub push and EC2 deployment/smoke of the current consolidated local version.
- Batch 62A tagged release artifact / GitHub runtime decoupling.
- Final customer domain, Route 53, ACM, CloudFront, and HTTPS.
- Domain-dependent SEO metadata, canonical/Open Graph URLs, sitemap.xml, and robots.txt.
- Final launch/cutover approval and checklist.
