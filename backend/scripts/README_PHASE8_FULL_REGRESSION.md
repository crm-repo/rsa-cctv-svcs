# Phase 8 Batch 28 — Full Public/Admin Regression

This batch adds the final Phase 8 regression checklist and a local API regression script.

## What it verifies

- Public API reads
- Public booking/inquiry writes
- Admin lead updates
- Admin catalog create/update
- Admin CMS create/update
- Admin auth prep endpoint
- Works in mock mode and DynamoDB mode, depending on how the backend is started

## Dry run

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\test_phase8_full_regression.py
```

## Execute in mock mode

PowerShell 1:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
uvicorn app.main:app --reload
```

PowerShell 2:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\test_phase8_full_regression.py --execute --confirm-write-test
```

## Execute in DynamoDB mode

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

python scripts\test_phase8_full_regression.py --execute --confirm-write-test
```

After DynamoDB test:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```

## Notes

The execute test creates small non-destructive regression records. No delete action is used.
