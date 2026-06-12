# Batch 37 — Nginx public-site proxy

This batch configures Nginx on the EC2 demo instance.

Nginx serves:

- public static frontend from `/opt/rsa-cms/current/frontend`
- `/api/` via proxy to FastAPI at `127.0.0.1:8000`

Nginx blocks:

- `/admin`
- `/admin/`

Admin must remain blocked publicly until Cognito/JWT enforcement is enabled.

Run on EC2:

```bash
sudo /tmp/configure_rsa_cms_nginx.sh
/tmp/check_rsa_cms_nginx_public_site.sh
```

Then update the EC2 security group manually for the Batch 37 smoke test:

- Add HTTP 80 from your current IP `/32`
- Remove direct port 8000 after Nginx works
- Keep SSH 22 from your current IP `/32`

Do not open HTTP 80 to `0.0.0.0/0` in this batch.
