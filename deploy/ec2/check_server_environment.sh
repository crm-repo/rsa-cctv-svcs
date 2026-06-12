#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/rsa-cms"

echo "RSA CMS Batch 35 server environment check"
echo "Mode: READ ONLY"
echo

echo "== OS =="
if [ -f /etc/os-release ]; then
  cat /etc/os-release | sed -n 's/^PRETTY_NAME=//p' | tr -d '"'
else
  uname -a
fi

echo
echo "== User =="
whoami
id

echo
echo "== Required commands =="
for cmd in python3 pip3 git curl unzip tar; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "OK: $cmd -> $(command -v "$cmd")"
  else
    echo "MISSING: $cmd"
  fi
done

echo
echo "== Python versions =="
python3 --version || true
pip3 --version || true
if [ -x "$APP_ROOT/venv/bin/python" ]; then
  "$APP_ROOT/venv/bin/python" --version
  "$APP_ROOT/venv/bin/pip" --version
else
  echo "MISSING: $APP_ROOT/venv/bin/python"
fi

echo
echo "== App folders =="
for path in "$APP_ROOT" "$APP_ROOT/backend" "$APP_ROOT/frontend" "$APP_ROOT/deploy" "$APP_ROOT/logs" "$APP_ROOT/runtime" "$APP_ROOT/backups" "$APP_ROOT/venv"; do
  if [ -d "$path" ]; then
    echo "OK: $path"
  else
    echo "MISSING: $path"
  fi
done

echo
echo "== AWS credential safety check =="
if [ -f "$HOME/.aws/credentials" ]; then
  echo "WARN: $HOME/.aws/credentials exists. Do not store long-term AWS keys on EC2."
else
  echo "OK: no $HOME/.aws/credentials file found."
fi

echo
echo "== EC2 instance profile metadata =="
TOKEN=""
TOKEN=$(curl -s -m 2 -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)
if [ -n "$TOKEN" ]; then
  ROLE_NAME=$(curl -s -m 2 -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/iam/security-credentials/" || true)
  if [ -n "$ROLE_NAME" ]; then
    echo "OK: instance profile role visible: $ROLE_NAME"
  else
    echo "WARN: no instance profile role name returned from metadata."
  fi
else
  echo "WARN: could not get IMDSv2 token. Metadata may be unavailable."
fi

echo
echo "== AWS CLI optional check =="
if command -v aws >/dev/null 2>&1; then
  aws --version || true
  aws sts get-caller-identity --region ap-southeast-1 || echo "WARN: aws sts check failed. This may need AWS CLI/config or IAM role propagation."
else
  echo "INFO: AWS CLI not installed. This is acceptable for app runtime if Python/boto3 uses the instance profile later."
fi

echo
echo "Batch 35 server environment check completed."
