#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"
SERVICE="rsa-cms-backend.service"

printf 'RSA CMS Batch 36 app runtime check\n'
printf 'Mode: READ ONLY\n\n'

printf '== OS ==\n'
if [ -f /etc/os-release ]; then
  sed -n 's/^PRETTY_NAME=//p' /etc/os-release | tr -d '"'
else
  uname -a
fi

printf '\n== User ==\n'
whoami
id

printf '\n== App release folders ==\n'
for path in "$APP_ROOT" "$APP_ROOT/releases" "$APP_ROOT/current" "$APP_ROOT/current/backend" "$APP_ROOT/current/frontend" "$APP_ROOT/runtime" "$APP_ROOT/logs" "$APP_ROOT/venv"; do
  if [ -e "$path" ]; then
    printf 'OK: %s\n' "$path"
  else
    printf 'MISSING: %s\n' "$path"
  fi
done

printf '\n== Runtime env safety ==\n'
if [ -f "$APP_ROOT/runtime/backend.env" ]; then
  printf 'OK: %s exists\n' "$APP_ROOT/runtime/backend.env"
  if grep -Eq 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN' "$APP_ROOT/runtime/backend.env"; then
    printf 'WARN: AWS credential variable found in backend.env. Remove long-term AWS keys from EC2.\n'
  else
    printf 'OK: no AWS access-key variables found in backend.env\n'
  fi
  grep -E '^(RSA_ENV|RSA_REPOSITORY_MODE|AWS_DEFAULT_REGION|AWS_REGION|RSA_ADMIN_AUTH_MODE)=' "$APP_ROOT/runtime/backend.env" || true
else
  printf 'MISSING: %s\n' "$APP_ROOT/runtime/backend.env"
fi

printf '\n== Python/venv ==\n'
if [ -x "$APP_ROOT/venv/bin/python" ]; then
  "$APP_ROOT/venv/bin/python" --version
  "$APP_ROOT/venv/bin/pip" --version
else
  printf 'MISSING: venv python\n'
fi

printf '\n== Systemd service ==\n'
if systemctl list-unit-files "$SERVICE" >/dev/null 2>&1; then
  systemctl is-enabled "$SERVICE" || true
  systemctl is-active "$SERVICE" || true
  systemctl --no-pager --full status "$SERVICE" | sed -n '1,25p' || true
else
  printf 'MISSING: %s\n' "$SERVICE"
fi

printf '\n== Local backend health ==\n'
if curl -fsS --max-time 8 http://127.0.0.1:8000/api/health; then
  printf '\nOK: local /api/health responded\n'
else
  printf '\nWARN: local /api/health failed\n'
fi

printf '\n== Local public API smoke ==\n'
for url in \
  http://127.0.0.1:8000/api/products \
  http://127.0.0.1:8000/api/brands \
  http://127.0.0.1:8000/api/pages/contact; do
  if curl -fsS --max-time 8 "$url" >/dev/null; then
    printf 'OK: %s\n' "$url"
  else
    printf 'WARN: failed: %s\n' "$url"
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
sudo journalctl -u "$SERVICE" -n 40 --no-pager || true

printf '\nBatch 36 app runtime check completed.\n'
