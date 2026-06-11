from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request

API_BASE_URL = "http://127.0.0.1:8000/api"


def _json_request(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(f"{API_BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch 24 admin media preparation smoke test.")
    parser.add_argument("--execute", action="store_true", help="Call local API endpoints.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 24 Admin Media Prep Test")
    print(f"API base URL: {API_BASE_URL}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if not args.execute:
        print("\nNo API calls were made.")
        print("Start backend first, then run:")
        print("  python scripts\\test_admin_media_prep.py --execute")
        return 0

    try:
        config = _json_request("/admin/media/config")
        prepared = _json_request(
            "/admin/media/prepare-upload",
            method="POST",
            payload={
                "media_type": "products",
                "file_name": "Hikvision Dome Camera.JPG",
                "content_type": "image/jpeg",
                "size_bytes": 123456,
            },
        )
    except urllib.error.URLError as exc:
        print(f"Unable to reach local API at {API_BASE_URL}: {exc}")
        return 1

    print("\nConfig:")
    print(json.dumps(config, indent=2))
    print("\nPrepared media reference:")
    print(json.dumps(prepared, indent=2))

    if prepared.get("field_value") != "uploads/products/hikvision-dome-camera.jpg":
        print("Unexpected prepared media key.")
        return 1

    if prepared.get("upload_prepared") is not False:
        print("Batch 24 should not enable binary upload yet.")
        return 1

    print("\nBatch 24 admin media preparation smoke test PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
