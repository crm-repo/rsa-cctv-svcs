# Phase 8 Batch 45 — Admin Login Browser Smoke Test on EC2

## Purpose

Batch 45 verifies the real browser admin login flow on the EC2 public-IP demo after Cognito has been configured and Nginx has exposed only the admin login/auth surface.

This batch does **not** expose admin data APIs yet. The goal is to prove that the admin login page and Cognito token/session flow work while the sensitive admin/CRM data routes remain blocked.

## Safety constraints

- Do not commit the Cognito admin password.
- Do not paste the password into chat.
- Do not enable SMS, phone verification, or MFA for this demo stage.
- Do not expose `/docs`, `/redoc`, or `/openapi.json` publicly.
- Do not expose admin data APIs yet.
- Use EC2 public IP for demo; Route 53/domain remains later.
- Stop EC2 after the batch if you are pausing.

## Preconditions

- Batch 41 Cognito user pool check passed.
- Batch 42 local Cognito login check passed.
- Batch 43 EC2 backend Cognito runtime check passed.
- Batch 44 Nginx admin-login access check passed.
- EC2 is running for this browser smoke test.

## Current known values

```text
RSA_COGNITO_REGION=ap-southeast-1
RSA_COGNITO_USER_POOL_ID=ap-southeast-1_BNvYFNmw9
RSA_COGNITO_CLIENT_ID=3r13vplp8agjigm3e52ficsm1e
RSA_ADMIN_EMAIL=jhannbernas@gmail.com
```

Use the current EC2 public IP from:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_demo_instance_status.py
```

## Step 1 — Run support smoke check from Windows

Replace `<PUBLIC_IPV4>` with the current EC2 IP:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_admin_login_browser_smoke.py --base-url http://<PUBLIC_IPV4>
```

Expected:

- `/admin/` returns 200.
- `/admin/login.html` returns 200.
- `/api/admin/auth/config` returns 200.
- `/api/admin/auth/status` returns anonymous authenticated=false.
- Admin data APIs remain 403.
- `/docs`, `/redoc`, and `/openapi.json` remain 403.

## Step 2 — Browser login test

Open a private/incognito browser window and go to:

```text
http://<PUBLIC_IPV4>/admin/login.html
```

Login with:

```text
Email: jhannbernas@gmail.com
Password: the Cognito admin password
```

If Cognito asks for a new password, set a permanent password and keep it private.

Expected:

- Login succeeds.
- You are redirected to the admin dashboard or see an authenticated admin session.
- You are not asked for SMS or phone verification.
- You do not need a phone number.

## Step 3 — Optional real login script check

After confirming the browser flow, this script can test the same login API flow without printing or storing the password:

```powershell
python scripts\check_ec2_admin_login_browser_smoke.py `
  --base-url http://<PUBLIC_IPV4> `
  --admin-email "jhannbernas@gmail.com" `
  --execute `
  --confirm-login-test
```

The password prompt is hidden. Do not paste the password into chat.

Expected:

- Login returns an access token.
- `/api/admin/auth/status` with that token returns authenticated=true.
- Admin data APIs still return 403 until the protected API exposure batch.

## Step 4 — Manual browser checks

Open these URLs in the browser:

```text
http://<PUBLIC_IPV4>/
http://<PUBLIC_IPV4>/admin/login.html
http://<PUBLIC_IPV4>/api/admin/auth/config
http://<PUBLIC_IPV4>/api/admin/products
http://<PUBLIC_IPV4>/docs
```

Expected:

```text
/                         -> public homepage
/admin/login.html          -> admin login page
/api/admin/auth/config     -> Cognito config JSON
/api/admin/products        -> 403 Forbidden
/docs                      -> 403 Forbidden
```

## Pass criteria

Batch 45 passes when:

- Browser login works using Cognito admin credentials.
- Admin session/token is established.
- SMS/phone/MFA are not required.
- Admin data APIs are still blocked publicly.
- API docs remain blocked publicly.
- Public website still works.

## Rollback

If browser login fails but public site is otherwise healthy:

1. Keep Nginx Batch 44 config in place.
2. Do not expose data APIs.
3. Re-run Batch 43 Cognito runtime check.
4. Re-run Batch 44 Nginx admin-login access check.
5. Verify app client still allows `ALLOW_USER_PASSWORD_AUTH`.
6. Verify the admin user is enabled and not deleted.
