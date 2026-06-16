# RSA CMS / Mini-CRM Requirements

## Authority

This document is the authoritative business, functional, and non-functional requirements specification for RSA CMS / Mini-CRM. For implementation progress, use [feature-status.md](./feature-status.md). For technical design, use [architecture.md](./architecture.md).


## Phase 8 Continuation Requirements — Batches 56D to 60

### Promotions hero promoted package rule

The Promotions hero must show only package/kits products that meet all of these conditions:

```text
show_flag = Y
show_pack_flag = Y
category/category_key indicates Packages/Kits
```

Brands hero must remain dynamic from the Brands API and must not be patched by duplicate frontend renderers.

### Media upload/display requirements

- Admin media fields should use Browse/Choose File controls, not manual path typing.
- Approved media upload fields include Products, Brands, Project Gallery, and Contact Person images.
- Company Contact and Social Media records should not receive image/photo upload fields unless explicitly reopened.
- Uploaded media should store resolved `/api/media/...` paths and remain displayable through the backend media route.
- The S3 bucket remains private; public display is through the backend/Nginx media route, not public bucket access.
- Upload size should remain bounded for Free-Tier-first operation.

### Admin user/role requirements

- Use Cognito Groups for role/authorization: `Admin` and `Standard`.
- Do not use the Cognito `profile` attribute as a role field.
- Do not create a DynamoDB users table for launch user management.
- Settings > Users should read/manage Cognito users through protected FastAPI backend routes only.
- Admin users may view/add/update/enable/disable Cognito users and manage Admin/Standard group assignment.
- Standard users must not see Settings and must be blocked by backend authorization from user-management routes.

### Delete/restricted-action requirements

- Delete controls are Admin-only for record types where delete is approved.
- Standard users must not see delete controls and backend delete endpoints must still return 403 if called.
- Leads must not expose delete controls even for Admin. Keep booking, inquiry, and customer/lead records for traceability.
- Prefer hide/archive/disable where data relationships or operational traceability matter.
- Existing category/subcategory/brand dependency protections remain required.

### SEO/domain requirements

- Batch 57 SEO metadata/page titles, canonical URLs, Open Graph URLs, sitemap.xml, and robots.txt are deferred until Route 53/final domain is ready.
- Do not set EC2 public IP as canonical URL.

## Functional Requirements

## Approved Phase 8 Backend/CMS Requirements

The approved Phase 8 backend/CMS requirements are documented in [PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md](./PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md). These requirements supersede older package-banner/contact-table assumptions where they conflict.

### Product and Package Requirements

- Products and package products must be stored in `rsa_products`.
- Package products are products where `category_key = packages`.
- `show_flag` controls normal public visibility in product catalog, promotions grid, search/filter results, and package category listing.
- `show_pack_flag` controls homepage package cards and promotions package hero/highlight placement only.
- `show_flag = N` must prevent public display even when `show_pack_flag = Y`.
- Use `display_seq` for ordering.
- Product IDs must be category-based using the category prefix, such as `CCTV-0000001`, `RECO-0000001`, and `PACK-0000001`.
- `old_price` must not be used. `price` is the normal/original/base price. `sale_price` determines sale status.
- Product name may default from `product_brand_name + feature_01 + subcategory`, but it must remain editable before saving.
- Product description must remain manually managed and must not be auto-generated from the product name defaulting rule.
- No `auto_name_flag` field is required.

### Product Category Requirements

- Categories must be stored in `rsa_categories`.
- Categories must include `category_prefix` for product ID generation.
- Categories must include `icon_code` to store Font Awesome category button icons.
- The admin UI can use a normal text input for `icon_code`; a full icon picker is not required for launch.

### Product Feature Requirements

- Product features are stored on products as `feature_01` through `feature_10`.
- At least 3 features are required when creating a product.
- Empty/null feature fields must not display publicly.
- Reusable feature suggestions must be stored in `rsa_key_features`.

### Contact Us Requirements

- Contact Us data must be stored in one consolidated table: `rsa_contact_us`.
- The admin page may still show 3 separate sections: Company Contact, Contact Person, and Social Media.
- The table must use `contact_type` with values `Company Contact`, `Contact Person`, and `Social Media`.
- Company Contact should use fixed/default record `CONT-0000001`.
- Company Contact fields must include office address and showroom address, plus separate office/showroom map embed/link fields.
- Social Media records must use `icon_code` for Font Awesome icon code.

### Public Page API Requirements

Grouped page APIs are approved:

```text
GET /api/pages/about
GET /api/pages/contact
GET /api/pages/services
```

Individual public CMS APIs are also approved for reusable modules:

```text
GET /api/about
GET /api/project-gallery
GET /api/services
GET /api/contact
GET /api/contact-persons
GET /api/social-media
```


## Public Website Requirements

The public website must provide:

1. Homepage
2. Products page
3. Promotions page
4. Brands page
5. About Us page
6. Services page
7. Contact Us page
8. Booking / Request Site Visit page

The public website must prioritize lead generation, not ecommerce checkout.

## Homepage Requirements

### Final Homepage Order

The homepage must display sections in this order:

1. Hero
2. Feature Strip
3. R.S.A. Recommended CCTV Packages
4. Featured Products
5. Products on Sale
6. About Us / Top Brands / Why Choose Us
7. Services Preview
8. Final CTA
9. Footer

### Recommended Packages

- Must appear above Featured Products.
- Must show three square package banners for launch.
- View All must navigate to Promotions.
- Static visually for the current frontend phase.
- Future backend source uses `rsa_products` with `category_key = packages`; `show_flag` controls normal catalog/promotions visibility and `show_pack_flag` controls homepage/package hero placement.

### Featured Products

- Must use dot paging.
- Must remain inside one large preview card.
- Must not use separate floating individual card containers.

### Products on Sale

- Must use dot paging.
- Must display sale products.
- Must replace older “Promotions Preview” naming.

### Top Brands

- Must use dot paging.
- Must show six brands per page.
- Must use a two-column by three-row layout.
- Future source should be `featured_brand = Y`.

## Products Page Requirements

The Products page must support:

- Product hero section
- Breadcrumb and search row
- Category filter strip
- Brand strip
- Product count
- Sort dropdown
- Product grid
- Pagination
- Empty state
- Product quick view modal

### Product Categories

Approved categories:

- All Products
- Sale
- Packages/Kits
- CCTV Cameras
- Recorders
- Networking
- Accessories
- Power Supply
- Storage

### Product Brand Filter

- Clicking a brand applies a filter.
- Clicking the active brand again clears the brand filter.
- Brand filtering combines with category, search, sort, and pagination.

### Product Search

Search must check:

- Product name
- Product model
- Category
- Subcategory
- Features

### Product Sorting

Sort options:

- Default
- Price Low to High
- Price High to Low
- Newly Added
- On Sale

Sorting must physically reorder DOM cards after sorting.

### Product Pagination

Pagination must:

- Update after filters/search/sorting.
- Update product count.
- Reset to page 1 after filter/search changes.
- Show correct page buttons.

## Promotions Page Requirements

The Promotions page must reuse Products page catalog architecture.

### Promotions Sale Rule

Sale is always active on Promotions.

Sale cannot be removed.

### Promotions Filtering

- Categories filter within sale-only results.
- Brands filter within sale-only results.
- Search operates within sale-only results.
- Sorting operates within sale-only results.
- Packages/Kits shows sale packages and promotional packages.

### Promotions All Products Rule

Latest authoritative behavior:

- All Products clears category filtering.
- Sale remains active.
- The page shows all sale products.

Superseded behavior:

- All Products redirecting to Products page is no longer the current requirement.

## Brands Page Requirements

The Brands page must support brand-first product browsing.

### Brands Hero

The Brands hero must contain:

- Trusted CCTV/security headline
- Supporting copy
- Feature icons
- Logo wall/grid

Hero feature items:

- Genuine Products
- Reliable Warranty
- Proven Performance

### Brands Hero Logo Grid

The hero logo grid must:

- Display 12 featured brands.
- Future source: `featured_brand = Y`.
- Sort alphabetically.
- Use the same featured brands as homepage/product/promotions brand displays.

### Brands Hero Logo Background

Do not use fully transparent hero logo cards because black logo text becomes unreadable.

Candidate background colors:

```css
#d1d5db
#cbd5e1
#bfc7d1
```

### Brands Brand Strip

The brand strip must:

- Appear as the first major body element after hero/breadcrumb/search area.
- Use title “Explore Our Brands.”
- Be horizontally scrollable.
- Support drag-to-scroll.
- Support swipe on mobile.
- Show hover arrows.
- Avoid image drag behavior.

### Brands Brand Count Rule

| Brand Count | Layout |
|---|---|
| 1–15 | One row |
| 16+ | Two rows |

For odd brand counts, the top row gets one extra item.

Example:

```text
21 brands:
Row 1 = 11
Row 2 = 10
```

### Brands Filtering

- Brand is the primary filter.
- Category is secondary.
- Search and sorting respect selected brand/category.

Behavior:

```text
Selected brand + no category = all products under selected brand
Selected brand + selected category = products under both selected brand and category
```

Brands page category buttons should reuse Products category buttons but exclude:

- All Products
- Sale

## Services Requirements

The public Services area must communicate core services such as:

- CCTV installation
- CCTV maintenance
- Repair and troubleshooting

Homepage Services preview is complete for the current phase. The standalone Services page remains planned/partial unless separately completed.

## About Us Requirements

The About Us page is the current active work area.

Known About/Why Choose Us requirements:

- About Us / Why Choose Us card polish is complete on the homepage.
- The Learn More button should sit below Why Choose Us bullets and be centered.
- The applicable layout name is `about-why-grid`.
- The page should preserve company credibility, story, and trust-building content.

## Product Modal Requirements

The product modal must open from:

- Product image
- Product model
- Product name

The modal must display:

- Product image
- Brand logo
- Model
- Product name
- Category/subcategory
- Price
- Old price / sale comparison if applicable
- Sale/discount badge where applicable
- Stock status
- Key features

Modal close methods:

- X button
- Outside overlay click
- ESC key

Deferred modal enhancements:

- Image gallery
- Image zoom
- Full product details page
- Swipe-to-close mobile gesture

## Package Requirements

A package is a product with:

```text
category = packages
```

No separate `is_package` field is required for launch.

Package images use the normal product image field.

Homepage package banners are static visually for the current frontend phase.

Future backend/admin should manage package products through `rsa_products` using:

- `show_flag` for normal product catalog / promotions grid visibility
- `show_pack_flag` for homepage package cards and package hero/highlight placement
- `display_seq` for ordering
- `category_key = packages` for package records

Do not create a separate package banners table for launch.

### Package Banner Standard

Package banner artwork should use:

- Square 1:1 format
- Most Popular badge where applicable
- Centered package title
- Centered bundle image
- Circular stage/platform
- Feature badges
- Warranty strip
- Installation/training included strip

Package banners should not duplicate modal key features as long bullet lists inside the image.

## Admin CMS Requirements

Future admin must support:

- Dashboard
- Products
- Brands
- Categories
- Product Types
- Promotions
- Customers
- Bookings
- Inquiries
- About Us content
- Project Gallery
- Contact details
- Contact persons
- Social media links
- Services
- Settings
- User roles
- Audit logs

### Admin Menu Structure

```text
Dashboard
Products
  Add New Product
  All Products
  Featured Products
  Product Types
  Categories
  Brands
Promotions
Customers
  Add New Customer
  Customer List
Bookings
Inquiries
Contents
  About Us
    Company Story
    Project Gallery
  Contact Us
    Primary Contact Number
    Company Email
    Company Address
    Contact Persons
    Social Media Links
  Services
Settings
  Banner & Marketing Text
Logout
```

## CRM Requirements

Future CRM must support:

- Customers
- Contacts
- Notes
- Related bookings
- Booking status workflow
- Inquiry status workflow
- Customer source tracking
- Repeat customer flag
- Sales person assignment

### Customer Fields

- Customer Name
- Customer Status: Active, Prospect, Inactive
- Customer Category: Residential, Commercial
- Email Address
- Contact Number
- Customer From
- Customer Creation Date
- Sales Person
- Repeat Customer flag

### Customer Details Page

Customer details should show:

- Customer summary header
- Contacts
- Notes
- Related Bookings

## Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Pages should load quickly on desktop and mobile |
| Image Optimization | Images must be compressed and lazy loaded where practical |
| Security | Future forms must validate input and sanitize data |
| Authentication | Admin routes must be protected |
| Authorization | Admin actions must respect roles and permissions |
| Usability | Visitors should reach inquiry or booking within minimal clicks |
| Accessibility | Images require alt text; controls must be keyboard accessible |
| Maintainability | Reusable catalog, modal, filter, and card components are preferred |
| Scalability | Architecture must support API/database-driven product loading |
| SEO | Public pages need titles, meta descriptions, Open Graph tags, sitemap, and robots.txt |
| Cost Control | The completed project must follow the AWS Free-Tier-first rule for the first 12 months where practical |
| Deployment Cost | Route 53/domain is the expected paid exception; test/demo should use EC2 public IP or free AWS-provided endpoints before Route 53 |


## Cost and Deployment Requirements

### AWS Free-Tier-First Rule

The completed RSA CMS / Mini-CRM must be designed and implemented to fit AWS Free Tier as much as practical during the first 12 months.

First-year cost assumption:

- Route 53/domain is the expected paid exception when domain-based launch is approved.
- Before Route 53/domain setup, the project should be tested and demonstrated using the EC2 public IP or other free AWS-provided endpoint.
- After the 12-month free-tier window, the system should continue as a low-cost AWS deployment.

### Required Free-Tier Guardrails

- Use one Free-Tier-eligible EC2 micro instance for backend/admin APIs.
- Use DynamoDB with low provisioned capacity and minimal indexes for launch.
- Use S3 for compressed product, package, brand, service and gallery images.
- Use Cognito for admin authentication only unless public user accounts are explicitly approved.
- Disable Cognito SMS features, SMS MFA and phone verification where possible.
- Booking and inquiry requests only need to appear in the admin panel; SMS/email notifications are not required for launch.
- Avoid Application Load Balancer, NAT Gateway, RDS, multiple always-on EC2 instances and unnecessary paid notification services.
- Configure AWS billing alerts before public testing.

### Notification Rule

Booking, inquiry and contact submissions must be stored for admin review. Automatic SMS or email notification is optional and disabled by default for the Free-Tier-first deployment.

## Business Rules


### AWS Cost-Control Rule

```text
First 12 months → AWS Free-Tier-first deployment
Expected paid exception → Route 53/domain only, after IP-based testing/demo
After Free Tier → low-cost AWS operation
```

Any backend, database, authentication, storage, notification or deployment decision that may add AWS cost must be reviewed against this rule before implementation.

### Visibility Rule

```text
show_flag = Y → visible on public website
show_flag = N → hidden from public website
```

Applies to:

- Products
- Brands
- Services
- Package product display / package promo placement
- Public content

`show_flag` is different from workflow `status`.

### Sale Rule

A product is considered on sale when `sale_price` exists or sale data is present.

Promotions page always applies the Sale hard filter.

### Package Rule

A package is identified by:

```text
category = packages
```

### Brand Toggle Rule

Clicking an active brand clears the brand filter.

### Product Stock Rule

```text
stock_quantity = 0 → Sold Out
stock_quantity > 0 and <= low_stock_threshold → Low Stock
stock_quantity > low_stock_threshold → In Stock
```

### Booking Customer Rule

When booking is submitted:

1. Create booking record.
2. Auto-create customer if not existing.
3. Set Customer Status to Prospect.
4. Set Customer From to Booking Request.
5. Set Booking Type to Site Visit Request.

### Inquiry Customer Rule

When inquiry is submitted:

1. Create inquiry record.
2. Auto-create customer if not existing.
3. Set Customer Status to Prospect.
4. Set Customer From to Inquiries.

## User Workflows

### Product Discovery Flow

1. Visitor opens Products page.
2. Visitor searches or filters by category/brand.
3. Results update.
4. Visitor sorts if needed.
5. Visitor opens product modal.
6. Visitor contacts business or submits inquiry.

### Promotion Discovery Flow

1. Visitor opens Promotions.
2. Sale is already active.
3. Visitor selects category or brand if desired.
4. Results narrow within sale-only context.
5. Visitor opens product/package modal.
6. Visitor submits inquiry or booking.

### Brand Discovery Flow

1. Visitor opens Brands page.
2. Visitor views hero brand wall.
3. Visitor selects brand from strip.
4. Products under that brand display.
5. Visitor optionally selects category.
6. Search/sort operate within selected brand/category.
7. Visitor opens product modal or submits inquiry.

### Booking Flow

1. Visitor clicks Book Appointment or Request Site Visit.
2. Visitor fills booking form.
3. Booking record is created.
4. Customer record is auto-created if needed.
5. Staff follows up in admin.

### Inquiry Flow

1. Visitor opens product/package modal.
2. Visitor submits inquiry.
3. Inquiry record is created.
4. Customer record is auto-created if needed.
5. Staff follows up in admin.

## Acceptance Criteria

Before launch:

1. Business owner can identify recommended CCTV packages immediately on homepage.
2. Products on Sale and Promotions are clearly distinct.
3. Customer can search and filter products without confusion.
4. Promotions page never shows non-sale products.
5. Package and product modals display correct information.
6. Mobile view works without clipped modals, broken cards, or unusable navigation.
7. Hidden records with `show_flag = N` do not appear on the public site after backend integration.
8. Booking and inquiry forms validate required fields.
9. SEO metadata is present.
10. Images are optimized.
11. Final frontend backup is created.
12. Free-Tier-first deployment review is completed before backend/admin launch.
13. Booking/inquiry requests appear in the admin panel without requiring SMS/email notification workflows.
14. Billing alerts are configured before public testing.

## Validation Requirements

### Product Validation

| Field | Validation |
|---|---|
| show_flag | Required; Y or N |
| display_seq | Optional integer for manual ordering |
| product_name | Required; 3–255 characters |
| product_model | Optional; max 100 characters |
| category | Required; approved category only |
| product_brand_name / brand_key | Lowercase slug style; no spaces |
| price | Optional for package/quotation products; numeric value >= 0 when provided |
| sale_price | Optional numeric value |
| image_path | Required for products and packages |
| stock_quantity | Required integer >= 0 |
| low_stock_threshold | Required integer >= 0; default 10 |
| email | Valid format if provided |
| contact_number | Required for bookings/inquiries |
| preferred_date | Cannot be in the past |

## Data Requirements

The logical data model is defined in [architecture.md](./architecture.md). Public endpoints must enforce `show_flag = Y`.

## Security Requirements

Future implementation must include:

- Cognito authentication for admin.
- Admin-only Cognito configuration for first deployment, with SMS MFA/phone verification disabled where possible.
- JWT validation on protected routes.
- Hashed passwords only.
- Input validation.
- Input sanitization.
- Role-based authorization using Cognito Groups (`Admin`, `Standard`).
- Audit logging.
- Safe error messages.
- SSL before production.
