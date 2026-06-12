# Batch 42 Cognito local auth checklist

## AWS Cognito console

- [ ] User pool exists: `rsa-cms-admin-users`
- [ ] User pool ID recorded: `ap-southeast-1_BNvYFNmw9`
- [ ] App client exists: `rsa-cms-admin-web-client`
- [ ] Client ID recorded: `3r13vplp8agjigm3e52ficsm1e`
- [ ] App client has no client secret
- [ ] App client allows username/password auth for Batch 42 local testing: `ALLOW_USER_PASSWORD_AUTH`
- [ ] MFA is off
- [ ] SMS is not configured
- [ ] Self-registration is disabled
- [ ] Account recovery is email-only
- [ ] Admin user exists and is enabled: `jhannbernas@gmail.com`

## Local backend

- [ ] Batch 42 files copied into project
- [ ] Local backend started with `RSA_ADMIN_AUTH_MODE=cognito`
- [ ] `RSA_COGNITO_REGION=ap-southeast-1`
- [ ] `RSA_COGNITO_USER_POOL_ID=ap-southeast-1_BNvYFNmw9`
- [ ] `RSA_COGNITO_CLIENT_ID=3r13vplp8agjigm3e52ficsm1e`
- [ ] Read-only local check passed
- [ ] Execute local login check passed
- [ ] If `FORCE_CHANGE_PASSWORD`, new permanent password challenge completed

## Frontend admin login

- [ ] Login page detects Cognito mode
- [ ] Login page accepts email/password
- [ ] Valid login redirects to admin dashboard locally
- [ ] Invalid login shows a safe error message
- [ ] Logout clears tokens

## EC2 safety

- [ ] EC2 can stay stopped during Batch 42
- [ ] `/admin/` remains blocked publicly until later batch
- [ ] `/api/admin/*` remains blocked publicly until later batch
- [ ] No admin route exposed through Nginx yet

## Git

- [ ] Do not commit real passwords
- [ ] Do not commit real secrets
- [ ] Commit Batch 42 code/docs only
