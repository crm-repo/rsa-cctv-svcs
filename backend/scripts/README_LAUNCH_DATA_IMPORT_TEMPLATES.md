# Phase 8 Batch 25 — Launch Data Excel/CSV Templates

This batch prepares user-friendly launch data templates for company-provided content.

## Why this exists

Company users should not edit JSON. JSON remains useful for development/testing, but Excel/CSV is better for real launch data collection.

## Included files

```text
backend/app/data/import_templates/rsa_launch_data_template.xlsx
backend/app/data/import_templates/schema_manifest.json
backend/app/data/import_templates/csv/categories.csv
backend/app/data/import_templates/csv/brands.csv
backend/app/data/import_templates/csv/key_features.csv
backend/app/data/import_templates/csv/products.csv
backend/app/data/import_templates/csv/services.csv
backend/app/data/import_templates/csv/about.csv
backend/app/data/import_templates/csv/project_gallery.csv
backend/app/data/import_templates/csv/contact_us.csv
backend/scripts/validate_launch_data_templates.py
```

## Recommended company workflow

1. Give the company the Excel workbook:

   ```text
   rsa_launch_data_template.xlsx
   ```

2. Ask them to fill the sheets.

3. They should only enter image filenames, not project-folder paths.

   Example:

   ```text
   hikvision-dome-camera.jpg
   ```

   Not:

   ```text
   assets/images/products/hikvision-dome-camera.jpg
   ```

4. Before final import, export sheets to CSV or copy the rows into the CSV templates.

5. Validate CSV files:

   ```powershell
   cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
   venv\Scripts\activate

   python scripts\validate_launch_data_templates.py
   ```

## Important conventions

### Philippines mobile numbers

Use:

```text
+63 919 123 4567
0919 123 4567
(0) 919 123 4567
```

### Visibility flags

Use:

```text
Y
N
```

### Contact Us contact types

Use exactly:

```text
Company Contact
Contact Person
Social Media
```

Photo fields apply only to Contact Person rows.

### Product name

`product_name` may be left blank. The admin/backend can default it from:

```text
Brand + feature_01 + subcategory
```

The admin may still edit the product name later.

### Image fields

For user-facing templates, fill filename fields only:

```text
image_filename
brand_logo_filename
photo_filename
```

Path/key fields are resolved later by the media upload/import process.

## What this batch does not do

This batch does not import the templates into DynamoDB yet.

The actual launch import can be done later after reviewing the completed company data.
