#!/usr/bin/env bash
set -euo pipefail

ISSUES=0
BASE_URL="http://127.0.0.1"
BACKEND_URL="http://127.0.0.1:8000"

echo "RSA CMS Batch 38 Nginx API exposure lockdown check"
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
    curl -sS -o /tmp/rsa-cms-b38-body.txt -w "%{http_code}" \
      -X POST \
      -H "Content-Type: application/json" \
      --data '{"customer_name":"Batch 38 Smoke Test","contact_number":"0919 138 3800","email":"batch38.smoke@example.com","address":"Batch 38 EC2 smoke test","preferred_date":"2026-12-30","preferred_time":"Morning","service_interest":"CCTV Installation","notes":"Batch 38 public POST smoke test."}' \
      "$url" || true
  else
    curl -sS -o /tmp/rsa-cms-b38-body.txt -w "%{http_code}" "$url" || true
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
    head -c 300 /tmp/rsa-cms-b38-body.txt || true
    echo
    ISSUES=$((ISSUES + 1))
  fi
}

echo
printf '== Files ==\n'
check_file /opt/rsa-cms/current/frontend/index.html
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

if sudo nginx -t >/tmp/rsa-cms-b38-nginx-test.txt 2>&1; then
  echo "OK: nginx config test successful"
else
  echo "FAIL: nginx config test failed"
  cat /tmp/rsa-cms-b38-nginx-test.txt
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
printf '== Blocked admin/management checks through Nginx ==\n'
expect_status GET /admin/ 403
expect_status GET /api/admin/products 403
expect_status GET /api/customers 403
expect_status GET /api/bookings 403
expect_status GET /api/inquiries 403
expect_status GET /docs 403
expect_status GET /openapi.json 403

echo
printf '== Internal backend check ==\n'
backend_status=$(curl -sS -o /tmp/rsa-cms-b38-backend-body.txt -w "%{http_code}" "${BACKEND_URL}/api/health" || true)
echo "GET ${BACKEND_URL}/api/health -> HTTP ${backend_status} (expected 200 internal only)"
if [[ "$backend_status" != "200" ]]; then
  ISSUES=$((ISSUES + 1))
fi

echo
printf '== Recent nginx logs ==\n'
tail -n 12 /var/log/nginx/rsa-cms-access.log 2>/dev/null || true

if [[ "$ISSUES" -eq 0 ]]; then
  echo
  echo "Batch 38 Nginx API exposure lockdown check PASSED."
else
  echo
  echo "Batch 38 Nginx API exposure lockdown check completed with ${ISSUES} issue(s)."
fi

exit "$ISSUES"
