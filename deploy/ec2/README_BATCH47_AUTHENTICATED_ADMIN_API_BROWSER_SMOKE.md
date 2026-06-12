# Batch 47 — Authenticated Admin API Browser Smoke

This batch is primarily a local/browser smoke-test batch.

No EC2-side script is required for the normal flow. The backend and Nginx behavior should already be in place from Batch 46.

Use:

```powershell
python backend/scripts/check_ec2_authenticated_admin_api_smoke.py --base-url http://<PUBLIC_IPV4>
```

Then run the authenticated version if needed:

```powershell
python backend/scripts/check_ec2_authenticated_admin_api_smoke.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

The password prompt is hidden. Do not paste or commit passwords.
