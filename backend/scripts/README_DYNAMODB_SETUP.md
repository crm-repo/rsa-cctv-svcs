# Phase 8 Batch 5 — DynamoDB Table Setup Scripts

## Purpose

This batch prepares safe DynamoDB table setup scripts for the approved Phase 8 Final v5 plan.

It does **not** create AWS resources automatically.

The scripts are included so the table configuration can be reviewed first, then executed manually only when ready.

## Approved Launch Tables

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

## Approved Launch GSIs

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

## Free-Tier-First Defaults

The setup uses:

```text
BillingMode = PROVISIONED
ReadCapacityUnits = 1
WriteCapacityUnits = 1
```

This applies to each table and each GSI unless environment variables override the values.

Optional overrides:

```text
DYNAMODB_DEFAULT_RCU=1
DYNAMODB_DEFAULT_WCU=1
AWS_REGION=ap-southeast-1
```

## Important Cost Guardrails

Do not enable these for launch unless explicitly approved:

```text
On-demand capacity mode
DynamoDB Streams
Global Tables
Point-in-Time Recovery
Extra GSIs
Large/non-optimized image storage in DynamoDB
```

Images/files should be stored in S3 later, not DynamoDB.

## Run a Dry Run First

From the backend folder:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\create_dynamodb_tables.py --all
```

Expected result:

```text
Mode: DRY RUN
Dry run only. No AWS resources will be created.
```

This prints the table creation configuration as JSON.

## Create Tables Only When Ready

Run this only after AWS credentials, region, and cost settings are confirmed:

```powershell
python scripts\create_dynamodb_tables.py --all --execute --wait
```

If some tables already exist and you want to continue creating missing ones:

```powershell
python scripts\create_dynamodb_tables.py --all --execute --wait --skip-existing
```

## Create One Table Only

Example:

```powershell
python scripts\create_dynamodb_tables.py --table customers --execute --wait
```

Valid logical table names:

```text
products
brands
categories
key_features
customers
bookings
inquiries
about
project_gallery
services
contact_us
id_counters
```

## Check Tables

After creation:

```powershell
python scripts\check_dynamodb_tables.py --all
```

Strict mode exits with an error if any table or approved GSI is missing or not active:

```powershell
python scripts\check_dynamodb_tables.py --all --strict
```

## Table Name Environment Variables

The scripts use the table names from `app/database.py`, which read these optional environment variables:

```text
DYNAMODB_PRODUCTS_TABLE=rsa_products
DYNAMODB_BRANDS_TABLE=rsa_brands
DYNAMODB_CATEGORIES_TABLE=rsa_categories
DYNAMODB_KEY_FEATURES_TABLE=rsa_key_features
DYNAMODB_CUSTOMERS_TABLE=rsa_customers
DYNAMODB_BOOKINGS_TABLE=rsa_bookings
DYNAMODB_INQUIRIES_TABLE=rsa_inquiries
DYNAMODB_ABOUT_TABLE=rsa_about
DYNAMODB_PROJECT_GALLERY_TABLE=rsa_project_gallery
DYNAMODB_SERVICES_TABLE=rsa_services
DYNAMODB_CONTACT_US_TABLE=rsa_contact_us
DYNAMODB_ID_COUNTERS_TABLE=rsa_id_counters
```

For this project, keep the approved default `rsa_` names unless there is a specific reason to override them.

## Batch 5 Test Steps

1. Copy the files into your project.
2. Start the backend and confirm current APIs still work.
3. Run dry-run table preview:

```powershell
python scripts\create_dynamodb_tables.py --all
```

4. Confirm the output includes 12 tables and 5 GSIs.
5. Do **not** run `--execute` until AWS setup/cost review is complete.

## Notes

Batch 5 only prepares table setup scripts.

Actual data loading is planned later:

```text
JSON seed data during development/testing
Excel/CSV import templates before demo/launch for real company data
```
