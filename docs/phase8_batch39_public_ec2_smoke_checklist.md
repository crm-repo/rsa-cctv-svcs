# Batch 39 Public EC2 Smoke Checklist

## Before testing

- [ ] EC2 instance `rsa-cms-demo-backend` is running only because testing is in progress.
- [ ] Current EC2 public IP is known.
- [ ] Security group has HTTP `80` from your IP `/32`.
- [ ] Security group does not expose `8000` publicly.
- [ ] Nginx is active.
- [ ] `rsa-cms-backend.service` is active.

## Read-only public smoke

- [ ] `/` returns 200.
- [ ] `/products.html` returns 200.
- [ ] `/promotions.html` returns 200.
- [ ] `/brands.html` returns 200.
- [ ] `/about.html` returns 200.
- [ ] `/services.html` returns 200.
- [ ] `/contact-us.html` returns 200.
- [ ] `/booking.html` returns 200.
- [ ] `/api/health` returns 200.
- [ ] `/api/products` returns 200.
- [ ] `/api/brands` returns 200.
- [ ] `/api/categories` returns 200.
- [ ] `/api/package-banners` returns 200.
- [ ] `/api/pages/about` returns 200.
- [ ] `/api/pages/contact` returns 200.
- [ ] `/api/pages/services` returns 200.

## Public lockdown checks

- [ ] `/admin/` returns 403.
- [ ] `/api/admin/products` returns 403.
- [ ] `/api/customers` returns 403.
- [ ] GET `/api/bookings` returns 403.
- [ ] GET `/api/inquiries` returns 403.
- [ ] `/docs` returns 403.
- [ ] `/redoc` returns 403.
- [ ] `/openapi.json` returns 403.
- [ ] `http://<PUBLIC_IPV4>:8000/api/health` does not return 200.

## Optional public write smoke

- [ ] POST `/api/bookings` returns 200 or 201.
- [ ] POST `/api/inquiries` returns 200 or 201.
- [ ] Public records can be reviewed later through admin once protected admin access is enabled or through controlled internal checks.

## After testing

- [ ] Commit and push Batch 39 files.
- [ ] Stop EC2 if not continuing immediately.
