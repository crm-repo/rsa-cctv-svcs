#!/usr/bin/env bash
set -euo pipefail

echo "RSA CMS Batch 46 - Configure Nginx protected admin API access"
echo "This exposes admin/CRM API paths through Nginx, relying on backend Cognito JWT enforcement."
echo "Anonymous admin/CRM data API requests should return 401, not 200."

if [[ "${EUID}" -ne 0 ]]; then
  echo "ERROR: run with sudo: sudo /tmp/configure_rsa_cms_nginx_protected_admin_api_access.sh" >&2
  exit 1
fi

APP_ROOT="/opt/rsa-cms/current"
FRONTEND_ROOT="${APP_ROOT}/frontend"
NGINX_SITE="/etc/nginx/sites-available/rsa-cms.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/rsa-cms.conf"
SNIPPET="/etc/nginx/snippets/rsa-cms-proxy-headers.conf"
BACKUP_DIR="/opt/rsa-cms/backups/nginx"
BACKUP_FILE="${BACKUP_DIR}/rsa-cms.conf.batch46.$(date -u +%Y%m%d%H%M%S).bak"

if [[ ! -d "${FRONTEND_ROOT}" ]]; then
  echo "ERROR: frontend root not found: ${FRONTEND_ROOT}" >&2
  exit 1
fi

if [[ ! -f "${FRONTEND_ROOT}/admin/login.html" ]]; then
  echo "ERROR: admin login page not found: ${FRONTEND_ROOT}/admin/login.html" >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  echo "ERROR: nginx is not installed. Run Batch 37 first." >&2
  exit 1
fi

mkdir -p "${BACKUP_DIR}" /etc/nginx/snippets
if [[ -f "${NGINX_SITE}" ]]; then
  cp "${NGINX_SITE}" "${BACKUP_FILE}"
  echo "Backed up previous config to: ${BACKUP_FILE}"
fi

cat > "${SNIPPET}" <<'NGINXSNIPPET'
proxy_http_version 1.1;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
NGINXSNIPPET

cat > "${NGINX_SITE}" <<'NGINXCONF'
server {
    client_max_body_size 8m;  # batch56b-media-upload-size-limit
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
    # Backend/Nginx API protection below prevents anonymous data access.
    location = /admin {
        return 301 /admin/;
    }

    location ^~ /admin/ {
        try_files $uri $uri/ =404;
    }

    # Public health/API routes.
    location = /api/health {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    location ~ ^/api/(products|brands|categories|key-features|package-banners|about|project-gallery|services|contact|contact-persons|social-media)(/|$) {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    location ^~ /api/pages/ {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    # batch56b-media-public-route: allow public media display paths
    location ^~ /api/media/ {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    # Public admin authentication endpoints needed by login.html.
    location ^~ /api/admin/auth/ {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    # Protected admin data APIs. Backend middleware must enforce Cognito bearer tokens.
    location ^~ /api/admin/ {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    # Protected CRM/lead management APIs. Public POST form exceptions are enforced by backend middleware.
    location ^~ /api/customers {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    location ^~ /api/bookings {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
    }

    location ^~ /api/inquiries {
        proxy_pass http://127.0.0.1:8000;
        include /etc/nginx/snippets/rsa-cms-proxy-headers.conf;
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
	location /api/ {
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

echo "Batch 46 protected admin API Nginx access configured and reloaded."
echo "Run: /tmp/check_rsa_cms_nginx_protected_admin_api_access.sh"
