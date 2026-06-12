#!/usr/bin/env bash
set -euo pipefail

ISSUES=0
BASE_URL="http://127.0.0.1"
BACKEND_URL="http://127.0.0.1:8000"

echo "RSA CMS Batch 44 Nginx admin-login access check"
echo "Mode: READ ONLY"

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
    curl -sS -o /tmp/rsa-cms-b44-body.txt -w "%{http_code}" \
      -X POST \
      -H "Content-Type: application/json" \
      --data '{"username":"batch44.invalid@example.com","password":"DefinitelyWrong#2026"}' \
      "$url" || true
  else
    curl -sS -o /tmp/rsa-cms-b44-body.txt -w "%{http_code}" "$url" || true
  fi
}

expect_status() {
  local method="$1"
  local path="$2"
  local expected="$3"
  local status
  status=$(http_status "$method" "${BASE_URL}${path}")
  echo "${method} ${path} -> HTTP ${status} (expected ${expected})"
  if [[ "$status" != "$expected" ]]; then
    echo "  Body preview:"
    head -c 500 /tmp/rsa-cms-b44-body.txt || true
    echo
    ISSUES=$((ISSUES + 1))
  fi
}

expect_status_one_of() {
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
    head -c 500 /tmp/rsa-cms-b44-body.txt || true
    echo
    ISSUES=$((ISSUES + 1))
  fi
}

echo
printf '== Files ==\n'
check_file /opt/rsa-cms/current/frontend/index.html
check_file /opt/rsa-cms/current/frontend/admin/login.html
check_file /opt/rsa-cms/current/frontend/admin/index.html
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

if sudo nginx -t >/tmp/rsa-cms-b44-nginx-test.txt 2>&1; then
  echo "OK: nginx config test successful"
else
  echo "FAIL: nginx config test failed"
  cat /tmp/rsa-cms-b44-nginx-test.txt
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
printf '== Admin UI/auth exposure checks through Nginx ==\n'
expect_status GET /admin/ 200
expect_status GET /admin/login.html 200
expect_status GET /admin/assets/js/admin-auth.js 200
expect_status GET /api/admin/auth/config 200
expect_status GET /api/admin/auth/status 200
# Invalid Cognito credentials should reach backend and fail auth, not be blocked by Nginx.
expect_status_one_of POST /api/admin/auth/cognito-login 400 401 422

echo
printf '== Still-blocked admin/management checks through Nginx ==\n'
expect_status GET /api/admin/products 403
expect_status GET /api/customers 403
expect_status GET /api/bookings 403
expect_status GET /api/inquiries 403
expect_status GET /docs 403
expect_status GET /redoc 403
expect_status GET /openapi.json 403

echo
printf '== Internal backend auth check on port 8000 ==\n'
backend_status=$(curl -sS -o /tmp/rsa-cms-b44-backend-body.txt -w "%{http_code}" "${BACKEND_URL}/api/admin/auth/config" || true)
echo "GET ${BACKEND_URL}/api/admin/auth/config -> HTTP ${backend_status} (expected 200 internal)"
if [[ "$backend_status" != "200" ]]; then
  ISSUES=$((ISSUES + 1))
else
  if grep -q '"mode":"cognito"' /tmp/rsa-cms-b44-backend-body.txt || grep -q '"mode": "cognito"' /tmp/rsa-cms-b44-backend-body.txt; then
    echo "OK: backend auth config is Cognito mode"
  else
    echo "FAIL: backend auth config does not show Cognito mode"
    cat /tmp/rsa-cms-b44-backend-body.txt
    ISSUES=$((ISSUES + 1))
  fi
fi

echo
printf '== Recent nginx logs ==\n'
tail -n 14 /var/log/nginx/rsa-cms-access.log 2>/dev/null || true

if [[ "$ISSUES" -eq 0 ]]; then
  echo
  echo "Batch 44 Nginx admin-login access check PASSED."
else
  echo
  echo "Batch 44 Nginx admin-login access check completed with ${ISSUES} issue(s)."
fi

exit "$ISSUES"
