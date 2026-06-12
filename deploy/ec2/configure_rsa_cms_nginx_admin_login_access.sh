#!/usr/bin/env bash
set -euo pipefail

echo "RSA CMS Batch 44 - Configure Nginx protected admin-login access"
echo "This exposes the admin static UI and admin auth endpoints only."
echo "Management/admin data APIs remain blocked until the protected API exposure batch."

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run with sudo: sudo /tmp/configure_rsa_cms_nginx_admin_login_access.sh" >&2
  exit 1
fi

APP_ROOT="/opt/rsa-cms/current"
FRONTEND_ROOT="${APP_ROOT}/frontend"
NGINX_SITE="/etc/nginx/sites-available/rsa-cms.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/rsa-cms.conf"
BACKUP_DIR="/opt/rsa-cms/backups/nginx"
BACKUP_FILE="${BACKUP_DIR}/rsa-cms.conf.batch44.$(date -u +%Y%m%d%H%M%S).bak"

if [[ ! -d "${FRONTEND_ROOT}" ]]; then
  echo "ERROR: frontend root not found: ${FRONTEND_ROOT}" >&2
  exit 1
fi

if [[ ! -f "${FRONTEND_ROOT}/admin/login.html" ]]; then
  echo "ERROR: admin login page not found: ${FRONTEND_ROOT}/admin/login.html" >&2
  echo "Deploy Batch 42+ frontend files to EC2 before Batch 44." >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  echo "ERROR: nginx is not installed. Run Batch 37 first." >&2
  exit 1
fi

mkdir -p "${BACKUP_DIR}"
if [[ -f "${NGINX_SITE}" ]]; then
  cp "${NGINX_SITE}" "${BACKUP_FILE}"
  echo "Backed up previous config to: ${BACKUP_FILE}"
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

    # Admin static UI. Browser-side guard redirects anonymous users to login.
    # Admin data/management APIs remain blocked below unless explicitly allowed.
    location = /admin {
        return 301 /admin/;
    }

    location ^~ /admin/ {
        try_files $uri $uri/ =404;
    }

    # Public health/API routes.
    location = /api/health {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/products {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/brands {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/categories {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/key-features {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/package-banners {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/about {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/project-gallery {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/services {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/contact {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/contact-persons {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/social-media {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/pages/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Public form endpoints: allow creation only. Block list/detail/update/delete access.
    location = /api/bookings {
        limit_except POST { deny all; }
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /api/bookings/ {
        limit_except POST { deny all; }
        proxy_pass http://127.0.0.1:8000/api/bookings;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/bookings/ {
        return 403;
    }

    location = /api/inquiries {
        limit_except POST { deny all; }
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /api/inquiries/ {
        limit_except POST { deny all; }
        proxy_pass http://127.0.0.1:8000/api/inquiries;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/inquiries/ {
        return 403;
    }

    # Publicly expose only admin authentication endpoints needed by login.html.
    # They return public-safe config, anonymous status, or Cognito login responses.
    location ^~ /api/admin/auth/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Keep all other admin and CRM management APIs blocked until the protected
    # admin API exposure batch verifies backend JWT enforcement end-to-end.
    location = /api/admin {
        return 403;
    }
    location ^~ /api/admin/ {
        return 403;
    }
    location ^~ /api/customers {
        return 403;
    }

    # Keep developer docs blocked publicly.
    location = /docs {
        return 403;
    }
    location ^~ /docs/ {
        return 403;
    }
    location = /redoc {
        return 403;
    }
    location = /openapi.json {
        return 403;
    }

    # Any unapproved API route is blocked by default.
    location ^~ /api/ {
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
systemctl reload nginx

echo "Batch 44 admin login Nginx access configured and reloaded."
echo "Run: /tmp/check_rsa_cms_nginx_admin_login_access.sh"
