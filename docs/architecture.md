# RSA CMS / Mini-CRM Architecture

## Authority

This document is the authoritative technical design reference for RSA CMS / Mini-CRM. For implementation progress, use [feature-status.md](./feature-status.md). For business requirements, use [requirements.md](./requirements.md).


## Current Phase 8 Continuation Architecture — Through Batch 56D

As of Batch 56D, the working architecture has moved beyond the Batch 29 local-only baseline:

- Public frontend remains static HTML/CSS/JavaScript, but major public sections are now API-rendered.
- Public Products, Promotions, Brands, Homepage, About, Services, Contact, and Booking pages are API-backed where implemented.
- FastAPI backend is deployed to a single Free-Tier-first EC2 demo instance using systemd.
- Nginx fronts the public site on port 80 and proxies only approved public/API/media/admin routes.
- Admin pages and admin/CRM APIs are protected through Cognito JWT bearer-token auth.
- DynamoDB mode is the active deployed backend data source; mock mode remains useful for safe local/default development only where explicitly configured.
- Private S3 media storage is enabled for uploaded media, with backend `/api/media/...` display/proxy routes.
- Admin media upload integration writes resolved `/api/media/...` paths for Products, Brands, Project Gallery, and Contact Person images.
- Products/Brands static image records were backfilled to S3; Project Gallery and Contact Person backfill were intentionally left for manual handling.
- Promotions hero uses promoted package products only (`show_flag=Y`, `show_pack_flag=Y`, package/kits category).
- Brands hero is already dynamic through the public brands API and must not be overwritten by duplicate renderers.

### EC2/Nginx deployment notes from Batch 56B

The EC2 Nginx config must preserve both media fixes:

```text
location ^~ /api/media/ ...
client_max_body_size 8m;
```

The media route must appear before any default `/api/` deny/403 rule so public media can display while admin/CRM APIs remain protected.

### Cognito role-management direction

Cognito remains the launch source of truth for admin login accounts. The planned authorization model uses Cognito Groups:

```text
Admin
Standard
```

The browser must not call Cognito admin APIs directly. Settings > Users should call protected FastAPI routes; FastAPI performs Cognito admin API operations server-side with IAM permissions.

No `rsa_admin_users` DynamoDB table is required for launch unless later profile metadata/audit requirements are added.

Batch 59A user onboarding uses suppressed Cognito invitation email and a backend-generated temporary password shown once only after create/reset. Temporary passwords are not stored, logged, or re-viewable. First-login password change must be handled in the browser. User create/view/edit fields use First Name and Last Name (`given_name`, `family_name`); the main Users table shows generated Full Name.

### Planned domain/HTTPS architecture — Batch 61

After customer demo/launch approval and final domain confirmation, the approved HTTPS architecture is:

```text
Visitor browser
  -> HTTPS
Route 53 DNS
  -> alias record
CloudFront distribution + ACM certificate
  -> EC2 Nginx origin / FastAPI backend
```

Batch 61 is deferred until the domain is known. The current EC2 public-IP HTTP demo remains the active demo setup until then. Route 53/domain is the approved paid exception. Avoid ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, and unnecessary paid services by default.

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




## Current Phase 8 Implemented Architecture Baseline

As of Batch 29, the current local/regression architecture includes:

- Static public frontend pages served locally or through static hosting.
- JavaScript API clients/renderers connecting public pages to backend APIs.
- Python FastAPI backend with public and admin route modules.
- Repository abstraction supporting mock mode and DynamoDB mode.
- Mock repository mode as the safe default.
- DynamoDB repository mode for AWS-backed regression/import testing.
- AWS DynamoDB tables created in `ap-southeast-1` following the approved Phase 8 Final v5 plan.
- Admin dashboard, lead management, catalog management, CMS management, auth prep, and media prep.
- Excel/CSV launch templates and safe dry-run-first import tooling.

Still planned for production/external use:

- EC2 public-IP backend/admin deployment.
- Real Cognito JWT enforcement for admin routes.
- Real S3 binary upload/storage is now implemented for the current media scope; image optimization/backfill cleanup remains ongoing.
- CloudFront/SSL/domain.
- Billing alerts and Free-Tier deployment review.
- SEO, sitemap, robots, image optimization, and launch hardening.

## Phase 8 Final v5 Backend/Data Plan

The approved Phase 8 DynamoDB/API implementation plan is documented in [PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md](./PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md).

This plan supersedes older backend table assumptions in this document where they conflict.

Approved launch summary:

- Use `rsa_` table prefix.
- Use simple multi-table DynamoDB design.
- Launch with 12 DynamoDB tables and 5 GSIs.
- Store package products in `rsa_products`; do not create `rsa_package_banners`.
- Use `show_flag` for normal public visibility.
- Use `show_pack_flag` only for package homepage/promo hero placement.
- Use `display_seq` instead of `display_order`.
- Use category-based product IDs with four-letter prefixes.
- Use `rsa_id_counters` for backend-generated sequential IDs.
- Store category and brand snapshot fields on products for faster public API responses.
- Use `sale_price` to determine sale status; do not create `old_price` or sale boolean fields.
- Use `rsa_categories.icon_code` for Font Awesome category button icons.
- Use `rsa_key_features` for reusable product feature suggestions.
- Consolidate Contact Us into `rsa_contact_us` with `contact_type` values: `Company Contact`, `Contact Person`, and `Social Media`.
- Keep `rsa_product_types` deferred and not for launch.

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

Simplified launch capacity count:

```text
12 tables + 5 GSIs = 17 RCU + 17 WCU minimum simplified count
```

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
- Package/package hero display sourced from `rsa_products`
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
- Product type data (deferred; `rsa_product_types` not for launch)
- Promotions
- Package/package hero display sourced from `rsa_products`
- Customers
- Bookings
- Inquiries
- Services
- About Us content
- Project gallery content
- Consolidated Contact Us records using `rsa_contact_us` and `contact_type`
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

### Approved Phase 8 v5 Launch Table Set

| Table | Purpose |
|---|---|
| `rsa_products` | Product catalog records, package products, and package hero/homepage source |
| `rsa_brands` | Brand records, brand keys, and logos |
| `rsa_categories` | Product categories, category prefixes, and category icon codes |
| `rsa_key_features` | Reusable product feature suggestions/autocomplete |
| `rsa_customers` | CRM customer records |
| `rsa_bookings` | Booking / Request Site Visit records |
| `rsa_inquiries` | Product/package inquiry records |
| `rsa_about` | About Us CMS content |
| `rsa_project_gallery` | Project gallery CMS content |
| `rsa_services` | Services CMS content |
| `rsa_contact_us` | Consolidated company contact, contact persons, and social media records |
| `rsa_id_counters` | Backend-generated sequential ID counters |

Deferred tables:

```text
rsa_product_types
rsa_promotions
rsa_settings
rsa_admin_users
rsa_roles
rsa_audit_logs
rsa_customer_contacts
rsa_customer_notes
```

Removed from launch design:

```text
rsa_package_banners
rsa_contact_company
rsa_contact_persons
rsa_social_media
```

Total launch tables:

```text
12
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
| product_id | Primary identifier; category-based ID such as `CCTV-0000001`, `RECO-0000001`, or `PACK-0000001` |
| show_flag | Normal public visibility for catalog, promotions grid, search/filter results, and package category listing |
| show_pack_flag | Additional package-only placement flag for homepage promo/package cards and promotions hero/highlight section |
| display_seq | Manual ordering; replaces `display_order` |
| product_name | Public display name; may default from brand + feature_01 + subcategory but remains editable |
| product_model | Model/SKU |
| product_slug | Future SEO/detail page slug |
| category_id | Source reference to `rsa_categories` |
| category_key | Category filtering snapshot |
| category_name | Category display snapshot |
| category_prefix | Product ID generation snapshot |
| subcategory | Human-readable product type/subcategory |
| brand_id | Source reference to `rsa_brands` |
| product_brand_key | Brand filter snapshot |
| product_brand_name | Brand display snapshot |
| brand_logo_path | Brand logo display snapshot |
| description | Manually managed product description |
| feature_01 ... feature_10 | Product feature bullets; minimum 3 required for admin product creation |
| price | Normal/original/base price |
| sale_price | Sale price when on sale; sale status is determined by presence of this value |
| image_path | Product or package image path/S3 key |
| stock_quantity | Stock count |
| low_stock_threshold | Low stock threshold |
| meta_title | SEO metadata |
| meta_description | SEO metadata |
| created_at / updated_at | Audit timestamps |
| created_by / updated_by | Admin audit fields |

Do not use `old_price`, `sale_flag`, `is_sale`, or `on_sale` database fields.

### Categories

| Field | Purpose |
|---|---|
| category_id | Primary identifier |
| show_flag | Public/admin visibility |
| display_seq | Manual ordering |
| category_name | Display name |
| category_key | Filter/API key |
| category_prefix | Four-letter product ID prefix |
| icon_code | Font Awesome icon code for category buttons |
| description | Optional description |
| created_at / updated_at | Audit timestamps |
| created_by / updated_by | Admin audit fields |

### Key Features

| Field | Purpose |
|---|---|
| key_feat_id | Primary identifier |
| key_feat_name | Reusable feature text for product feature autocomplete/dropdown |
| created_at / updated_at | Audit timestamps |
| created_by / updated_by | Admin audit fields |

### Brands

| Field | Purpose |
|---|---|
| brand_id | Primary identifier |
| show_flag | Public visibility |
| display_seq | Manual ordering |
| brand_name | Display name |
| brand_key | Filter key |
| logo_path | Logo asset |
| description | Future brand content |
| website_url | Optional external link |
| featured_brand | Flag for homepage/hero/brand previews |
| created_at / updated_at | Audit timestamps |

### Package Products

Packages are stored in `rsa_products` using:

```text
category_key = packages
```

`GET /api/package-banners` reads from `rsa_products` and filters:

```text
show_flag = Y
category_key = packages
show_pack_flag = Y
```

Recommended derived mapping:

```text
package_banner_id = product_id
product_id = product_id
banner_image_path = image_path
display_seq = display_seq
show_pack_flag = show_pack_flag
```

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


### Contact Us

`rsa_contact_us` consolidates Company Contact, Contact Person, and Social Media records in one table.

Shared fields:

| Field | Purpose |
|---|---|
| contact_us_id | Primary identifier; may use CONT, CPER, or SOCM prefix |
| show_flag | Public/admin visibility |
| contact_type | `Company Contact`, `Contact Person`, or `Social Media` |
| display_seq | Manual ordering |
| created_at / updated_at | Audit timestamps |
| created_by / updated_by | Admin audit fields |

Company Contact fields:

```text
primary_contact_number
secondary_contact_number
company_email
company_address
showroom_address
whatsapp_number
viber_number
business_hours
office_map_embed_url
office_map_link_url
showroom_map_embed_url
showroom_map_link_url
```

Contact Person fields:

```text
person_image_path
person_name
position_title
department
phone_number
email_address
```

Social Media fields:

```text
platform_name
platform_key
profile_url
icon_code
```

Use fixed/default Company Contact record `CONT-0000001`. No `contact_type` GSI is required for launch.

### Launch GSI Summary

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


## API Architecture

### Public API Endpoints

```text
GET  /api/products
GET  /api/products/{id}
GET  /api/brands
GET  /api/categories
GET  /api/key-features
GET  /api/package-banners
GET  /api/pages/about
GET  /api/pages/contact
GET  /api/pages/services
GET  /api/about
GET  /api/project-gallery
GET  /api/services
GET  /api/contact
GET  /api/contact-persons
GET  /api/social-media
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
- Package/package hero display sourced from `rsa_products`
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
