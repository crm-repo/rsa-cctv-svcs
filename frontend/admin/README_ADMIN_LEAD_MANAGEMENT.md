# RSA CMS Admin Lead Management Pages — Batch 18

Batch 18 adds API-backed admin CRM pages for:

- `frontend/admin/bookings.html`
- `frontend/admin/inquiries.html`
- `frontend/admin/customers.html`

## Scope

This batch is intentionally non-destructive:

- List bookings, inquiries, and customers from backend APIs.
- Open record detail drawer/modal.
- Update booking/inquiry status, assigned person, and comments.
- Customers page is read-only.
- No delete actions.
- No Cognito yet.
- Mock mode remains the default.

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
http://127.0.0.1:5500/admin/bookings.html
http://127.0.0.1:5500/admin/inquiries.html
http://127.0.0.1:5500/admin/customers.html
```

## DynamoDB mode optional regression

After mock-mode testing passes, optionally start backend with:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

Then retest the same admin pages. Stop Uvicorn and reset the temporary variable after testing:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```
