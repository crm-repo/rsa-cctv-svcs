#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"
RELEASE_ZIP="/tmp/rsa-cms-release.zip"
SERVICE_SRC="/tmp/rsa-cms-backend.service"
ENV_FILE="$APP_ROOT/runtime/backend.env"
APP_USER="ubuntu"
if id ec2-user >/dev/null 2>&1; then
  APP_USER="ec2-user"
fi
if id ubuntu >/dev/null 2>&1; then
  APP_USER="ubuntu"
fi
TIMESTAMP="$(date -u +%Y%m%d%H%M%S)"
RELEASE_DIR="$APP_ROOT/releases/$TIMESTAMP"
CURRENT_LINK="$APP_ROOT/current"
VENV_DIR="$APP_ROOT/venv"

printf '\nRSA CMS Batch 36 app release installer\n'
printf 'This script deploys the Git archive to EC2 and configures the backend service.\n'
printf 'It does not store AWS access keys and does not create AWS resources.\n\n'

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: run through sudo: sudo /tmp/install_rsa_cms_release.sh"
  exit 1
fi

if [ ! -f "$RELEASE_ZIP" ]; then
  echo "ERROR: release zip missing: $RELEASE_ZIP"
  exit 1
fi

if [ ! -f "$SERVICE_SRC" ]; then
  echo "ERROR: service file missing: $SERVICE_SRC"
  exit 1
fi

mkdir -p "$APP_ROOT/releases" "$APP_ROOT/runtime" "$APP_ROOT/logs" "$APP_ROOT/backups"
mkdir -p "$RELEASE_DIR"
unzip -q "$RELEASE_ZIP" -d "$RELEASE_DIR"
chown -R "$APP_USER:$APP_USER" "$APP_ROOT"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
fi

sudo -u "$APP_USER" "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
if [ -f "$RELEASE_DIR/backend/requirements.txt" ]; then
  sudo -u "$APP_USER" "$VENV_DIR/bin/python" -m pip install -r "$RELEASE_DIR/backend/requirements.txt"
else
  echo "ERROR: backend/requirements.txt not found in release package."
  exit 1
fi

ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"
chown -h "$APP_USER:$APP_USER" "$CURRENT_LINK"

if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<'ENV'
# RSA CMS backend runtime environment for EC2 demo.
# Do not put AWS access keys here. DynamoDB access uses the EC2 instance profile.
RSA_ENV=ec2-demo
RSA_REPOSITORY_MODE=dynamodb
AWS_DEFAULT_REGION=ap-southeast-1
AWS_REGION=ap-southeast-1
RSA_ADMIN_AUTH_MODE=disabled
RSA_CORS_ORIGINS=*
PYTHONUNBUFFERED=1
ENV
  chmod 640 "$ENV_FILE"
  chown root:"$APP_USER" "$ENV_FILE"
else
  echo "Keeping existing runtime env file: $ENV_FILE"
fi

install -m 0644 "$SERVICE_SRC" /etc/systemd/system/rsa-cms-backend.service
systemctl daemon-reload
systemctl enable rsa-cms-backend.service
systemctl restart rsa-cms-backend.service

printf '\nWaiting for backend service to settle...\n'
sleep 5
systemctl --no-pager --full status rsa-cms-backend.service || true

printf '\nLocal health check:\n'
if curl -fsS --max-time 8 http://127.0.0.1:8000/api/health; then
  printf '\nOK: backend /api/health responded locally.\n'
else
  printf '\nWARN: backend /api/health did not respond locally. Check logs with:\n'
  printf '  sudo journalctl -u rsa-cms-backend -n 120 --no-pager\n'
fi

printf '\nDeployment complete.\n'
printf 'Current release: %s\n' "$RELEASE_DIR"
printf 'Current symlink: %s\n' "$CURRENT_LINK"
printf 'Service: rsa-cms-backend.service\n'
printf 'Run runtime check: /tmp/check_rsa_cms_app_runtime.sh\n'
