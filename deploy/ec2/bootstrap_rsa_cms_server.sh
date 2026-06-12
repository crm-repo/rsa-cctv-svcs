#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"
APP_USER="${SUDO_USER:-$USER}"

printf '\nRSA CMS Batch 35 server bootstrap\n'
printf 'This script installs basic server packages and creates app folders.\n'
printf 'It does not deploy the application and does not store AWS keys.\n\n'

if [ "$(id -u)" -eq 0 ]; then
  echo "Do not run this script directly as root. Run it as ec2-user/ubuntu; it will use sudo when needed."
  exit 1
fi

install_packages_dnf() {
  sudo dnf install -y python3 python3-pip git curl unzip tar
}

install_packages_yum() {
  sudo yum install -y python3 python3-pip git curl unzip tar
}

install_packages_apt() {
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-pip python3-venv git curl unzip tar
}

if command -v dnf >/dev/null 2>&1; then
  install_packages_dnf
elif command -v yum >/dev/null 2>&1; then
  install_packages_yum
elif command -v apt-get >/dev/null 2>&1; then
  install_packages_apt
else
  echo "ERROR: could not find dnf, yum, or apt-get. Install Python/Git/curl/unzip manually."
  exit 1
fi

sudo mkdir -p \
  "$APP_ROOT" \
  "$APP_ROOT/backend" \
  "$APP_ROOT/frontend" \
  "$APP_ROOT/deploy" \
  "$APP_ROOT/logs" \
  "$APP_ROOT/runtime" \
  "$APP_ROOT/backups"

sudo chown -R "$APP_USER":"$APP_USER" "$APP_ROOT"

if [ ! -d "$APP_ROOT/venv" ]; then
  python3 -m venv "$APP_ROOT/venv"
fi

"$APP_ROOT/venv/bin/python" -m pip install --upgrade pip setuptools wheel

cat > "$APP_ROOT/README_SERVER_ENVIRONMENT.txt" <<README
RSA CMS EC2 server environment prepared by Batch 35.

Do not store AWS access keys here.
Use the EC2 instance profile for DynamoDB access.
Application deployment is handled in a later batch.
README

printf '\nBootstrap complete.\n'
printf 'Prepared folders under %s\n' "$APP_ROOT"
printf 'Run: /tmp/check_server_environment.sh\n'
