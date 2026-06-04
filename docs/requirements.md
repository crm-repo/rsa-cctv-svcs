# RSA CMS / Mini-CRM Requirements

## Authority

This document is the authoritative business, functional, and non-functional requirements specification for RSA CMS / Mini-CRM. For implementation progress, use [feature-status.md](./feature-status.md). For technical design, use [architecture.md](./architecture.md).

## Functional Requirements

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
- Static for launch.
- Future admin should manage package banner visibility and ordering.

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

Homepage package banners are static for launch.

Future admin should manage package banners using:

- show_flag
- display_order
- homepage_visible
- promotions_hero_visible

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

## Business Rules

### Visibility Rule

```text
show_flag = Y → visible on public website
show_flag = N → hidden from public website
```

Applies to:

- Products
- Brands
- Services
- Package banners
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

## Validation Requirements

### Product Validation

| Field | Validation |
|---|---|
| show_flag | Required; Y or N |
| display_order | Optional integer |
| product_name | Required; 3–255 characters |
| product_model | Optional; max 100 characters |
| category | Required; approved category only |
| product_brand_name / brand_key | Lowercase slug style; no spaces |
| price | Required numeric value >= 0 |
| old_price | Optional numeric value; should exceed sale/current price |
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
- JWT validation on protected routes.
- Hashed passwords only.
- Input validation.
- Input sanitization.
- Role-based authorization.
- Audit logging.
- Safe error messages.
- SSL before production.
