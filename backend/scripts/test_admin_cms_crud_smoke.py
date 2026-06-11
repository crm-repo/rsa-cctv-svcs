"""Batch 21 Admin CMS CRUD smoke test.

Dry-run by default. Execute mode writes small CMS test records through the local API.
"""
from __future__ import annotations

import argparse
import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

API_BASE = "http://127.0.0.1:8000/api"


def _request(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urlrequest.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    with urlrequest.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _health() -> None:
    try:
        _request("/health")
    except (URLError, HTTPError) as exc:
        raise SystemExit(f"Unable to reach local API at {API_BASE}: {exc}") from exc


def _assert_items(path: str, label: str) -> None:
    payload = _request(path)
    items = payload.get("items", []) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise AssertionError(f"{label} did not return an item list.")
    print(f"OK {label}: {len(items)} records")


def _create_update(path: str, id_field: str, create_payload: dict, update_payload: dict, label: str) -> None:
    created = _request(path, method="POST", payload=create_payload)
    item_id = created.get(id_field)
    if not item_id:
        raise AssertionError(f"{label} create did not return {id_field}.")
    updated = _request(f"{path}/{item_id}", method="PUT", payload=update_payload)
    if updated.get(id_field) != item_id:
        raise AssertionError(f"{label} update returned unexpected ID.")
    print(f"OK {label}: created and updated {item_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 21 admin CMS CRUD smoke test")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-write-test", action="store_true")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 21 Admin CMS CRUD Smoke Test")
    print(f"API base URL: {API_BASE}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if not args.execute:
        print("\nNo API writes were made.")
        print("Start backend first, then run:")
        print("  python scripts\\test_admin_cms_crud_smoke.py --execute --confirm-write-test")
        return 0

    if not args.confirm_write_test:
        raise SystemExit("Refusing to write test records without --confirm-write-test")

    _health()
    _assert_items("/admin/about", "admin about")
    _assert_items("/admin/project-gallery", "admin project gallery")
    _assert_items("/admin/services", "admin services")
    _assert_items("/admin/contact-us", "admin contact-us")

    _create_update(
        "/admin/services",
        "service_id",
        {
            "show_flag": "N",
            "display_seq": 98,
            "service_title": "Batch 21 Test Service",
            "short_description": "Temporary admin CMS CRUD smoke-test service.",
            "service_description": "Created by Batch 21 smoke test.",
            "cta_label": "Test CTA",
            "cta_url": "contact-us.html",
            "updated_by": "batch21-smoke-test",
        },
        {"short_description": "Updated by Batch 21 smoke test.", "updated_by": "batch21-smoke-test"},
        "service",
    )
    _create_update(
        "/admin/project-gallery",
        "project_id",
        {
            "show_flag": "N",
            "display_seq": 98,
            "project_title": "Batch 21 Test Project",
            "project_description": "Temporary admin CMS CRUD smoke-test gallery item.",
            "image_path": "/assets/images/projects/batch21-test.jpg",
            "alt_text": "Batch 21 test project",
            "updated_by": "batch21-smoke-test",
        },
        {"project_description": "Updated by Batch 21 smoke test.", "updated_by": "batch21-smoke-test"},
        "project gallery item",
    )
    _create_update(
        "/admin/contact-us",
        "contact_us_id",
        {
            "show_flag": "N",
            "contact_type": "Social Media",
            "display_seq": 98,
            "platform_name": "Batch 21 Test Social",
            "platform_key": "batch21-test",
            "profile_url": "https://example.com/batch21-test",
            "icon_code": "fa-solid fa-flask",
            "updated_by": "batch21-smoke-test",
        },
        {"profile_url": "https://example.com/batch21-test-updated", "updated_by": "batch21-smoke-test"},
        "contact/social record",
    )

    print("\nBatch 21 admin CMS CRUD smoke test PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
