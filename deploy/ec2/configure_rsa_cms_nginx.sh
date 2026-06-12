#!/usr/bin/env bash
set -euo pipefail

echo "RSA CMS Batch 37 - Configure Nginx public site proxy"
echo "This script configures nginx on the EC2 instance."

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run with sudo: sudo /tmp/configure_rsa_cms_nginx.sh" >&2
  exit 1
fi

APP_ROOT="/opt/rsa-cms/current"
FRONTEND_ROOT="${APP_ROOT}/frontend"
NGINX_SITE="/etc/nginx/sites-available/rsa-cms.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/rsa-cms.conf"

if [[ ! -d "${FRONTEND_ROOT}" ]]; then
  echo "ERROR: frontend root not found: ${FRONTEND_ROOT}" >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  echo "Installing nginx..."
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
else
  echo "nginx already installed."
fi

cat > "${NGINX_SITE}" <<'NGINXCONF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;
    root /opt/rsa-cms/current/frontend;
    index index.html;

    access_log /var/log/nginx/rsa-cms-access.log;
    error_log /var/log/nginx/rsa-cms-error.log;

    # Public website static pages.
    location / {
        try_files $uri $uri/ =404;
    }

    # Public API proxy to local FastAPI service.
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin UI must not be public while Cognito/JWT enforcement is not enabled.
    location ^~ /admin/ {
        return 403;
    }
    location = /admin {
        return 403;
    }

    # Avoid exposing hidden/local files.
    location ~ /\. {
        deny all;
    }
}
NGINXCONF

rm -f /etc/nginx/sites-enabled/default
ln -sfn "${NGINX_SITE}" "${NGINX_ENABLED}"

nginx -t
systemctl enable nginx
systemctl restart nginx

echo "Nginx configured and restarted."
echo "Run: /tmp/check_rsa_cms_nginx_public_site.sh"
