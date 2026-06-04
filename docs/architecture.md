# RSA CMS / Mini-CRM Architecture

## Authority

This document is the authoritative technical design reference for RSA CMS / Mini-CRM. For implementation progress, use [feature-status.md](./feature-status.md). For business requirements, use [requirements.md](./requirements.md).

## Architecture Overview

RSA CMS / Mini-CRM uses a phased architecture.

The current phase is a static frontend built with:

- HTML
- Tailwind CSS
- Custom CSS
- JavaScript

The future architecture introduces:

- Python FastAPI backend
- AWS DynamoDB database
- AWS Cognito authentication
- AWS S3 image storage
- AWS CloudFront CDN and HTTPS
- AWS EC2 backend hosting
- Admin CMS
- Mini-CRM workflows

The system must support a transition from static product markup to a shared data source and later to API/database-driven rendering.

All backend, database, authentication, storage and deployment decisions are constrained by the AWS Free-Tier-first project rule: the completed project should fit within AWS Free Tier as much as practical during the first 12 months, with Route 53/domain as the expected paid exception, and then continue as a low-cost AWS deployment after the free-tier window.

## Technology Stack

| Layer | Technology | Status |
|---|---|---|
| Frontend | HTML, Tailwind CSS, custom CSS, JavaScript | Current |
| Backend API | Python FastAPI | Planned |
| Database | AWS DynamoDB | Planned |
| Authentication | AWS Cognito | Planned |
| Image/File Storage | AWS S3 | Planned |
| CDN / HTTPS | AWS CloudFront | Planned |
| Backend Hosting | AWS EC2 | Planned |
| Admin UI | Custom admin interface | Planned |

## Infrastructure Design

### AWS Services

| Service | Purpose |
|---|---|
| EC2 | Run FastAPI backend, admin APIs, business logic, and auth validation |
| DynamoDB | Store CMS and CRM data |
| S3 | Store product, brand, service, promotion, gallery, and banner images |
| Cognito | Admin login, user authentication, JWT token handling |
| CloudFront | CDN, HTTPS, and public asset acceleration |

### Suggested S3 Buckets

```text
cctv-site-assets
cctv-product-images
cctv-project-gallery
```

### Backend Hosting

Free-Tier-first starting target:

```text
One AWS Free-Tier-eligible EC2 micro instance only
```

The exact instance family must be confirmed in the selected AWS account and Region before launch. The project should not use multiple always-on EC2 instances for the first-year deployment unless explicitly approved.


### AWS Free-Tier-First Deployment Constraint

RSA CMS / Mini-CRM was designed from the beginning as an AWS Free-Tier-first project.

First 12 months target:

- Keep the completed public website, backend, admin CMS, Mini-CRM, database, authentication and image storage within AWS Free Tier as much as practical.
- Treat Route 53/domain cost as the expected paid exception once the project is ready for domain-based deployment.
- Before Route 53/domain setup, test and demonstrate the project using the EC2 public IP or other free AWS-provided endpoints.
- Keep the post-free-tier architecture low-cost and simple.

Required cost guardrails:

- Use one Free-Tier-eligible EC2 micro instance for FastAPI/admin APIs.
- Use DynamoDB with low provisioned capacity for the first deployment.
- Store images and uploads in S3, but compress and cap uploaded assets.
- Use Cognito for admin authentication only; avoid public user signup unless approved.
- Disable SMS MFA, phone verification and SMS notifications where possible.
- Booking and inquiry requests only need to be stored and visible in the admin panel; automatic SMS/email notifications are not required for launch.
- Avoid Application Load Balancer, NAT Gateway, RDS, multiple always-on EC2 instances, global tables, unnecessary paid monitoring and large media storage unless explicitly approved.
- Configure AWS Budgets/billing alerts before deployment.

Forbidden by default for first-year Free-Tier-first deployment:

```text
Application Load Balancer
NAT Gateway
RDS
Multiple always-on EC2 instances
SMS workflows
Large video storage
Unnecessary paid notification services
Excessive CloudWatch log retention
```

## Frontend Architecture

### Current Frontend Structure

```text
frontend/
├── index.html
├── about.html
├── products.html
├── promotions.html
├── brands.html
├── services.html
├── contact-us.html
├── booking.html
├── admin/
│   ├── dashboard.html
│   ├── products.html
│   ├── customers.html
│   ├── bookings.html
│   ├── inquiries.html
│   ├── promotions.html
│   ├── contents.html
│   └── settings.html
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── icons/
└── components/
```

### Frontend Component Patterns

Core reusable patterns:

- Header and navigation
- Mobile menu overlay
- Hero sections
- Feature strips
- Soft cards
- Package banners
- Product catalog cards
- Product quick view modal
- Category filter strip
- Brand strip
- Search input
- Sort dropdown
- Pagination
- Empty result state
- CTA section
- Footer

### Shared Catalog Architecture

The Products page is the master catalog pattern.

| Page | Catalog Role | Special Rule |
|---|---|---|
| Products | Full product catalog | Category, brand, search, sort, pagination |
| Promotions | Sale-only catalog based on Products architecture | Sale hard filter is always active |
| Brands | Brand-first catalog based on Products architecture | Brand is primary filter; category is secondary |

### Frontend Data Attributes

Current static product cards use HTML data attributes as a bridge to future dynamic data.

Important attributes include:

- `data-category`
- `data-product-brand-name`
- `data-product-name`
- `data-product-model`
- `data-product-category`
- `data-product-price`
- `data-product-old-price`
- `data-product-image`
- `data-product-brand`
- `data-product-stock`
- `data-product-low-quantity`
- `data-product-features`

Future API/database integration should preserve equivalent data fields.

## Backend Architecture

### Planned Backend Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth/
│   ├── routes/
│   │   ├── products.py
│   │   ├── promotions.py
│   │   ├── customers.py
│   │   ├── bookings.py
│   │   ├── inquiries.py
│   │   ├── contact_us.py
│   │   ├── services.py
│   │   └── settings.py
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── middleware/
├── requirements.txt
└── .env
```

### Backend Responsibilities

The backend will handle:

- Product data
- Brand data
- Category data
- Product type data
- Promotions
- Package banners
- Customers
- Bookings
- Inquiries
- Services
- About Us content
- Project gallery content
- Contact company details
- Contact persons
- Social media links
- Settings
- Admin authentication
- User roles and permissions
- Audit logs

## Authentication and Authorization

### Authentication

Planned authentication provider:

```text
AWS Cognito
```

Cognito will support:

- Admin login
- JWT token authentication
- Protected backend routes

### Authorization

Future roles:

| Role | Access Summary |
|---|---|
| Super Admin | Full access including users and audit logs |
| Admin | Full operational access except user management |
| Sales Staff | Manage bookings and inquiries; view catalog/content |
| Marketing Staff | Edit content, brands, and services; view bookings/inquiries |

Authorization must be enforced server-side on protected admin routes.

## Database Design

### Database Technology

Planned database:

```text
AWS DynamoDB
```

### DynamoDB Modeling Constraint

The field lists in this document are backend-ready logical models. Before implementation, DynamoDB keys and indexes must be designed around actual access patterns. Do not blindly implement a relational-style schema without reviewing query patterns.

For the Free-Tier-first deployment, DynamoDB should start with provisioned capacity at the lowest practical RCU/WCU settings. Add GSIs only when required by a real admin/public access pattern. Avoid on-demand mode, global tables, streams, point-in-time recovery and unnecessary indexes during the first deployment unless explicitly approved after cost review.

### Approved Table Set

| Table | Purpose |
|---|---|
| products | Product and package catalog records |
| brands | Brand records and logos |
| categories | Product category records |
| product_types | Product type records |
| promotions | Promotional records |
| customers | CRM customer records |
| bookings | Booking / Request Site Visit records |
| inquiries | Product/package inquiry records |
| about | About Us content |
| projects | Project gallery content |
| contact_company | Company contact details |
| contact_persons | Contact persons and sales staff |
| social_media | Social media links |
| services | Service content |
| settings | Site-wide settings |

Total planned tables:

```text
15
```

## Universal Visibility Rule

```text
show_flag = Y → visible on public website
show_flag = N → hidden from public website
```

`show_flag` is different from `status`.

- `show_flag` controls public visibility.
- `status` controls internal workflow state.

Example statuses:

- New
- Contacted
- Scheduled
- Completed
- Cancelled
- Active
- Disabled
- Archived

## Logical Data Model Summary

### Products

| Field | Purpose |
|---|---|
| product_id | Primary identifier |
| show_flag | Public visibility |
| display_order | Manual ordering |
| product_name | Public display name |
| product_model | Model/SKU |
| product_slug | Future SEO/detail page slug |
| category | Main category such as `cctv`, `recorders`, `packages` |
| subcategory | Human-readable product type |
| brand_id | Reference to brand |
| product_brand_name | Brand filter key |
| description | Long description |
| features | Product features or pipe-delimited static field |
| price | Base/current price |
| old_price | Original price for sale comparison |
| sale_price | Sale price where applicable |
| image_path | Product or package image |
| brand_logo_path | Brand logo path when not joined |
| stock_quantity | Stock count |
| low_stock_threshold | Low stock threshold |
| meta_title | SEO metadata |
| meta_description | SEO metadata |
| created_at / updated_at | Audit timestamps |
| created_by / updated_by | Admin audit fields |

### Brands

| Field | Purpose |
|---|---|
| brand_id | Primary identifier |
| show_flag | Public visibility |
| display_order | Manual ordering |
| brand_name | Display name |
| brand_key | Filter key |
| logo_path | Logo asset |
| description | Future brand content |
| website_url | Optional external link |
| featured_brand | Flag for homepage/hero/brand previews |
| created_at / updated_at | Audit timestamps |

### Package Banners

| Field | Purpose |
|---|---|
| package_banner_id | Primary identifier |
| show_flag | Public visibility |
| display_order | Manual ordering |
| product_id | Optional linked package product |
| banner_image_path | Square package banner image |
| homepage_visible | Homepage placement flag |
| promotions_hero_visible | Promotions hero placement flag |
| created_at / updated_at | Audit timestamps |

### Customers

| Field | Purpose |
|---|---|
| customer_id | Primary identifier |
| customer_name | Customer display name |
| customer_status | Active, Prospect, Inactive |
| customer_category | Residential or Commercial |
| email_address | Email |
| contact_number | Phone/contact number |
| customer_from | Inquiries, Booking Request, Social Media, Referral, etc. |
| sales_person | Assigned sales/contact person |
| repeat_customer | Yes/No repeat customer flag |
| created_at / updated_at | Audit timestamps |

### Bookings

| Field | Purpose |
|---|---|
| booking_id | Primary identifier |
| customer_id | Linked customer |
| customer_name | Submitted name |
| contact_number | Phone/contact number |
| email | Optional email |
| address | Service address/location |
| preferred_date | Preferred date |
| preferred_time | Preferred time |
| service_interest | CCTV install, maintenance, repair, package, etc. |
| booking_type | Repair, Site Visit Request, Installation, Maintenance, Warranty Repair, Others |
| assigned_person | Assigned staff/contact person |
| comments | Admin comments |
| notes | Customer notes |
| status | New, Contacted, Scheduled, Completed, Cancelled |
| created_at / updated_at | Audit timestamps |

### Inquiries

| Field | Purpose |
|---|---|
| inquiry_id | Primary identifier |
| customer_id | Linked customer |
| product_id | Optional linked product/package |
| customer_name | Submitted name |
| contact_number | Phone/contact number |
| email | Optional email |
| subject | Inquiry subject |
| message | Message body |
| source_page | Products, Promotions, Homepage, etc. |
| assigned_person | Assigned staff/contact person |
| status | New, Replied, Closed |
| created_at | Audit timestamp |

## API Architecture

### Public API Endpoints

```text
GET  /api/products
GET  /api/products/{id}
GET  /api/brands
GET  /api/package-banners
POST /api/bookings
POST /api/inquiries
```

### Admin API Endpoints

```text
POST   /api/admin/products
PUT    /api/admin/products/{id}
DELETE /api/admin/products/{id}

POST   /api/admin/brands
PUT    /api/admin/brands/{id}
DELETE /api/admin/brands/{id}

GET    /api/bookings
PUT    /api/bookings/{id}

GET    /api/inquiries
PUT    /api/inquiries/{id}
```

### Product Query Parameters

`GET /api/products` should support:

- category
- brand
- sale
- search
- sort
- page
- per_page

### Public Endpoint Visibility Rule

Public endpoints must return only records with:

```text
show_flag = Y
```

## Storage Architecture

Images should be stored in S3 and delivered through CloudFront.

Image types:

- Product images
- Brand logos
- Package banners
- Promotion images
- Service images
- Project gallery images
- Site banners
- Icons and static marketing assets

## Deployment Architecture

Planned Free-Tier-first deployment flow:

1. Static frontend hosted through the simplest free-tier-compatible path for the current stage.
2. FastAPI backend and admin APIs deployed to one Free-Tier-eligible EC2 micro instance.
3. Backend connects to DynamoDB using low provisioned capacity and minimal indexes.
4. Admin authentication handled by Cognito with SMS disabled where possible.
5. Images uploaded to S3 with compression and upload-size limits.
6. CloudFront and ACM may be used for CDN/HTTPS where applicable and free-tier-compatible.
7. Test and demo through EC2 public IP or free AWS-provided endpoint before Route 53/domain setup.
8. Configure Route 53/domain only when the project is ready for domain-based launch; Route 53/domain is the expected paid exception.
9. Configure billing alerts before public testing.

## Design Decisions and Rationale

| Decision | Rationale |
|---|---|
| Lead-generation instead of ecommerce | CCTV installation requires consultation, site visit, and quotation |
| Static frontend first | Allows fast UI iteration before backend/admin complexity |
| Products architecture reused by Promotions and Brands | Reduces duplicate logic and keeps UX consistent |
| Packages use `category = packages` | Avoids unnecessary `is_package` field |
| `show_flag` controls public visibility | Simple and consistent CMS behavior |
| Promotions always keeps Sale active | Promotions page must never show non-sale products |
| Brands page uses brand-first browsing | Provides a distinct browsing path from Products |
| Brand strip two-row threshold is 16+ brands | Matches category strip behavior |
| Hero logo cards are not transparent | Black logo text becomes unreadable on dark background |
| AWS Free-Tier-first deployment | Keeps first 12 months within Free Tier as much as practical, with Route 53/domain as the expected paid exception |
| Booking/inquiry admin-panel-only notifications | Avoids SMS/email notification cost while still capturing leads in the admin panel |

## Technical Constraints

1. Current frontend is static HTML/CSS/JS.
2. Shared CSS classes affect Products, Promotions, and Brands.
3. Page-specific overrides are safer than global CSS changes.
4. Products and Promotions currently duplicate product markup.
5. DynamoDB keys/indexes must be designed around access patterns.
6. Mobile and tablet responsive rules require device-specific handling.
7. Image optimization is required for production performance.
8. AWS Free-Tier-first cost guardrails must be preserved during backend, admin and deployment implementation.
9. Route 53/domain is the expected paid exception after IP-based testing/demo.
10. Notification workflows must be treated as optional and disabled by default for first-year cost control.
