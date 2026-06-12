# Phase 8 Batch 41 Cognito Setup Checklist

## AWS Console

- [ ] Region is `ap-southeast-1`.
- [ ] User pool created: `rsa-cms-admin-users`.
- [ ] Sign-in uses email.
- [ ] Self-registration is disabled/admin-created users only.
- [ ] MFA is OFF.
- [ ] SMS is not configured.
- [ ] Phone number is not required.
- [ ] Phone number is not auto-verified.
- [ ] Account recovery uses email only.
- [ ] App client created: `rsa-cms-admin-web-client`.
- [ ] App client has no client secret.
- [ ] App client supports username/email + password auth and refresh tokens.
- [ ] One admin user has been created with an email address.
- [ ] No admin passwords or temporary passwords are committed or pasted into docs.

## Local verification

- [ ] `check_cognito_admin_user_pool.py` runs successfully.
- [ ] User Pool ID copied locally.
- [ ] App Client ID copied locally.
- [ ] Admin email copied locally.
- [ ] Local values are not committed.

## Deployment safety

- [ ] `/admin/` is still blocked publicly by Nginx.
- [ ] `/api/admin/*` is still blocked publicly by Nginx.
- [ ] `/api/customers`, `/api/bookings`, and `/api/inquiries` are still blocked publicly.
- [ ] `/docs`, `/redoc`, and `/openapi.json` are still blocked publicly.
- [ ] EC2 can remain stopped unless doing live checks.
