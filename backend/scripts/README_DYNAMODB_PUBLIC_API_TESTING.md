# Batch 15 — DynamoDB-backed public API testing

Batch 15 extends DynamoDB repository mode to public read APIs:

- products
- package banners
- brands
- categories
- key features
- about
- project gallery
- services
- contact us
- grouped page APIs

Mock mode remains the default. DynamoDB mode is enabled only when you set:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
```

## Test

PowerShell 1:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

PowerShell 2:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\test_dynamodb_public_api_smoke.py
python scripts\test_dynamodb_public_api_smoke.py --execute
```

The execute test is read-only. It calls local API GET endpoints and does not write records.

After testing, stop uvicorn and remove the temporary environment variable:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```
