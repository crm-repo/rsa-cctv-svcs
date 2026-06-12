# Batch 45 — Admin Login Browser Smoke Test

No EC2-side deployment script is required for this batch. Batch 45 uses the Batch 44 Nginx configuration and Batch 43 Cognito runtime values.

Run the local helper script from Windows:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_admin_login_browser_smoke.py --base-url http://<PUBLIC_IPV4>
```

Then manually test:

```text
http://<PUBLIC_IPV4>/admin/login.html
```

Stop EC2 after this batch if not continuing immediately.
