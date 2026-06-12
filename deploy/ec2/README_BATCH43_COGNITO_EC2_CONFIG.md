# Batch 43 — Cognito EC2 Backend Config

Files:

- `update_rsa_cms_cognito_env.sh` — updates `/opt/rsa-cms/runtime/backend.env` to Cognito mode and restarts backend.
- `check_rsa_cms_cognito_runtime.sh` — EC2-local runtime check for Cognito mode while Nginx keeps admin blocked.

Run the update script with Cognito values passed as environment variables:

```bash
sudo RSA_COGNITO_REGION="ap-southeast-1" \
  RSA_COGNITO_USER_POOL_ID="ap-southeast-1_BNvYFNmw9" \
  RSA_COGNITO_CLIENT_ID="3r13vplp8agjigm3e52ficsm1e" \
  /tmp/update_rsa_cms_cognito_env.sh
```

Do not put AWS access keys or admin passwords in env files.
