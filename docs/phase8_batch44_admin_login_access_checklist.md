# Batch 44 Admin Login Access Checklist

- [ ] EC2 started only for this deployment/test session.
- [ ] Current public IPv4 confirmed after EC2 start.
- [ ] Batch 44 Nginx configure/check scripts copied to EC2.
- [ ] Nginx config backup created.
- [ ] `sudo nginx -t` passes.
- [ ] Nginx reload succeeds.
- [ ] `/admin/login.html` returns HTTP 200.
- [ ] `/api/admin/auth/config` returns HTTP 200.
- [ ] `/api/admin/auth/status` returns HTTP 200 and anonymous unauthenticated status.
- [ ] Invalid `POST /api/admin/auth/cognito-login` reaches backend and fails with 400/401/422, not 403.
- [ ] `/api/admin/products` remains HTTP 403.
- [ ] `/api/customers` remains HTTP 403.
- [ ] `GET /api/bookings` and `GET /api/inquiries` remain HTTP 403.
- [ ] `/docs`, `/redoc`, and `/openapi.json` remain HTTP 403.
- [ ] Public pages and public APIs remain HTTP 200.
- [ ] EC2 stopped after testing if not continuing immediately.
