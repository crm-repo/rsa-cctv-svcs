#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"
ENV_FILE="$APP_ROOT/runtime/backend.env"
SERVICE="rsa-cms-backend.service"
APP_USER="ubuntu"
if id ec2-user >/dev/null 2>&1; then APP_USER="ec2-user"; fi
if id ubuntu >/dev/null 2>&1; then APP_USER="ubuntu"; fi

printf 'RSA CMS Batch 43 - Apply Cognito backend runtime environment\n'
printf 'This updates /opt/rsa-cms/runtime/backend.env and restarts the backend service.\n'
printf 'It does not store AWS access keys and does not change Nginx public admin lockdown.\n\n'

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: run with sudo and pass environment variables, for example:"
  echo "sudo RSA_COGNITO_REGION=ap-southeast-1 RSA_COGNITO_USER_POOL_ID=... RSA_COGNITO_CLIENT_ID=... /tmp/update_rsa_cms_cognito_env.sh"
  exit 1
fi

: "${RSA_COGNITO_REGION:?Set RSA_COGNITO_REGION before running this script.}"
: "${RSA_COGNITO_USER_POOL_ID:?Set RSA_COGNITO_USER_POOL_ID before running this script.}"
: "${RSA_COGNITO_CLIENT_ID:?Set RSA_COGNITO_CLIENT_ID before running this script.}"

mkdir -p "$APP_ROOT/runtime" "$APP_ROOT/backups/env"

if [ -f "$ENV_FILE" ]; then
  BACKUP="$APP_ROOT/backups/env/backend.env.batch43.$(date -u +%Y%m%d%H%M%S).bak"
  cp "$ENV_FILE" "$BACKUP"
  printf 'Backed up existing env to: %s\n' "$BACKUP"
else
  printf 'Creating new runtime env file: %s\n' "$ENV_FILE"
fi

# Preserve non-managed keys while removing managed/auth/region/safety-sensitive entries.
TMP_FILE="$(mktemp)"
if [ -f "$ENV_FILE" ]; then
  grep -Ev '^(RSA_ENV|RSA_REPOSITORY_MODE|AWS_DEFAULT_REGION|AWS_REGION|RSA_ADMIN_AUTH_MODE|RSA_COGNITO_REGION|RSA_COGNITO_USER_POOL_ID|RSA_COGNITO_CLIENT_ID|RSA_COGNITO_JWKS_CACHE_SECONDS|RSA_CORS_ORIGINS|PYTHONUNBUFFERED|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN)=' "$ENV_FILE" > "$TMP_FILE" || true
fi

cat > "$ENV_FILE" <<ENV
# RSA CMS backend runtime environment for EC2 demo.
# Generated/updated by Batch 43.
# Do not put AWS access keys here. DynamoDB access uses the EC2 instance profile.
RSA_ENV=ec2-demo
RSA_REPOSITORY_MODE=dynamodb
AWS_DEFAULT_REGION=ap-southeast-1
AWS_REGION=ap-southeast-1
RSA_ADMIN_AUTH_MODE=cognito
RSA_COGNITO_REGION=${RSA_COGNITO_REGION}
RSA_COGNITO_USER_POOL_ID=${RSA_COGNITO_USER_POOL_ID}
RSA_COGNITO_CLIENT_ID=${RSA_COGNITO_CLIENT_ID}
RSA_COGNITO_JWKS_CACHE_SECONDS=3600
RSA_CORS_ORIGINS=*
PYTHONUNBUFFERED=1
ENV

if [ -s "$TMP_FILE" ]; then
  printf '\n# Preserved existing non-managed settings\n' >> "$ENV_FILE"
  cat "$TMP_FILE" >> "$ENV_FILE"
fi
rm -f "$TMP_FILE"

if grep -Eq 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN' "$ENV_FILE"; then
  echo "ERROR: AWS credential variable found in $ENV_FILE. Remove long-term AWS keys from EC2."
  exit 1
fi

chmod 640 "$ENV_FILE"
chown root:"$APP_USER" "$ENV_FILE"

printf '\nRuntime auth values now set to Cognito mode:\n'
grep -E '^(RSA_ENV|RSA_REPOSITORY_MODE|AWS_DEFAULT_REGION|AWS_REGION|RSA_ADMIN_AUTH_MODE|RSA_COGNITO_REGION|RSA_COGNITO_USER_POOL_ID|RSA_COGNITO_CLIENT_ID)=' "$ENV_FILE"

printf '\nRestarting backend service...\n'
systemctl daemon-reload
systemctl restart "$SERVICE"
sleep 5
systemctl --no-pager --full status "$SERVICE" | sed -n '1,28p' || true

printf '\nLocal backend auth config check:\n'
if curl -fsS --max-time 8 http://127.0.0.1:8000/api/admin/auth/config; then
  printf '\nOK: backend auth config responded locally.\n'
else
  printf '\nWARN: backend auth config did not respond locally. Check logs with:\n'
  printf '  sudo journalctl -u %s -n 120 --no-pager\n' "$SERVICE"
fi

printf '\nBatch 43 Cognito runtime env update completed.\n'
