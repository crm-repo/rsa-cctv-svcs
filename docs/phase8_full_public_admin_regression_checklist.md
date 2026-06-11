# Phase 8 Full Manual Regression Checklist

## Public website

Run backend and frontend locally.

Backend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\frontend"
python -m http.server 5500
```

Open and verify:

- `http://127.0.0.1:5500/`
- `http://127.0.0.1:5500/products.html`
- `http://127.0.0.1:5500/promotions.html`
- `http://127.0.0.1:5500/brands.html`
- `http://127.0.0.1:5500/about.html`
- `http://127.0.0.1:5500/services.html`
- `http://127.0.0.1:5500/contact-us.html`
- `http://127.0.0.1:5500/booking.html`

Check:

- Products load.
- Promotions show sale products.
- Brands load.
- CMS page content loads.
- Booking form submits.
- Inquiry/contact form submits.
- No console errors.

## Admin website

Open and verify:

- `http://127.0.0.1:5500/admin/`
- `http://127.0.0.1:5500/admin/bookings.html`
- `http://127.0.0.1:5500/admin/inquiries.html`
- `http://127.0.0.1:5500/admin/customers.html`
- `http://127.0.0.1:5500/admin/products.html`
- `http://127.0.0.1:5500/admin/categories.html`
- `http://127.0.0.1:5500/admin/brands.html`
- `http://127.0.0.1:5500/admin/key-features.html`
- `http://127.0.0.1:5500/admin/about.html`
- `http://127.0.0.1:5500/admin/project-gallery.html`
- `http://127.0.0.1:5500/admin/services.html`
- `http://127.0.0.1:5500/admin/contact-us.html`

Check:

- Dashboard cards load.
- Lead lists load.
- Booking and inquiry status updates save.
- Product/category/brand/key feature create/update works.
- Product key-feature suggestions appear.
- Product name preview uses Brand + Feature 01 + Subcategory.
- Product image / brand logo / CMS image fields use Choose File.
- Contact Person photo field appears only for Contact Person records.
- CMS create/update works.
- No delete action appears.
- Auth badge appears in local mode.

## DynamoDB mode

Repeat critical checks with backend started as:

```powershell
$env:RSA_REPOSITORY_MODE="dynamodb"
uvicorn app.main:app --reload
```

After testing:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```
