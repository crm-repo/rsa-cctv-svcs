# RSA CMS / Mini-CRM Project Overview

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
- Product types
- Promotions
- Package banners
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

`feature-status.md` is the authoritative implementation tracker. The summary below reflects the latest known state.

| Area | Latest Status | Notes |
|---|---|---|
| Homepage | Complete for current phase | Do not reopen unless specifically requested |
| Products Page | Established static catalog foundation | Master reusable catalog implementation |
| Promotions Page | Complete for current phase | Sale remains a hard filter; All Products resets category while keeping Sale active |
| Brands Page | Complete for current phase | Brand strip and hero polish are considered done unless reopened |
| About Us Page | Current active work area | Next public page to implement/polish |
| Services Page | Planned / partial | Public page still requires final implementation status confirmation |
| Contact Us Page | Planned | Public page and contact workflow still needed |
| Booking Page | Planned | Required for Request Site Visit workflow |
| Backend / Admin / CRM | Planned | Not yet implemented |
| SEO / Deployment | Planned | Required before production launch |

## Current Authoritative Updates

1. **Promotions All Products behavior has changed.** Older documentation stated that All Products redirects to Products. The latest rule is that All Products clears category filtering while keeping Sale active.
2. **Homepage, Promotions, and Brands are complete for the current phase.** They should not be reopened unless explicitly requested.
3. **About Us is the current active work area.**
4. **Brands hero logo cards should not be fully transparent.** Black logo text becomes unreadable on the dark hero background.
5. **Brands page active brand styling must override Products page pseudo-element styling.**
6. **Feature status, architecture, and requirements authorities are separated.** Use `feature-status.md` for status, `architecture.md` for technical design, and `requirements.md` for business requirements.

## Documentation Map

| Document | Purpose |
|---|---|
| [architecture.md](./architecture.md) | Authoritative technical design reference |
| [requirements.md](./requirements.md) | Authoritative business and functional requirements specification |
| [feature-status.md](./feature-status.md) | Authoritative implementation progress tracker |
| [open-issues.md](./open-issues.md) | Risks, blockers, technical debt, unresolved decisions, dependencies |
| [implementation-guidelines.md](./implementation-guidelines.md) | Development, coding, testing, and AI-agent implementation guidance |
| [decision-log.md](./decision-log.md) | Significant project decisions and rationale |
