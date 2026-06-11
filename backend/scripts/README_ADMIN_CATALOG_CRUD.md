# Batch 20 — Admin Catalog CRUD Backend/Actions

This batch adds safe create/update support for admin catalog records.

Covered modules:

- Products
- Categories
- Brands
- Key Features

Safe limits:

- No delete endpoints yet.
- No image upload yet.
- No Cognito yet; still local/admin preview only.
- Mock mode remains default.
- DynamoDB mode works only when `RSA_REPOSITORY_MODE=dynamodb` is explicitly set.

Smoke test:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\test_admin_catalog_crud_smoke.py
python scripts\test_admin_catalog_crud_smoke.py --execute --confirm-write-test
```
