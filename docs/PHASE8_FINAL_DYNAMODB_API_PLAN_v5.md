# Phase 8 Final v5 — DynamoDB Access Pattern and Table-Key Plan

Status: Approved for implementation  
Project: RSA CMS / Mini-CRM  
Phase: Phase 8 — Backend / Admin CMS / Mini-CRM

## 1. Approved Launch Tables

Use the `rsa_` prefix and simple multi-table DynamoDB design.

Launch tables:

```text
rsa_products
rsa_brands
rsa_categories
rsa_key_features
rsa_customers
rsa_bookings
rsa_inquiries
rsa_about
rsa_project_gallery
rsa_services
rsa_contact_us
rsa_id_counters
```

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

Packages are stored in `rsa_products`. Contact Us records are consolidated into `rsa_contact_us`.

## 2. Approved Launch GSIs

```text
rsa_products:
- category_key-display_seq-index
  PK: category_key
  SK: display_seq

- product_brand_key-display_seq-index
  PK: product_brand_key
  SK: display_seq

rsa_customers:
- contact_number_normalized-index
  PK: contact_number_normalized

rsa_bookings:
- status-created_at-index
  PK: status
  SK: created_at

rsa_inquiries:
- status-created_at-index
  PK: status
  SK: created_at
```

Skipped for launch:

```text
customer email GSI
product show_pack GSI
product sale GSI
brand_key GSI
category_key GSI
key feature search GSI
CMS content GSIs
contact_type GSI
customer status/source GSIs
customer related booking GSI
inquiry product/customer GSIs
```

Simplified launch capacity count:

```text
12 tables at 1 RCU / 1 WCU each = 12 RCU + 12 WCU
5 GSIs at 1 RCU / 1 WCU each = 5 RCU + 5 WCU
Total = 17 RCU + 17 WCU minimum simplified count
```

## 3. ID Rules

All major IDs use a four-letter prefix followed by a seven-digit sequence.

```text
XXXX-0000001
```

Examples:

```text
CCTV-0000001
RECO-0000001
PACK-0000001
BRND-0000001
CUST-0000001
BOOK-0000001
INQR-0000001
CATG-0000001
KFEA-0000001
ABOU-0000001
PROJ-0000001
SERV-0000001
CONT-0000001
CPER-0000001
SOCM-0000001
```

Product IDs are category-based. The backend reads `category_prefix` from `rsa_categories`, increments the matching counter in `rsa_id_counters`, and generates the next product ID server-side.

## 4. Universal Visibility Rules

```text
show_flag = Y → visible on public website
show_flag = N → hidden from public website
```

`show_flag` is not the same as workflow `status`.

Package products use:

```text
show_flag = normal catalog / promotions grid visibility
show_pack_flag = homepage package cards and package hero/highlight placement only
```

`show_flag = N` overrides all public display, even if `show_pack_flag = Y`.

## 5. Product Rules

Packages are normal products where:

```text
category_key = packages
```

`GET /api/package-banners` should read from `rsa_products`, filtering:

```text
show_flag = Y
category_key = packages
show_pack_flag = Y
```

Sale rule:

```text
price = normal/original/base price
sale_price = sale/current promotional price
```

A product is on sale when `sale_price` exists. Do not create `old_price`, `sale_flag`, `is_sale`, or `on_sale` database fields.

Product name defaulting rule:

```text
product_name default = product_brand_name + feature_01 + subcategory
```

This is an admin form convenience only. `product_name` is editable before saving. Do not auto-generate or modify `description`, and do not add `auto_name_flag`.

Approved product fields:

```text
product_id
show_flag
show_pack_flag
display_seq
product_name
product_model
product_slug
category_id
category_key
category_name
category_prefix
subcategory
brand_id
product_brand_key
product_brand_name
brand_logo_path
description
feature_01
feature_02
feature_03
feature_04
feature_05
feature_06
feature_07
feature_08
feature_09
feature_10
price
sale_price
image_path
stock_quantity
low_stock_threshold
meta_title
meta_description
created_at
updated_at
created_by
updated_by
```

Product features require minimum 3 populated feature fields. Null feature fields are not displayed publicly.

## 6. Category Rules

`rsa_categories` stores admin-managed categories and product ID prefixes.

Approved fields:

```text
category_id
show_flag
display_seq
category_name
category_key
category_prefix
icon_code
description
created_at
updated_at
created_by
updated_by
```

`icon_code` stores Font Awesome class/code for category buttons, for example:

```text
fa-solid fa-video
fa-solid fa-hard-drive
fa-solid fa-box
```

Approved category snapshot fields on `rsa_products`:

```text
category_id
category_key
category_name
category_prefix
```

Do not store category `icon_code` on products for launch.

## 7. Brand Rules

`brand_id` remains the source reference. Products also store snapshot fields for faster public API reads:

```text
product_brand_key
product_brand_name
brand_logo_path
```

If brand key/name/logo changes later, the admin/backend should update affected product snapshot fields.

## 8. Key Features

Use `rsa_key_features` for reusable product feature suggestions/autocomplete.

Approved fields:

```text
key_feat_id
key_feat_name
created_at
updated_at
created_by
updated_by
```

Feature input behavior:

- Admin can select an existing key feature.
- Admin can type a new feature.
- If no existing match is selected, the backend stores the new text in `rsa_key_features` for reuse.

## 9. Customers, Bookings, and Inquiries

Booking and inquiry submissions auto-create or link customers.

Customer matching at launch uses contact number only:

```text
1. Normalize contact number.
2. Query contact_number_normalized-index.
3. Reuse customer_id if found.
4. Create customer if not found.
5. Store email_address_normalized but do not index it at launch.
```

Default customer values:

```text
customer_status = Prospect
customer_from = Booking Request or Inquiries
repeat_customer = N
```

Booking default values:

```text
status = New
booking_type = Site Visit Request
```

Inquiry default values:

```text
status = New
```

## 10. CMS Content Tables

Approved CMS content tables:

```text
rsa_about
rsa_project_gallery
rsa_services
rsa_contact_us
```

About Us can use one active record at launch. Project Gallery and Services are small lists filtered by `show_flag` and sorted by `display_seq`.

## 11. Consolidated Contact Us Table

Use one table:

```text
rsa_contact_us
```

Primary key:

```text
contact_us_id
```

Use `contact_type` to separate records:

```text
Company Contact
Contact Person
Social Media
```

The admin page still shows 3 sections, but all records are stored in the same table.

Shared fields:

```text
contact_us_id
show_flag
contact_type
display_seq
created_at
updated_at
created_by
updated_by
```

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

Use fixed/default company contact record:

```text
CONT-0000001
```

No `contact_type` GSI is needed at launch.

## 12. Public API Strategy

Public product/catalog APIs:

```text
GET /api/products
GET /api/products/{id}
GET /api/products?category=...
GET /api/products?brand=...
GET /api/products?sale=true
GET /api/brands
GET /api/brands/{id}
GET /api/brands/key/{brand_key}
GET /api/categories
GET /api/key-features
GET /api/package-banners
```

Lead capture APIs:

```text
POST /api/bookings
POST /api/inquiries
```

Grouped page APIs:

```text
GET /api/pages/about
GET /api/pages/contact
GET /api/pages/services
```

Individual CMS public APIs:

```text
GET /api/about
GET /api/project-gallery
GET /api/services
GET /api/contact
GET /api/contact-persons
GET /api/social-media
```

Admin-style routes remain unprotected only for local testing and must be protected by Cognito before public/external admin testing.

## 13. Free-Tier-First Rules

For launch:

- Use provisioned capacity with low RCU/WCU unless later approved otherwise.
- Do not add unnecessary GSIs.
- Do not use global tables.
- Do not enable DynamoDB Streams unless needed later.
- Do not enable Point-in-Time Recovery unless later approved.
- Do not store images/files directly in DynamoDB.
- Store image paths or S3 keys only.
- Keep notification workflows disabled by default.
- Booking and inquiry records only need to appear in admin for launch.

## 14. Approved Implementation Order

```text
1. Update product model/service to match v5 schema.
2. Add categories model/service/routes.
3. Add key features model/service/routes.
4. Update package-banners endpoint to read from products.
5. Add About / Project Gallery / Services mock APIs.
6. Add consolidated Contact Us mock APIs.
7. Add ID counter service.
8. Add repository layer.
9. Move customers, bookings, and inquiries to DynamoDB.
10. Move product/CMS content tables to DynamoDB.
11. Add Cognito protection before external/public admin testing.
```
