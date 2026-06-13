# Phase 8 Batch 54B — Static Review Data DynamoDB Import

This batch imports the reviewed Batch 54A static HTML data into DynamoDB.

## Safety rules

- DynamoDB tables are **not deleted**.
- Selected table records are wiped/reseeded only when `--execute` is used.
- Execute mode requires `--confirm-wipe-reviewed-static-data`.
- `rsa_id_counters` is **not wiped**.
- ID counters are never reset downward. They are only advanced when the reviewed static IDs are higher than the current counter value.
- `customers`, `bookings`, and `inquiries` are wiped by default when running `--all`, then left empty so new tests can recreate them from the public forms.

## Dry-run first

From the `backend` folder:

```powershell
python scripts\import_static_review_data_to_dynamodb.py --all
```

Expected result: validation summary only. No DynamoDB deletes/writes.

## Execute import

Only after dry-run is clean:

```powershell
python scripts\import_static_review_data_to_dynamodb.py --all --execute --confirm-wipe-reviewed-static-data
```

## Optional commands

Process only one table:

```powershell
python scripts\import_static_review_data_to_dynamodb.py --table products
python scripts\import_static_review_data_to_dynamodb.py --table products --execute --confirm-wipe-reviewed-static-data
```

Skip wiping leads while importing catalog/CMS/contact data:

```powershell
python scripts\import_static_review_data_to_dynamodb.py --all --skip-lead-wipe
```

## Source files

Default source folder:

```text
backend/app/data/review_import
```

Expected files:

```text
categories.json
brands.json
products.json
key_features.json
about.json
project_gallery.json
services.json
contact_us.json
customers.json
bookings.json
inquiries.json
```
