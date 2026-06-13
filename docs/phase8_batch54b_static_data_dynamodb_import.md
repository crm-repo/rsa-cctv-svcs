# Phase 8 Batch 54B — Safe DynamoDB Wipe/Reimport from Reviewed Static Data

## Objective

Load the reviewed static HTML data from Batch 54A into DynamoDB as the new launch/demo baseline.

## Scope

Wipe and reload:

- `rsa_products`
- `rsa_brands`
- `rsa_categories`
- `rsa_key_features`
- `rsa_about`
- `rsa_project_gallery`
- `rsa_services`
- `rsa_contact_us`

Wipe only, leaving empty for fresh test submissions:

- `rsa_customers`
- `rsa_bookings`
- `rsa_inquiries`

Preserve:

- DynamoDB tables
- GSIs
- `rsa_id_counters`

## Counter rule

Counters are never reset downward. The importer scans the reviewed static IDs and advances only prefixes whose reviewed max ID is greater than the current counter value.

## Validation

The importer validates:

- Required primary keys
- Duplicate primary keys
- Product category references
- Product subcategory references inside the selected category
- Product brand references
- Exactly one company contact row using `CONT-0000001`

## Commands

Dry-run:

```powershell
cd backend
python scripts\import_static_review_data_to_dynamodb.py --all
```

Execute:

```powershell
python scripts\import_static_review_data_to_dynamodb.py --all --execute --confirm-wipe-reviewed-static-data
```

## Post-import checks

After import, start EC2 only when ready to test. Then verify:

- Public product catalog loads 28 reviewed products.
- Public brands page loads reviewed brands.
- Public services/about/contact pages load reviewed CMS/contact data.
- Contact form creates a new inquiry.
- Booking form creates a new booking.
- Admin pages show new inquiry/booking/customer records after test submissions.
