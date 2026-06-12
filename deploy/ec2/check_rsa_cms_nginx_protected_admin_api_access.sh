#!/usr/bin/env bash
set -euo pipefail

ISSUES=0
BASE_URL="http://127.0.0.1"
BACKEND_URL="http://127.0.0.1:8000"

echo "RSA CMS Batch 46 Nginx protected admin API access check"
echo "Mode: READ ONLY anonymous/protection checks"

check_file() {
  local path="$1"
  if [[ -e "$path" ]]; then
    echo "OK: $path"
  else
    echo "FAIL: missing $path"
    ISSUES=$((ISSUES + 1))
  fi
}

http_status() {
  local method="$1"
  local url="$2"
  if [[ "$method" == "POST" ]]; then
    curl -sS -o /tmp/rsa-cms-b46-body.txt -w "%{http_code}" \
      -X POST \
      -H "Content-Type: application/json" \
      --data '{"username":"batch46.invalid@example.com","password":"DefinitelyWrong#2026"}' \
      "$url" || true
  else
    curl -sS -o /tmp/rsa-cms-b46-body.txt -w "%{http_code}" "$url" || true
  fi
}

expect_status() {
  local method="$1"
  local path="$2"
  shift 2
  local expected_values=("$@")
  local status
  status=$(http_status "$method" "${BASE_URL}${path}")
  echo "${method} ${path} -> HTTP ${status} (expected one of: ${expected_values[*]})"
  local ok=0
  for expected in "${expected_values[@]}"; do
    if [[ "$status" == "$expected" ]]; then ok=1; fi
  done
  if [[ "$ok" -ne 1 ]]; then
    echo "  Body preview:"
    head -c 500 /tmp/rsa-cms-b46-body.txt || true
    echo
    ISSUES=$((ISSUES + 1))
  fi
}

echo
printf '== Files ==\n'
check_file /opt/rsa-cms/current/frontend/index.html
check_file /opt/rsa-cms/current/frontend/admin/login.html
check_file /opt/rsa-cms/current/backend/app/middleware/admin_route_auth.py
check_file /etc/nginx/sites-available/rsa-cms.conf
check_file /etc/nginx/sites-enabled/rsa-cms.conf

echo
printf '== Services ==\n'
if systemctl is-active --quiet rsa-cms-backend.service; then
  echo "OK: rsa-cms-backend.service active"
else
  echo "FAIL: rsa-cms-backend.service not active"
  ISSUES=$((ISSUES + 1))
fi

if systemctl is-active --quiet nginx; then
  echo "OK: nginx active"
else
  echo "FAIL: nginx not active"
  ISSUES=$((ISSUES + 1))
fi

if sudo nginx -t >/tmp/rsa-cms-b46-nginx-test.txt 2>&1; then
  echo "OK: nginx config test successful"
else
  echo "FAIL: nginx config test failed"
  cat /tmp/rsa-cms-b46-nginx-test.txt
  ISSUES=$((ISSUES + 1))
fi

echo
printf '== Public website/API checks through Nginx ==\n'
expect_status GET / 200
expect_status GET /products.html 200
expect_status GET /booking.html 200
expect_status GET /api/health 200
expect_status GET /api/products 200
expect_status GET /api/brands 200
expect_status GET /api/pages/contact 200

echo
printf '== Admin UI/auth checks through Nginx ==\n'
expect_status GET /admin/ 200
expect_status GET /admin/login.html 200
expect_status GET /api/admin/auth/config 200
expect_status GET /api/admin/auth/status 200
expect_status POST /api/admin/auth/cognito-login 400 401 422

echo
printf '== Anonymous protected API checks through Nginx ==\n'
# These should now reach backend and fail with 401, not be blocked by Nginx with 403 and never return 200 anonymously.
expect_status GET /api/admin/products 401
expect_status GET /api/admin/categories 401
expect_status GET /api/admin/brands 401
expect_status GET /api/admin/key-features 401
expect_status GET /api/admin/about 401
expect_status GET /api/admin/project-gallery 401
expect_status GET /api/admin/services 401
expect_status GET /api/admin/contact-us 401
expect_status GET /api/admin/media/config 401
expect_status GET /api/customers 401
expect_status GET /api/bookings 401
expect_status GET /api/inquiries 401

echo
printf '== Still-blocked developer surfaces ==\n'
expect_status GET /docs 403
expect_status GET /redoc 403
expect_status GET /openapi.json 403

echo
printf '== Internal backend auth check on port 8000 ==\n'
backend_status=$(curl -sS -o /tmp/rsa-cms-b46-backend-body.txt -w "%{http_code}" "${BACKEND_URL}/api/admin/products" || true)
echo "GET ${BACKEND_URL}/api/admin/products anonymous -> HTTP ${backend_status} (expected 401 internal)"
if [[ "$backend_status" != "401" ]]; then
  echo "  Body preview:"
  head -c 500 /tmp/rsa-cms-b46-backend-body.txt || true
  echo
  ISSUES=$((ISSUES + 1))
fi

echo
printf '== Recent nginx logs ==\n'
tail -n 16 /var/log/nginx/rsa-cms-access.log 2>/dev/null || true

if [[ "$ISSUES" -eq 0 ]]; then
  echo
  echo "Batch 46 Nginx protected admin API access check PASSED."
else
  echo
  echo "Batch 46 Nginx protected admin API access check completed with ${ISSUES} issue(s)."
fi

exit "$ISSUES"
