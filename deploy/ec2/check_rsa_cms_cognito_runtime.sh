#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"
ENV_FILE="$APP_ROOT/runtime/backend.env"
SERVICE="rsa-cms-backend.service"
ISSUES=0

check_ok() {
  if "$@"; then
    return 0
  fi
  ISSUES=$((ISSUES + 1))
  return 1
}

http_code() {
  local url="$1"
  curl -sS -o /tmp/rsa_cms_batch43_body.txt -w '%{http_code}' --max-time 8 "$url" || printf '000'
}

printf 'RSA CMS Batch 43 Cognito backend runtime check\n'
printf 'Mode: READ ONLY\n\n'

printf '== Runtime env file ==\n'
if [ -f "$ENV_FILE" ]; then
  printf 'OK: %s exists\n' "$ENV_FILE"
  if grep -Eq 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN' "$ENV_FILE"; then
    printf 'FAIL: AWS credential variable found in backend.env.\n'
    ISSUES=$((ISSUES + 1))
  else
    printf 'OK: no AWS access-key variables found in backend.env\n'
  fi
  grep -E '^(RSA_ENV|RSA_REPOSITORY_MODE|AWS_DEFAULT_REGION|AWS_REGION|RSA_ADMIN_AUTH_MODE|RSA_COGNITO_REGION|RSA_COGNITO_USER_POOL_ID|RSA_COGNITO_CLIENT_ID)=' "$ENV_FILE" || true
else
  printf 'FAIL: missing %s\n' "$ENV_FILE"
  ISSUES=$((ISSUES + 1))
fi

printf '\n== Systemd service ==\n'
if systemctl is-active --quiet "$SERVICE"; then
  printf 'OK: %s active\n' "$SERVICE"
else
  printf 'FAIL: %s not active\n' "$SERVICE"
  ISSUES=$((ISSUES + 1))
fi
systemctl --no-pager --full status "$SERVICE" | sed -n '1,20p' || true

printf '\n== Local backend Cognito auth checks on port 8000 ==\n'
CODE=$(http_code 'http://127.0.0.1:8000/api/admin/auth/config')
printf 'GET /api/admin/auth/config -> HTTP %s\n' "$CODE"
if [ "$CODE" = "200" ]; then
  cat /tmp/rsa_cms_batch43_body.txt; printf '\n'
  if grep -q '"mode"[[:space:]]*:[[:space:]]*"cognito"' /tmp/rsa_cms_batch43_body.txt; then
    printf 'OK: backend auth mode is cognito\n'
  else
    printf 'FAIL: backend auth mode is not cognito\n'
    ISSUES=$((ISSUES + 1))
  fi
else
  printf 'FAIL: auth config did not return 200 locally\n'
  ISSUES=$((ISSUES + 1))
fi

CODE=$(http_code 'http://127.0.0.1:8000/api/admin/auth/status')
printf 'GET /api/admin/auth/status anonymous -> HTTP %s\n' "$CODE"
if [ "$CODE" = "200" ]; then
  cat /tmp/rsa_cms_batch43_body.txt; printf '\n'
  if grep -q '"authenticated"[[:space:]]*:[[:space:]]*false' /tmp/rsa_cms_batch43_body.txt; then
    printf 'OK: anonymous admin status is not authenticated\n'
  else
    printf 'FAIL: anonymous admin status did not return authenticated=false\n'
    ISSUES=$((ISSUES + 1))
  fi
else
  printf 'FAIL: anonymous auth status did not return 200 locally\n'
  ISSUES=$((ISSUES + 1))
fi

printf '\n== Local public API checks on backend port 8000 ==\n'
for path in /api/health /api/products /api/brands; do
  CODE=$(http_code "http://127.0.0.1:8000${path}")
  if [ "$CODE" = "200" ]; then
    printf 'OK: GET %s -> HTTP 200\n' "$path"
  else
    printf 'FAIL: GET %s -> HTTP %s\n' "$path" "$CODE"
    ISSUES=$((ISSUES + 1))
  fi
 done

printf '\n== Nginx local public lockdown check on port 80 ==\n'
for entry in \
  '/ 200' \
  '/api/health 200' \
  '/api/admin/auth/config 403' \
  '/api/admin/auth/status 403' \
  '/admin/ 403' \
  '/docs 403' \
  '/openapi.json 403'; do
  path="${entry% *}"
  expected="${entry#* }"
  CODE=$(http_code "http://127.0.0.1${path}")
  if [ "$CODE" = "$expected" ]; then
    printf 'OK: GET %s -> HTTP %s\n' "$path" "$CODE"
  else
    printf 'FAIL: GET %s -> HTTP %s, expected %s\n' "$path" "$CODE" "$expected"
    ISSUES=$((ISSUES + 1))
  fi
 done

printf '\n== Instance profile metadata ==\n'
TOKEN=""
TOKEN=$(curl -s -m 2 -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)
if [ -n "$TOKEN" ]; then
  ROLE_NAME=$(curl -s -m 2 -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/iam/security-credentials/" || true)
  if [ -n "$ROLE_NAME" ]; then
    printf 'OK: instance profile role visible: %s\n' "$ROLE_NAME"
  else
    printf 'WARN: no instance profile role returned.\n'
  fi
else
  printf 'WARN: could not get IMDSv2 token.\n'
fi

printf '\n== Recent backend logs ==\n'
sudo journalctl -u "$SERVICE" -n 30 --no-pager || true

rm -f /tmp/rsa_cms_batch43_body.txt

if [ "$ISSUES" -eq 0 ]; then
  printf '\nBatch 43 Cognito backend runtime check PASSED.\n'
  exit 0
fi

printf '\nBatch 43 Cognito backend runtime check completed with %s issue(s).\n' "$ISSUES"
exit 1
