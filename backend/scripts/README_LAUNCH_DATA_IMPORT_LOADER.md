# Phase 8 Batch 26 — Launch Data Import Loader

This batch adds a safe import script for the company-friendly launch data templates from Batch 25.

## Supported sources

Default source:

```powershell
python scripts\import_launch_data_to_dynamodb.py --all
```

This reads CSV files from:

```text
backend/app/data/import_templates/csv
```

Optional Excel source:

```powershell
python scripts\import_launch_data_to_dynamodb.py --source excel --all
```

Excel import requires `openpyxl` in the backend virtual environment:

```powershell
pip install openpyxl
```

CSV import does not require extra packages.

## Safe defaults

Running without `--execute` is dry-run only:

```powershell
python scripts\import_launch_data_to_dynamodb.py --all
```

Existing records are skipped by default during execute mode:

```powershell
python scripts\import_launch_data_to_dynamodb.py --all --execute
```

Use overwrite only when intentionally replacing existing launch records:

```powershell
python scripts\import_launch_data_to_dynamodb.py --all --execute --overwrite
```

## IDs and media paths

If IDs are blank in the CSV/Excel file, the importer generates IDs using the approved prefixes.

Image filename fields are converted into upload keys such as:

```text
uploads/products/hikvision-2mp-dome.jpg
uploads/brands/hikvision-logo.png
uploads/contact-persons/juan-dela-cruz.jpg
```

Contact Person photo fields apply only to Contact Person rows.

## Product name default

If `product_name` is blank, the importer defaults it from:

```text
product_brand_name + feature_01 + subcategory
```

This follows the approved admin/defaulting rule. The value can still be edited later in admin.

## Recommended launch flow

1. Company fills Excel or CSV templates.
2. Developer validates templates:

   ```powershell
   python scripts\validate_launch_data_templates.py
   ```

3. Developer dry-runs the import:

   ```powershell
   python scripts\import_launch_data_to_dynamodb.py --all
   ```

4. Developer imports into DynamoDB:

   ```powershell
   python scripts\import_launch_data_to_dynamodb.py --all --execute
   ```

5. Developer verifies public/admin pages in DynamoDB mode.
