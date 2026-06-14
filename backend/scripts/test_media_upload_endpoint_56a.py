from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import uuid


def encode_multipart(fields: dict[str, str], file_field: str, file_path: Path, content_type: str) -> tuple[bytes, str]:
    boundary = f"----rsa56a{uuid.uuid4().hex}"
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.extend(file_path.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def request_json(url: str, *, method: str = "GET", data: bytes | None = None, content_type: str | None = None, token: str | None = None) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    if content_type:
        headers["Content-Type"] = content_type
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body or "{}")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            payload = {"raw_body": body}
        return exc.code, payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch 56A media upload endpoint smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/", help="API base URL, usually http://127.0.0.1:8000/api/")
    parser.add_argument("--image", required=True, help="Path to jpg/png/webp test image")
    parser.add_argument("--token", default="", help="Optional admin bearer token when admin routes are protected")
    parser.add_argument("--media-type", default="products", choices=["products", "brands", "project-gallery", "contact-persons"])
    args = parser.parse_args()

    base = args.base_url.rstrip("/") + "/"
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Missing image: {image_path}")

    status, config = request_json(urljoin(base, "admin/media/config"), token=args.token or None)
    print("config_status:", status)
    print(json.dumps(config, indent=2))
    if status >= 400:
        raise SystemExit("Config request failed")

    content_type = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
    data, multipart_type = encode_multipart(
        {
            "media_type": args.media_type,
            "brand_name": "Dahua",
            "feature_01": "Full Color 4K Bullet Camera with long feature text",
            "subcategory": "Bullet Camera",
        },
        "file",
        image_path,
        content_type,
    )

    status, upload = request_json(
        urljoin(base, "admin/media/upload"),
        method="POST",
        data=data,
        content_type=multipart_type,
        token=args.token or None,
    )
    print("upload_status:", status)
    print(json.dumps(upload, indent=2))
    if status >= 400:
        raise SystemExit("Upload request failed")
    if not upload.get("upload_prepared"):
        raise SystemExit("Upload did not return upload_prepared=true")

    media_url = str(upload.get("media_url") or "")
    if media_url.startswith("/api/"):
        media_url = urljoin(base, media_url.removeprefix("/api/"))
    elif media_url.startswith("/"):
        media_url = args.base_url.rstrip("/").split("/api")[0] + media_url

    if media_url:
        req = Request(media_url, method="GET", headers={"Accept": "image/*"})
        with urlopen(req, timeout=30) as response:
            content = response.read()
            print("display_status:", response.status)
            print("display_content_type:", response.headers.get("Content-Type"))
            print("display_size_bytes:", len(content))
            if response.status != 200 or not content:
                raise SystemExit("Display endpoint failed")

    print("Batch 56A media upload endpoint smoke test PASSED.")


if __name__ == "__main__":
    main()
