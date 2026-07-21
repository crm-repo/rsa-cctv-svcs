# RSA CMS Admin Dashboard Shell — Phase 8 Batch 17

This folder adds the first admin UI shell for the RSA CMS / Mini-CRM project.

## Scope

Batch 17 is intentionally read-only and safe:

- Admin dashboard layout
- Sidebar navigation shell
- Summary dashboard cards
- Recent bookings and latest inquiries panels
- Catalog snapshot panel
- CMS management preview cards
- Quick action placeholders
- API-backed dashboard data loading

## Not included yet

- Cognito authentication
- Product CRUD
- CMS CRUD
- Booking/inquiry status updates
- Image upload
- Destructive actions

## Local test

Start backend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
uvicorn app.main:app --reload
```

Start frontend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\frontend"
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500/admin/
```

The dashboard should load API data from:

```text
http://127.0.0.1:8000/api
```

Optional override:

```text
http://127.0.0.1:5500/admin/?apiBase=http://127.0.0.1:8000/api
```

## DynamoDB-mode preview

To preview with real DynamoDB-backed API data, start the backend with:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

After testing, stop Uvicorn and reset:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```
