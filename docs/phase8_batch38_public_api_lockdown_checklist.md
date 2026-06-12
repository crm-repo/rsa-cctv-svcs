# Phase 8 Batch 38 checklist — Public API lockdown

## EC2/Nginx

- [ ] EC2 instance `rsa-cms-demo-backend` is running only for this work session.
- [ ] Nginx config test passes with `sudo nginx -t`.
- [ ] Nginx service is active.
- [ ] Backend service `rsa-cms-backend.service` is active.
- [ ] Public homepage loads through port 80.
- [ ] Public API `/api/health` works through port 80.

## Public/admin route separation

- [ ] `/admin/` returns 403.
- [ ] `/api/admin/products` returns 403.
- [ ] `/api/customers` returns 403.
- [ ] `GET /api/bookings` returns 403.
- [ ] `GET /api/inquiries` returns 403.
- [ ] `/docs` returns 403.
- [ ] `/openapi.json` returns 403.
- [ ] Direct public port 8000 is unreachable.

## Security group

- [ ] SSH 22 is limited to current IP `/32`.
- [ ] HTTP 80 is limited to current IP `/32` for this demo stage.
- [ ] Port 8000 inbound rule has been removed.
- [ ] No inbound rule uses `0.0.0.0/0` or `::/0` for SSH, 80, 443, 8000, or 3389.

## Cost/safety

- [ ] No Elastic IP created.
- [ ] No ALB created.
- [ ] No NAT Gateway created.
- [ ] No RDS created.
- [ ] EC2 will be stopped when this work session ends.
