# Phase 8 Batch 41 — Create Cognito Admin User Pool and Configure Auth Values

## Goal

Create the RSA CMS admin Cognito resources in a controlled, Free-Tier-first way, record the user pool/app client values, and verify the configuration before exposing any admin pages publicly.

Batch 41 does **not** expose `/admin/` publicly. Nginx must continue blocking admin routes until a later protected-admin batch passes.

## Required names

Use these names unless there is a strong reason not to:

- User pool name: `rsa-cms-admin-users`
- App client name: `rsa-cms-admin-web-client`
- Region: `ap-southeast-1`
- Admin auth mode later: `cognito`

## Free-Tier / cost guardrails

Keep this Cognito setup email/password only:

- Do not enable SMS.
- Do not enable phone-number sign-in.
- Do not enable SMS MFA.
- Keep MFA off for this launch/demo stage.
- Do not configure SES/custom email sender yet unless explicitly approved.
- Do not expose admin publicly until JWT verification and smoke tests pass.

## Manual AWS Console setup

Sign in with an admin/owner account only for this setup if `rsa-cms-cli-user` does not have Cognito setup permissions.

### 1. Create the user pool

Go to:

```text
AWS Console → Cognito → User pools → Create user pool
```

Use:

```text
Application type: Traditional web application or Single-page application, depending on console wording
Sign-in option: Email
User pool name: rsa-cms-admin-users
```

Recommended settings:

```text
Self registration: Disabled / admin-created users only
MFA: No MFA / Off
Account recovery: Email only
Required attribute: email
Phone number: not required, not auto-verified
SMS: not configured
```

### 2. Create the app client

Use:

```text
App client name: rsa-cms-admin-web-client
Client secret: Do not generate a client secret
```

For authentication flows, allow normal username/email + password login for the admin frontend. Depending on the AWS console wording, this may appear as one or more of:

```text
ALLOW_USER_PASSWORD_AUTH
ALLOW_USER_SRP_AUTH
ALLOW_REFRESH_TOKEN_AUTH
```

Do not create a client secret for browser-based admin login.

### 3. Create one admin user

Create a user with your admin email address.

Recommended:

```text
Send invitation by email if available
Set temporary password and force password change on first login
Do not add phone number
```

Do not paste or commit temporary passwords into the repository.

### 4. Record these values locally

Copy these values from the Cognito console:

```text
User Pool ID
App Client ID
Region
Admin email
```

You can store them in a local uncommitted file copied from:

```text
deploy/cognito/admin-auth.values.local.template.env
```

Do not commit local env/value files or passwords.

## Run the read-only check

From local PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_cognito_admin_user_pool.py `
  --user-pool-id "<USER_POOL_ID>" `
  --client-id "<CLIENT_ID>" `
  --admin-email "<ADMIN_EMAIL>"
```

Expected result:

```text
Batch 41 Cognito admin user pool check PASSED.
```

## Stop point

After Batch 41, do not update Nginx to expose admin yet. The next batch should wire the Cognito values into the backend/frontend and test auth while keeping public admin blocked until protection is verified.
