# RSA CMS Phase 8 Batch 14 — DynamoDB Mode API Testing

Batch 14 is the first local regression test where the backend API is intentionally started with:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
```

This should be done only after:

1. DynamoDB tables exist and are ACTIVE.
2. JSON seed data has been loaded.
3. The app still defaults to `mock` when the environment variable is not set.

## Step 1 — Read-only seed count check

From the backend folder:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_dynamodb_seed_counts.py
```

Expected: all seed tables show counts greater than 0.

## Step 2 — Start backend in DynamoDB mode

Use a new PowerShell window:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

Keep this running.

## Step 3 — Run dry-run plan

In a second PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\test_dynamodb_mode_api_smoke.py
```

Expected: it prints the planned test and makes no writes.

## Step 4 — Run the DynamoDB-mode API smoke test

```powershell
python scripts\test_dynamodb_mode_api_smoke.py --execute --confirm-write-test
```

Expected:

- health endpoint works
- public read endpoints still respond
- booking POST creates a DynamoDB booking record
- customer auto-create writes to DynamoDB
- duplicate Philippine mobile number reuses the same customer
- booking status update persists to DynamoDB
- inquiry POST creates a DynamoDB inquiry record
- inquiry status update persists to DynamoDB

## Step 5 — Stop backend and reset local mode

In the PowerShell running uvicorn, press:

```text
Ctrl + C
```

Then remove the temporary env var:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```

Or open a fresh PowerShell. Fresh shells default back to `mock`.

## Important

Do not leave DynamoDB mode on by accident during normal local development unless you intentionally want API writes to go to AWS.
