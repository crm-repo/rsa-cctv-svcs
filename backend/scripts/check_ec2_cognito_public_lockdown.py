"""Batch 43 public EC2 Cognito/admin lockdown check.

Read-only smoke test from local machine after the EC2 backend has been
redeployed in Cognito mode. Public/admin routes should remain blocked by Nginx.
"""

from __future__ import annotations

import argparse
import socket
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlunparse


def request_code(url: str, timeout: int = 10) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "rsa-cms-batch43-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(500).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        body = exc.read(500).decode("utf-8", errors="replace")
        return exc.code, body
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        return None, str(exc)


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def direct_8000_url(base_url: str, path: str) -> str:
    parsed = urlparse(base_url)
    host = parsed.hostname or ""
    return urlunparse((parsed.scheme or "http", f"{host}:8000", path, "", "", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Batch 43 public EC2 Cognito/admin lockdown.")
    parser.add_argument("--base-url", required=True, help="EC2 public base URL, for example http://54.179.42.39")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    issues = 0

    print("RSA CMS / Mini-CRM Batch 43 Public Cognito/Admin Lockdown Check")
    print("Mode: READ ONLY")
    print(f"Base URL: {base_url}\n")

    print("== Public website/API still allowed through Nginx ==")
    allowed = [
        "/",
        "/products.html",
        "/booking.html",
        "/api/health",
        "/api/products",
        "/api/brands",
        "/api/pages/contact",
    ]
    for path in allowed:
        code, body = request_code(join_url(base_url, path))
        if code == 200:
            print(f"OK: GET {path} -> HTTP 200")
        else:
            issues += 1
            print(f"FAIL: GET {path} -> HTTP {code}: {body[:160]}")

    print("\n== Admin/auth/management surfaces still blocked publicly ==")
    blocked = [
        "/admin/",
        "/admin/login.html",
        "/api/admin/auth/config",
        "/api/admin/auth/status",
        "/api/admin/auth/cognito-login",
        "/api/admin/products",
        "/api/customers",
        "/api/bookings",
        "/api/inquiries",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    for path in blocked:
        code, body = request_code(join_url(base_url, path))
        if code == 403:
            print(f"OK: GET {path} -> HTTP 403")
        else:
            issues += 1
            print(f"FAIL: GET {path} -> HTTP {code}, expected 403: {body[:160]}")

    print("\n== Direct backend port check ==")
    direct_url = direct_8000_url(base_url, "/api/admin/auth/config")
    code, body = request_code(direct_url, timeout=6)
    if code is None:
        print(f"OK: GET :8000/api/admin/auth/config -> blocked/unreachable as expected ({body})")
    else:
        issues += 1
        print(f"FAIL: direct :8000 returned HTTP {code}; port 8000 should not be public.")

    print("\n== Summary ==")
    if issues:
        print(f"Batch 43 public Cognito/admin lockdown check FAILED with {issues} issue(s).")
        return 1
    print("Batch 43 public Cognito/admin lockdown check PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
