# Batch 37 checklist

- [ ] EC2 demo instance running only while testing.
- [ ] Current EC2 public IPv4 confirmed.
- [ ] Nginx configuration script copied to EC2.
- [ ] Nginx installed/configured.
- [ ] `rsa-cms-backend.service` active.
- [ ] `nginx` active.
- [ ] Local EC2 check `http://127.0.0.1/` returns 200.
- [ ] Local EC2 check `http://127.0.0.1/api/health` returns 200.
- [ ] Local EC2 check `http://127.0.0.1/api/products` returns 200.
- [ ] Local EC2 check `http://127.0.0.1/admin/` returns 403.
- [ ] Security group has SSH 22 from current IP `/32` only.
- [ ] Security group has HTTP 80 from current IP `/32` only.
- [ ] Direct public port 8000 removed after Nginx proxy works.
- [ ] No `0.0.0.0/0` inbound rule added in Batch 37.
- [ ] No Elastic IP, ALB, NAT Gateway, RDS, Route 53, SMS, or paid notification drift.
- [ ] EC2 stopped after the batch if not continuing immediately.
