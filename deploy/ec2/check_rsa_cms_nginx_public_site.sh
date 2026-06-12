#!/usr/bin/env bash
set -euo pipefail

echo "RSA CMS Batch 37 Nginx public site check"
echo "Mode: READ ONLY"

failures=0
check_path() {
  local path="$1"
  if [[ -e "$path" ]]; then
    echo "OK: $path"
  else
    echo "FAIL: missing $path"
    failures=$((failures + 1))
  fi
}

status_code() {
  local url="$1"
  curl -s -o /tmp/rsa_cms_check_body.txt -w "%{http_code}" "$url" || true
}

echo
printf '== Files ==\n'
check_path /opt/rsa-cms/current/frontend/index.html
check_path /etc/nginx/sites-available/rsa-cms.conf
check_path /etc/nginx/sites-enabled/rsa-cms.conf

echo
printf '== Services ==\n'
if systemctl is-active --quiet rsa-cms-backend.service; then
  echo "OK: rsa-cms-backend.service active"
else
  echo "FAIL: rsa-cms-backend.service not active"
  failures=$((failures + 1))
  systemctl status rsa-cms-backend.service --no-pager || true
fi

if systemctl is-active --quiet nginx; then
  echo "OK: nginx active"
else
  echo "FAIL: nginx not active"
  failures=$((failures + 1))
  systemctl status nginx --no-pager || true
fi

if nginx -t >/tmp/rsa_cms_nginx_test.log 2>&1; then
  echo "OK: nginx config test passed"
else
  echo "FAIL: nginx config test failed"
  failures=$((failures + 1))
  cat /tmp/rsa_cms_nginx_test.log
fi

echo
printf '== Local HTTP checks ==\n'
code=$(status_code http://127.0.0.1/)
echo "GET / -> HTTP $code"
if [[ "$code" != "200" ]]; then failures=$((failures + 1)); fi

code=$(status_code http://127.0.0.1/api/health)
echo "GET /api/health -> HTTP $code"
if [[ "$code" != "200" ]]; then failures=$((failures + 1)); fi
cat /tmp/rsa_cms_check_body.txt || true
printf '\n'

code=$(status_code http://127.0.0.1/api/products)
echo "GET /api/products -> HTTP $code"
if [[ "$code" != "200" ]]; then failures=$((failures + 1)); fi

code=$(status_code http://127.0.0.1/admin/)
echo "GET /admin/ -> HTTP $code"
if [[ "$code" != "403" ]]; then
  echo "FAIL: admin should be blocked publicly until Cognito/JWT enforcement is enabled."
  failures=$((failures + 1))
fi

echo
printf '== Recent nginx logs ==\n'
tail -n 20 /var/log/nginx/rsa-cms-access.log 2>/dev/null || true

echo
if [[ "$failures" -eq 0 ]]; then
  echo "Batch 37 Nginx public-site local check passed."
else
  echo "Batch 37 Nginx public-site local check completed with ${failures} issue(s)."
  exit 1
fi
