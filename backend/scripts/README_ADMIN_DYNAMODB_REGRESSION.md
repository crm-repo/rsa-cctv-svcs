# Batch 22 — Admin DynamoDB Regression Test

Purpose: confirm the admin catalog and CMS create/update actions work against real DynamoDB, not only mock mode.

## What it tests

- Admin category create in DynamoDB
- Admin brand create in DynamoDB
- Admin key feature create in DynamoDB
- Admin product create/update in DynamoDB
- Admin About create/update in DynamoDB
- Admin Services create/update in DynamoDB
- Admin Project Gallery create/update in DynamoDB
- Admin Contact Us / Social Media create/update in DynamoDB
- Public read APIs still respond after admin writes

The script creates hidden/low-display test records and does not delete records.

## Run order

PowerShell 1 — backend in DynamoDB mode:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

PowerShell 2 — dry run first:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\test_admin_dynamodb_regression.py
```

PowerShell 2 — execute test:

```powershell
python scripts\test_admin_dynamodb_regression.py --execute --confirm-write-test
```

Expected final line:

```text
Batch 22 admin DynamoDB regression test PASSED.
```

After test, stop Uvicorn and reset the environment variable:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```

Normal local development should continue to default to mock mode.
