from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MEDIA_MODELS = r'''from __future__ import annotations

from pydantic import BaseModel, Field


class MediaPrepareRequest(BaseModel):
    media_type: str = Field(..., description="Logical media area such as products, brands, project-gallery, contact-persons")
    file_name: str = Field(..., description="Original filename selected by admin")
    content_type: str | None = None
    size_bytes: int | None = None
    slug_source: str | None = None
    product_name: str | None = None
    brand_name: str | None = None
    feature_01: str | None = None
    subcategory: str | None = None


class MediaPrepareResponse(BaseModel):
    storage_mode: str
    upload_prepared: bool
    media_type: str
    file_name: str
    object_key: str
    public_path: str
    field_value: str
    message: str
    media_key: str | None = None
    media_url: str | None = None
    original_filename: str | None = None
    content_type: str | None = None
    size_bytes: int | None = None


class MediaUploadResponse(BaseModel):
    storage_mode: str
    upload_prepared: bool
    media_type: str
    file_name: str
    original_filename: str
    content_type: str
    size_bytes: int
    media_key: str
    media_url: str
    object_key: str
    public_path: str
    field_value: str
    message: str
'''

MEDIA_SERVICE = r'''from __future__ import annotations

import os
import re
import secrets
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from app.models.media import MediaPrepareRequest, MediaPrepareResponse, MediaUploadResponse


BATCH56A_MEDIA_VERSION = "batch56a-media-upload-endpoint"

UPLOAD_MEDIA_TYPES = {
    "products": "products",
    "brands": "brands",
    "project-gallery": "project-gallery",
    "contact-persons": "contact-persons",
}

MEDIA_TYPE_ALIASES = {
    "product": "products",
    "products": "products",
    "brand": "brands",
    "brands": "brands",
    "gallery": "project-gallery",
    "project-gallery": "project-gallery",
    "project_gallery": "project-gallery",
    "contact-person": "contact-persons",
    "contact-persons": "contact-persons",
    "contact_person": "contact-persons",
    "contact_persons": "contact-persons",
}

# Kept only for the legacy prepare-upload endpoint so older admin media picker
# behavior does not break before Batch 56B frontend integration.
PREPARE_ONLY_MEDIA_TYPES = {
    "services": "services",
    "about": "about",
    "contact": "contact",
    "categories": "categories",
    "general": "general",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
}


@dataclass(frozen=True)
class MediaObject:
    content: bytes
    content_type: str


def _backend_root() -> Path:
    # backend/app/services/media_service.py -> backend
    return Path(__file__).resolve().parents[2]


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def get_media_storage_mode() -> str:
    mode = _env("RSA_MEDIA_STORAGE_MODE", "local").lower() or "local"
    return mode if mode in {"local", "s3"} else "local"


def get_media_max_upload_bytes() -> int:
    raw = _env("RSA_MEDIA_MAX_UPLOAD_MB", "5")
    try:
        mb = int(raw)
    except ValueError:
        mb = 5
    mb = max(1, min(mb, 25))
    return mb * 1024 * 1024


def get_local_media_root() -> Path:
    configured = _env("RSA_MEDIA_LOCAL_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (_backend_root() / "data" / "media_uploads").resolve()


def get_s3_bucket_name() -> str:
    return _env("RSA_MEDIA_S3_BUCKET")


def get_aws_region() -> str:
    return _env("RSA_AWS_REGION") or _env("AWS_DEFAULT_REGION") or _env("AWS_REGION", "ap-southeast-1")


def _media_url_for_key(media_key: str) -> str:
    public_base_url = _env("RSA_MEDIA_PUBLIC_BASE_URL")
    if public_base_url:
        return f"{public_base_url.rstrip('/')}/{media_key}"
    return f"/api/media/{media_key}"


def get_media_storage_config() -> dict[str, object]:
    storage_mode = get_media_storage_mode()
    bucket_name = get_s3_bucket_name()
    local_root = get_local_media_root()
    max_bytes = get_media_max_upload_bytes()

    upload_binary_enabled = storage_mode == "local" or (storage_mode == "s3" and bool(bucket_name))

    return {
        "version": BATCH56A_MEDIA_VERSION,
        "storage_mode": storage_mode,
        "upload_binary_enabled": upload_binary_enabled,
        "s3_bucket_configured": bool(bucket_name),
        "s3_bucket_name": bucket_name,
        "aws_region": get_aws_region(),
        "local_media_root": str(local_root),
        "max_upload_mb": max_bytes // (1024 * 1024),
        "allowed_upload_media_types": sorted(UPLOAD_MEDIA_TYPES.keys()),
        "legacy_prepare_media_types": sorted(PREPARE_ONLY_MEDIA_TYPES.keys()),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "allowed_content_types": sorted(ALLOWED_CONTENT_TYPES.keys()),
        "media_url_format": "/api/media/{media_key}",
        "filename_rule": "readable-slug-short-unique-suffix-original-extension",
        "media_key_authoritative": True,
        "stores_full_s3_url": False,
        "public_bucket_required": False,
    }


def _normalize_media_type(media_type: str, *, allow_prepare_only: bool = False) -> str:
    raw = str(media_type or "").strip().lower().replace("_", "-")
    normalized = MEDIA_TYPE_ALIASES.get(raw, raw)
    if normalized in UPLOAD_MEDIA_TYPES:
        return normalized
    if allow_prepare_only and normalized in PREPARE_ONLY_MEDIA_TYPES:
        return normalized
    allowed = ", ".join(sorted(UPLOAD_MEDIA_TYPES))
    raise ValueError(f"Unsupported media type '{media_type}'. Allowed upload media types: {allowed}")


def _safe_original_filename(file_name: str) -> str:
    original = PurePosixPath(str(file_name or "")).name.strip()
    if not original:
        raise ValueError("file_name is required")
    return original


def _extension_from_filename(file_name: str) -> str:
    extension = PurePosixPath(file_name).suffix.lower()
    if extension == ".jpeg":
        return ".jpg"
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported image extension '{extension or '(none)'}'. Allowed: {allowed}")
    return extension


def _validate_content_type(content_type: str | None, extension: str) -> str:
    normalized = str(content_type or "").split(";")[0].strip().lower()
    if not normalized:
        # Some browsers/tools may omit the content type; keep a safe value based on extension.
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(extension, "application/octet-stream")

    allowed_extensions = ALLOWED_CONTENT_TYPES.get(normalized)
    if not allowed_extensions or extension not in allowed_extensions:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        raise ValueError(f"Unsupported or mismatched image content type '{normalized}'. Allowed: {allowed}")
    return normalized


def _slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _shorten_slug(value: str, *, max_words: int = 5, max_chars: int = 36) -> str:
    slug = _slugify(value)
    if not slug:
        return ""
    words = [part for part in slug.split("-") if part]
    shortened = "-".join(words[:max_words]) if words else slug
    if len(shortened) <= max_chars:
        return shortened
    shortened = shortened[:max_chars].strip("-")
    if "-" in shortened:
        shortened = shortened.rsplit("-", 1)[0]
    return shortened.strip("-") or slug[:max_chars].strip("-")


def _stem_from_context(
    media_type: str,
    *,
    original_filename: str,
    slug_source: str | None = None,
    product_name: str | None = None,
    brand_name: str | None = None,
    feature_01: str | None = None,
    subcategory: str | None = None,
) -> str:
    uploaded_stem = PurePosixPath(original_filename).stem

    if media_type == "products":
        # Prefer the final admin product name if present; otherwise use the approved
        # brand + shortened feature_01 + subcategory naming source.
        if product_name:
            source = product_name
        else:
            parts = [brand_name, _shorten_slug(feature_01 or ""), subcategory]
            source = " ".join(str(part or "").strip() for part in parts if str(part or "").strip())
        if not source:
            source = slug_source or uploaded_stem
    elif media_type == "brands":
        source = brand_name or slug_source or uploaded_stem
    elif media_type == "project-gallery":
        source = slug_source or product_name or uploaded_stem or "project-gallery"
    elif media_type == "contact-persons":
        source = slug_source or brand_name or product_name or uploaded_stem or "contact-person"
    else:
        source = slug_source or uploaded_stem or media_type

    slug = _slugify(source)
    if not slug:
        slug = _slugify(uploaded_stem) or media_type
    return slug[:80].strip("-") or media_type


def build_media_key(
    media_type: str,
    original_filename: str,
    *,
    content_type: str | None = None,
    slug_source: str | None = None,
    product_name: str | None = None,
    brand_name: str | None = None,
    feature_01: str | None = None,
    subcategory: str | None = None,
) -> tuple[str, str, str]:
    normalized_type = _normalize_media_type(media_type)
    safe_original = _safe_original_filename(original_filename)
    extension = _extension_from_filename(safe_original)
    safe_content_type = _validate_content_type(content_type, extension)

    now = datetime.now(timezone.utc)
    folder = UPLOAD_MEDIA_TYPES[normalized_type]
    stem = _stem_from_context(
        normalized_type,
        original_filename=safe_original,
        slug_source=slug_source,
        product_name=product_name,
        brand_name=brand_name,
        feature_01=feature_01,
        subcategory=subcategory,
    )
    suffix = secrets.token_hex(3)
    file_name = f"{stem}-{suffix}{extension}"
    media_key = f"{folder}/{now:%Y/%m}/{file_name}"
    return media_key, file_name, safe_content_type


def _validate_media_key(media_key: str) -> str:
    key = str(media_key or "").strip().replace("\\", "/").lstrip("/")
    if not key or ".." in key.split("/"):
        raise ValueError("Invalid media key")
    allowed_prefixes = tuple(f"{folder}/" for folder in UPLOAD_MEDIA_TYPES.values())
    if not key.startswith(allowed_prefixes):
        raise ValueError("Media key is outside the allowed upload folders")
    return key


def _local_path_for_key(media_key: str) -> Path:
    key = _validate_media_key(media_key)
    root = get_local_media_root()
    path = (root / key).resolve()
    if root not in path.parents and path != root:
        raise ValueError("Invalid media key path")
    return path


def _get_s3_client():
    try:
        import boto3  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on deployment environment
        raise RuntimeError("boto3 is required for RSA_MEDIA_STORAGE_MODE=s3") from exc
    return boto3.client("s3", region_name=get_aws_region())


def _store_local(media_key: str, content: bytes) -> None:
    path = _local_path_for_key(media_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _store_s3(media_key: str, content: bytes, content_type: str) -> None:
    bucket = get_s3_bucket_name()
    if not bucket:
        raise ValueError("RSA_MEDIA_S3_BUCKET is required when RSA_MEDIA_STORAGE_MODE=s3")
    client = _get_s3_client()
    client.put_object(
        Bucket=bucket,
        Key=media_key,
        Body=content,
        ContentType=content_type,
        CacheControl="public, max-age=3600",
    )


async def store_uploaded_media(
    *,
    media_type: str,
    upload_file,
    slug_source: str | None = None,
    product_name: str | None = None,
    brand_name: str | None = None,
    feature_01: str | None = None,
    subcategory: str | None = None,
) -> MediaUploadResponse:
    original_filename = _safe_original_filename(getattr(upload_file, "filename", ""))
    upload_content_type = getattr(upload_file, "content_type", None)
    media_key, file_name, content_type = build_media_key(
        media_type,
        original_filename,
        content_type=upload_content_type,
        slug_source=slug_source,
        product_name=product_name,
        brand_name=brand_name,
        feature_01=feature_01,
        subcategory=subcategory,
    )

    max_bytes = get_media_max_upload_bytes()
    content = await upload_file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise ValueError(f"Image is too large. Max size is {max_bytes // (1024 * 1024)} MB.")
    if not content:
        raise ValueError("Uploaded file is empty")

    storage_mode = get_media_storage_mode()
    if storage_mode == "s3":
        _store_s3(media_key, content, content_type)
    else:
        _store_local(media_key, content)

    media_url = _media_url_for_key(media_key)
    normalized_type = _normalize_media_type(media_type)

    return MediaUploadResponse(
        storage_mode=storage_mode,
        upload_prepared=True,
        media_type=normalized_type,
        file_name=file_name,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=len(content),
        media_key=media_key,
        media_url=media_url,
        object_key=media_key,
        public_path=media_url,
        field_value=media_url,
        message="Image uploaded successfully.",
    )


def load_media_object(media_key: str) -> MediaObject:
    key = _validate_media_key(media_key)
    extension = PurePosixPath(key).suffix.lower()
    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(extension, "application/octet-stream")

    if get_media_storage_mode() == "s3":
        bucket = get_s3_bucket_name()
        if not bucket:
            raise FileNotFoundError("S3 bucket is not configured")
        client = _get_s3_client()
        response = client.get_object(Bucket=bucket, Key=key)
        return MediaObject(
            content=response["Body"].read(),
            content_type=response.get("ContentType") or content_type,
        )

    path = _local_path_for_key(key)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError("Media object not found")
    return MediaObject(content=path.read_bytes(), content_type=content_type)


def prepare_media_reference(payload: MediaPrepareRequest) -> MediaPrepareResponse:
    # Prepare remains non-writing for legacy Batch 55A admin media picker behavior.
    raw_type = str(payload.media_type or "general").strip().lower().replace("_", "-")
    media_type = MEDIA_TYPE_ALIASES.get(raw_type, raw_type)
    if media_type not in UPLOAD_MEDIA_TYPES and media_type not in PREPARE_ONLY_MEDIA_TYPES:
        media_type = "general"

    original_filename = _safe_original_filename(payload.file_name)
    extension = _extension_from_filename(original_filename)
    content_type = _validate_content_type(payload.content_type, extension)

    if media_type in UPLOAD_MEDIA_TYPES:
        media_key, file_name, content_type = build_media_key(
            media_type,
            original_filename,
            content_type=content_type,
            slug_source=payload.slug_source,
            product_name=payload.product_name,
            brand_name=payload.brand_name,
            feature_01=payload.feature_01,
            subcategory=payload.subcategory,
        )
    else:
        stem = _slugify(PurePosixPath(original_filename).stem) or media_type
        file_name = f"{stem}{extension}"
        media_key = f"uploads/{media_type}/{file_name}"

    media_url = _media_url_for_key(media_key) if media_type in UPLOAD_MEDIA_TYPES else media_key

    return MediaPrepareResponse(
        storage_mode=get_media_storage_mode(),
        upload_prepared=False,
        media_type=media_type,
        file_name=file_name,
        object_key=media_key,
        public_path=media_url,
        field_value=media_url,
        media_key=media_key,
        media_url=media_url,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=payload.size_bytes,
        message=(
            "Image key prepared. Binary upload is available only through "
            "POST /api/admin/media/upload in Batch 56A; admin form integration is planned for Batch 56B."
        ),
    )
'''

ADMIN_MEDIA_ROUTE = r'''from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile, status

from app.models.media import MediaPrepareRequest, MediaPrepareResponse, MediaUploadResponse
from app.services.media_service import (
    get_media_storage_config,
    load_media_object,
    prepare_media_reference,
    store_uploaded_media,
)


router = APIRouter(prefix="/admin/media")
media_router = APIRouter(prefix="/media")


@router.get("/config")
def get_config():
    """Return public-safe media upload/storage configuration."""

    return get_media_storage_config()


@router.post("/prepare-upload", response_model=MediaPrepareResponse)
def prepare_upload(payload: MediaPrepareRequest):
    """Prepare a future media key/path without writing binary data.

    This endpoint remains for the interim admin media picker. Real binary upload
    is handled by POST /api/admin/media/upload in Batch 56A.
    """

    try:
        return prepare_media_reference(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    media_type: str = Form(...),
    file: UploadFile = File(...),
    slug_source: str | None = Form(default=None),
    product_name: str | None = Form(default=None),
    brand_name: str | None = Form(default=None),
    feature_01: str | None = Form(default=None),
    subcategory: str | None = Form(default=None),
):
    """Upload one validated admin image to local storage or private S3.

    Route protection is inherited from the existing admin API protection because
    this route is under /api/admin/* after the API prefix is applied.
    """

    try:
        return await store_uploaded_media(
            media_type=media_type,
            upload_file=file,
            slug_source=slug_source,
            product_name=product_name,
            brand_name=brand_name,
            feature_01=feature_01,
            subcategory=subcategory,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@media_router.get("/{media_key:path}")
def get_media(media_key: str):
    """Serve an uploaded media object through the backend display endpoint."""

    try:
        media = load_media_object(media_key)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return Response(
        content=media.content,
        media_type=media.content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
'''

PREFLIGHT_SCRIPT = r'''from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.media_service import get_media_storage_config, get_local_media_root  # noqa: E402


def mask(value: str) -> str:
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def main() -> None:
    print("RSA CMS / Mini-CRM Batch 56A Media Upload Preflight")
    print("Mode: read-only configuration check")

    config = get_media_storage_config()
    for key in [
        "version",
        "storage_mode",
        "upload_binary_enabled",
        "s3_bucket_configured",
        "s3_bucket_name",
        "aws_region",
        "local_media_root",
        "max_upload_mb",
        "allowed_upload_media_types",
        "allowed_extensions",
        "media_url_format",
        "filename_rule",
    ]:
        print(f"{key}: {config.get(key)}")

    issues = 0

    multipart_available = importlib.util.find_spec("multipart") is not None
    print(f"python_multipart_available: {multipart_available}")
    if not multipart_available:
        print("FAIL: python-multipart is required by FastAPI UploadFile/Form routes.")
        print("Install locally with: pip install python-multipart")
        issues += 1

    storage_mode = str(config.get("storage_mode") or "local")
    if storage_mode == "s3":
        boto3_available = importlib.util.find_spec("boto3") is not None
        print(f"boto3_available: {boto3_available}")
        if not boto3_available:
            print("FAIL: boto3 is required when RSA_MEDIA_STORAGE_MODE=s3.")
            issues += 1
        if not config.get("s3_bucket_configured"):
            print("FAIL: RSA_MEDIA_S3_BUCKET is required when RSA_MEDIA_STORAGE_MODE=s3.")
            issues += 1
    else:
        local_root = get_local_media_root()
        try:
            local_root.mkdir(parents=True, exist_ok=True)
            print(f"local_media_root_writable: {os.access(local_root, os.W_OK)}")
            if not os.access(local_root, os.W_OK):
                issues += 1
        except Exception as exc:
            print(f"FAIL: could not prepare local media root: {exc}")
            issues += 1

    print(f"aws_access_key_id: {mask(os.getenv('AWS_ACCESS_KEY_ID', ''))}")
    print("No secrets are printed by this preflight.")

    if issues:
        raise SystemExit(f"Batch 56A media upload preflight FAILED with {issues} issue(s).")

    print("Batch 56A media upload preflight PASSED.")


if __name__ == "__main__":
    main()
'''

TEST_SCRIPT = r'''from __future__ import annotations

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
'''

README = r'''# Batch 56A - Media upload design/preflight + backend upload endpoint

Approved decisions:

- Use S3 for deployed media storage, with local folder fallback for local development/testing.
- S3 bucket naming target: `rsa-cms-media-537765358118-ap-southeast-1`.
- Keep S3 private. No public write access and no public bucket policy required.
- Store/return both `media_key` and `media_url`; treat `media_key` as authoritative.
- Upload endpoint: `POST /api/admin/media/upload`.
- Display endpoint: `GET /api/media/{media_key:path}`.
- Allowed upload groups: `products`, `brands`, `project-gallery`, `contact-persons`.
- Allowed file types: `.jpg`, `.jpeg`, `.png`, `.webp` only.
- Max image size: 5 MB by default (`RSA_MEDIA_MAX_UPLOAD_MB=5`).
- Filename rule: readable slug + short unique suffix + original validated extension.
- Product slug source: `product_name` first; fallback to `brand_name + shortened feature_01 + subcategory`.
- No image conversion or resizing in 56A.
- Admin upload route stays under existing protected `/api/admin/*` protection.
- 56A is backend/preflight only. Full admin form integration is for 56B.

Environment variables:

```text
RSA_MEDIA_STORAGE_MODE=local              # local or s3
RSA_MEDIA_LOCAL_ROOT=backend/data/media_uploads
RSA_MEDIA_MAX_UPLOAD_MB=5
RSA_MEDIA_S3_BUCKET=rsa-cms-media-537765358118-ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1
```

For EC2/local-folder fallback, use a folder outside release directories, for example:

```text
RSA_MEDIA_LOCAL_ROOT=/opt/rsa-cms/shared/uploads
```

For S3 mode, set:

```text
RSA_MEDIA_STORAGE_MODE=s3
RSA_MEDIA_S3_BUCKET=rsa-cms-media-537765358118-ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1
```

No CloudFront, Route 53, S3 versioning, replication, advanced Storage Lens, or paid notification services are introduced by this batch.
'''


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[ok] wrote {path.relative_to(ROOT)}")


def patch_main_py() -> None:
    main_py = ROOT / "backend" / "app" / "main.py"
    if not main_py.exists():
        print("[warn] backend/app/main.py not found; add admin_media.media_router manually if needed.")
        return

    text = main_py.read_text(encoding="utf-8")
    if "admin_media.media_router" in text:
        print("[ok] backend/app/main.py already includes admin_media.media_router")
        return

    anchor = 'app.include_router(admin_media.router, prefix=settings.API_PREFIX, tags=["Admin Media"])'
    replacement = anchor + '\napp.include_router(admin_media.media_router, prefix=settings.API_PREFIX, tags=["Media"])'
    if anchor not in text:
        print("[warn] Could not find admin_media router include line in backend/app/main.py; add this manually:")
        print('app.include_router(admin_media.media_router, prefix=settings.API_PREFIX, tags=["Media"])')
        return

    main_py.write_text(text.replace(anchor, replacement), encoding="utf-8", newline="\n")
    print("[ok] patched backend/app/main.py to include /api/media display router")


def patch_requirements() -> None:
    candidates = [ROOT / "backend" / "requirements.txt", ROOT / "requirements.txt"]
    req = next((path for path in candidates if path.exists()), None)
    if req is None:
        print("[warn] requirements.txt not found; ensure python-multipart is installed in backend venv.")
        return

    text = req.read_text(encoding="utf-8")
    if "python-multipart" in text.lower():
        print(f"[ok] {req.relative_to(ROOT)} already includes python-multipart")
        return

    ending = "" if text.endswith("\n") else "\n"
    req.write_text(text + ending + "python-multipart\n", encoding="utf-8", newline="\n")
    print(f"[ok] added python-multipart to {req.relative_to(ROOT)}")


def main() -> None:
    write(ROOT / "backend" / "app" / "models" / "media.py", MEDIA_MODELS)
    write(ROOT / "backend" / "app" / "services" / "media_service.py", MEDIA_SERVICE)
    write(ROOT / "backend" / "app" / "routes" / "admin_media.py", ADMIN_MEDIA_ROUTE)
    write(ROOT / "backend" / "scripts" / "check_media_upload_preflight_56a.py", PREFLIGHT_SCRIPT)
    write(ROOT / "backend" / "scripts" / "test_media_upload_endpoint_56a.py", TEST_SCRIPT)
    write(ROOT / "docs" / "phase8_batch56a_media_upload_endpoint.md", README)
    patch_main_py()
    patch_requirements()
    print("[done] batch56a-media-upload-endpoint applied.")
    print("[done] Backend/preflight only. No admin form integration, no frontend behavior change, no DynamoDB schema change.")


if __name__ == "__main__":
    main()
