"""Batch 15 public read API smoke test for DynamoDB repository mode.

Safe by default. Running without --execute prints instructions only.
In execute mode, this script performs read-only HTTP GET requests against the
local backend. It does not write records and does not create AWS resources.
"""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api"


def _get_json(url: str) -> tuple[int, Any]:
    with urlopen(url, timeout=15) as response:  # noqa: S310 - local smoke-test helper
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else None


def _url(base: str, path: str, query: dict[str, str] | None = None) -> str:
    full_url = f"{base.rstrip('/')}/{path.lstrip('/')}"
    if query:
        full_url = f"{full_url}?{urlencode(query)}"
    return full_url


def _assert_list_payload(name: str, payload: Any, min_total: int = 1) -> None:
    if not isinstance(payload, dict):
        raise AssertionError(f"{name}: expected object response, got {type(payload).__name__}")

    if "items" not in payload:
        raise AssertionError(f"{name}: expected 'items' in response")

    items = payload["items"]
    if not isinstance(items, list):
        raise AssertionError(f"{name}: expected items list")

    if len(items) < min_total:
        raise AssertionError(f"{name}: expected at least {min_total} item(s), got {len(items)}")



def _run_execute(api_base_url: str) -> int:
    checks: list[tuple[str, str, dict[str, str] | None, str]] = [
        ("Health", "health", None, "health"),
        ("Products", "products", None, "list"),
        ("Products by category", "products", {"category": "packages"}, "list"),
        ("Sale products", "products", {"sale": "true"}, "list"),
        ("Package banners", "package-banners", None, "list"),
        ("Brands", "brands", None, "list"),
        ("Categories", "categories", None, "list"),
        ("Key features", "key-features", None, "list"),
        ("About", "about", None, "object"),
        ("Project gallery", "project-gallery", None, "list"),
        ("Services", "services", None, "list"),
        ("Contact", "contact", None, "object"),
        ("About page", "pages/about", None, "object"),
        ("Services page", "pages/services", None, "object"),
        ("Contact page", "pages/contact", None, "object"),
    ]

    print("RSA CMS / Mini-CRM Batch 15 Public DynamoDB API Smoke Test")
    print(f"API base URL: {api_base_url}")
    print("Mode: EXECUTE READ-ONLY")
    print("")

    for name, path, query, expected_shape in checks:
        url = _url(api_base_url, path, query)
        try:
            status, payload = _get_json(url)
        except HTTPError as exc:
            raise AssertionError(f"{name}: HTTP {exc.code} for {url}") from exc
        except URLError as exc:
            raise AssertionError(f"{name}: could not connect to {url}. Is uvicorn running?") from exc

        if status != 200:
            raise AssertionError(f"{name}: expected HTTP 200, got {status}")

        if expected_shape == "health":
            if not isinstance(payload, dict) or payload.get("status") not in {"ok", "healthy"}:
                raise AssertionError(f"{name}: unexpected health payload: {payload}")
        elif expected_shape == "list":
            _assert_list_payload(name, payload)
        elif expected_shape == "object":
            if not isinstance(payload, dict):
                raise AssertionError(f"{name}: expected object payload")

        print(f"OK  {name}: {url}")

    print("")
    print("Batch 15 public DynamoDB-mode API smoke test PASSED.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 15 public DynamoDB-mode API smoke test.")
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if not args.execute:
        print("RSA CMS / Mini-CRM Batch 15 Public DynamoDB API Smoke Test")
        print(f"API base URL: {args.api_base_url}")
        print("Mode: DRY RUN")
        print("")
        print("No API calls were made.")
        print("To run the real read-only public API smoke test:")
        print("  1. Start backend in a PowerShell window:")
        print('     $env:RSA_REPOSITORY_MODE="dynamodb"')
        print("     uvicorn app.main:app --reload")
        print("  2. Run this script in a second PowerShell:")
        print("     python scripts\\test_dynamodb_public_api_smoke.py --execute")
        return 0

    return _run_execute(args.api_base_url)


if __name__ == "__main__":
    raise SystemExit(main())
