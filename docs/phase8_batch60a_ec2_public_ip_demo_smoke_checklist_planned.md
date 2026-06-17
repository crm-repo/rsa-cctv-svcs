# Phase 8 Batch 60A — EC2 Public-IP Demo Smoke Checklist / Demo Readiness Pass

Project: RSA CMS / Mini-CRM  
Status: Planned  
Current anchor: Runs after Batch 58, Batch 59A, and Batch 59B  
Prepared: 2026-06-16

## Purpose

Batch 60A confirms that the EC2 public-IP demo is ready to be shown to the customer/stakeholders using the current approved/demo data.

This batch replaces the earlier idea named:

```text
Batch 62 — Full Public + Admin Regression After Final Data
```

The scope is the same regression workstream, moved earlier and renamed so the project can reach demo readiness before Route 53/domain launch.

## Demo target

The demo target remains the current HTTP public-IP setup:

```text
Public site: http://EC2_PUBLIC_IP/
Admin site:  http://EC2_PUBLIC_IP/admin/
```

HTTPS/domain is not required for this demo. Batch 61 handles the later Route 53 + ACM + CloudFront launch path after customer/domain approval.

## Required preconditions

Batch 60A should start only after these batches are applied and pushed/deployed:

```text
Batch 58  — Image Lazy Loading
Batch 59A — Cognito Groups + Settings > Users
Batch 59B — Admin-only Restricted/Delete Actions
```

EC2 should be started only while running the smoke/demo checks.

## Public website demo checklist

Verify all public pages load from the EC2 public IP:

```text
Home
Products
Promotions
Brands
About Us
Services
Contact Us
Booking / Request Site Visit
```

Public behavior checks:

```text
Homepage package cards display correctly.
Featured Products and Products on Sale sections load from API-backed data.
Products page loads DynamoDB product data, not mock/default data.
Products filtering works: category, brand, search, sort, pagination.
Promotions page keeps Sale active.
Promotions hero shows promoted package products only.
Brands page remains dynamic and is not broken by Promotions hero logic.
Package products without fixed price show Get Quotation where applicable.
Product modal opens and closes correctly.
Public images and S3-backed media display through /api/media/.
Contact form/inquiry submission creates an inquiry record.
Booking form submission creates a booking/customer lead record.
```

## Admin demo checklist

Verify admin login and protected pages:

```text
Admin login loads.
Admin user can sign in.
Admin dashboard loads after login.
Protected admin APIs reject missing/invalid tokens.
```

Admin role checks from Batch 59A / 59B:

```text
Admin user sees Settings.
Admin user sees Settings > Users.
Admin user can view users.
Admin user can add users.
Admin user can reset a user's temporary password.
New/temporary password is shown once only after create/reset.
First-login password-change flow works in browser.
Standard user does not see Settings.
Standard user cannot access Settings > Users directly.
Standard user gets backend 403 for restricted user-management APIs.
```

Admin CMS/catalog/lead checks:

```text
Products admin list/detail loads.
Product create/update still works.
Category/subcategory dropdown behavior still works.
Brand admin list/detail loads.
Services admin loads.
About / Project Gallery admin loads.
Contact Us admin loads.
Bookings admin loads.
Inquiries admin loads.
Customers admin loads.
Admin media upload still works for Products, Brands, Project Gallery, and Contact Person photos.
Restore Current behavior still works for media fields where applicable.
```

Admin-only restricted/delete checks from Batch 59B:

```text
Admin sees delete controls only for approved non-lead record types.
Standard users do not see delete controls.
Backend delete/restricted endpoints return 403 for Standard users.
Bookings have no delete control, even for Admin.
Inquiries have no delete control, even for Admin.
Customers/lead records have no delete control, even for Admin.
Existing category/subcategory/brand dependency protections remain intact.
```

## Demo data sanity checklist

Verify that demo data looks reasonable before showing it:

```text
Products have correct names, categories, subcategories, brands, prices/quotation labels, and images.
Promoted package records are intentional and show correctly.
Brands have correct logos and active/visible state.
Services content and images are acceptable.
About Us and project gallery content are acceptable.
Contact company/person/social media records are acceptable.
Booking and inquiry test records are clearly test/demo records if created during smoke.
No obvious broken image paths, placeholder text, or old batch notes are visible.
```

## Technical smoke commands

Recommended EC2/local service checks when connected to EC2:

```bash
sudo systemctl is-active nginx
sudo systemctl is-active rsa-cms-backend
sudo nginx -t
sudo ss -lntp | egrep ':80|:8000'
curl -sSI http://127.0.0.1/ | head -20
curl -sS -o /tmp/health.out -w "health_http=%{http_code}\n" http://127.0.0.1:8000/api/health
cat /tmp/health.out
```

Public browser smoke should use:

```text
http://CURRENT_EC2_PUBLIC_IP/
```

not HTTPS.

## Acceptance criteria

Batch 60A is complete when:

```text
Public website pages load from the current EC2 public IP.
Public forms can create booking/inquiry records.
Admin login works.
Admin/Standard role visibility and backend enforcement work.
Admin catalog/CMS/lead pages load.
Admin media display/upload still works.
Demo data has been reviewed and is acceptable for presentation.
Any issues found are fixed or explicitly logged before demo.
```

## Out of scope

Do not include:

```text
Route 53/domain/HTTPS setup
CloudFront setup
SEO canonical/sitemap/robots work
New feature development unrelated to demo readiness
Paid WAF/ALB/NAT/RDS changes
Email/SMS notification enablement
```

## EC2 cost reminder

Stop the EC2 demo instance after smoke testing/demo when it is not actively needed.
