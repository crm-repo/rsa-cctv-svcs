# Batch 16 — Public Website End-to-End DynamoDB Regression

This test confirms that the public website and public APIs work while the backend is running in DynamoDB mode.

## What this validates

- Backend runs with `RSA_REPOSITORY_MODE=dynamodb`
- Public read APIs return DynamoDB-backed data
- Public frontend pages load from the local frontend server
- Booking API creates records in DynamoDB
- Inquiry API creates records in DynamoDB
- Customer records are created/reused in DynamoDB
- Philippines contact-number formats remain supported

## Run order

### 1. Start backend in DynamoDB mode

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

Keep this PowerShell window open.

### 2. Start frontend static server

Open a second PowerShell window:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\frontend"
python -m http.server 5500
```

Keep this PowerShell window open.

### 3. Run the read-only regression test

Open a third PowerShell window:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\test_public_site_dynamodb_e2e.py
```

Expected final line:

```text
Batch 16 public-site DynamoDB regression PASSED.
```

### 4. Run the write regression test

This creates a small booking and inquiry test record through the public APIs and verifies them in DynamoDB.

```powershell
python scripts\test_public_site_dynamodb_e2e.py --execute --confirm-write-test
```

Expected final line:

```text
Batch 16 public-site DynamoDB regression PASSED.
```

## Manual browser check

Open these pages while the backend and frontend servers are running:

```text
http://127.0.0.1:5500/products.html
http://127.0.0.1:5500/promotions.html
http://127.0.0.1:5500/brands.html
http://127.0.0.1:5500/about.html
http://127.0.0.1:5500/services.html
http://127.0.0.1:5500/contact-us.html
http://127.0.0.1:5500/booking.html
```

Confirm page content loads and submit one test booking/inquiry if needed.

## Cleanup after testing

Stop Uvicorn with `Ctrl + C`, then reset the temporary environment variable:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```

Mock mode remains the default when the env var is not set.
