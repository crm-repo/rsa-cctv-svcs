from __future__ import annotations

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




def _merge_slug_parts(*parts: str) -> str:
    """Merge slug parts while removing repeated boundary phrases.

    Example:
    dahua + full-color-4k-bullet-camera + bullet-camera
    -> dahua-full-color-4k-bullet-camera
    """

    merged_words: list[str] = []
    for part in parts:
        slug = _slugify(part)
        if not slug:
            continue
        words = [word for word in slug.split("-") if word]
        if not words:
            continue

        if len(words) <= len(merged_words) and merged_words[-len(words):] == words:
            continue

        overlap = 0
        max_overlap = min(len(merged_words), len(words))
        for size in range(max_overlap, 0, -1):
            if merged_words[-size:] == words[:size]:
                overlap = size
                break

        merged_words.extend(words[overlap:])

    return "-".join(merged_words)

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
        # brand + shortened feature_01 + subcategory naming source. The fallback
        # merge removes repeated boundary phrases such as feature_01 ending with
        # "bullet camera" and subcategory also being "Bullet Camera".
        if product_name:
            source_slug = _slugify(product_name)
        else:
            source_slug = _merge_slug_parts(
                brand_name or "",
                _shorten_slug(feature_01 or ""),
                subcategory or "",
            )
        if not source_slug:
            source_slug = _slugify(slug_source or uploaded_stem)
    elif media_type == "brands":
        source_slug = _slugify(brand_name or slug_source or uploaded_stem)
    elif media_type == "project-gallery":
        source_slug = _slugify(slug_source or product_name or uploaded_stem or "project-gallery")
    elif media_type == "contact-persons":
        source_slug = _slugify(slug_source or brand_name or product_name or uploaded_stem or "contact-person")
    else:
        source_slug = _slugify(slug_source or uploaded_stem or media_type)

    if not source_slug:
        source_slug = _slugify(uploaded_stem) or media_type
    return source_slug[:80].strip("-") or media_type


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
