from __future__ import annotations

import os
import re
from pathlib import PurePosixPath

from app.models.media import MediaPrepareRequest, MediaPrepareResponse


ALLOWED_MEDIA_TYPES = {
    "products": "uploads/products",
    "brands": "uploads/brands",
    "categories": "uploads/categories",
    "gallery": "uploads/project-gallery",
    "project-gallery": "uploads/project-gallery",
    "services": "uploads/services",
    "about": "uploads/about",
    "contact": "uploads/contact",
    "general": "uploads/general",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def get_media_storage_config() -> dict[str, object]:
    storage_mode = os.getenv("RSA_MEDIA_STORAGE_MODE", "local-preview").strip().lower() or "local-preview"
    bucket_name = os.getenv("RSA_MEDIA_S3_BUCKET", "")
    public_base_url = os.getenv("RSA_MEDIA_PUBLIC_BASE_URL", "")

    return {
        "storage_mode": storage_mode,
        "s3_bucket_configured": bool(bucket_name),
        "s3_bucket_name": bucket_name,
        "public_base_url_configured": bool(public_base_url),
        "public_base_url": public_base_url,
        "allowed_media_types": sorted(ALLOWED_MEDIA_TYPES.keys()),
        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
        "upload_binary_enabled": False,
        "safety_note": (
            "Batch 24 prepares Browse/Choose File UI and media key generation only. "
            "Actual binary upload/S3 storage is intentionally deferred until the approved S3 batch."
        ),
    }


def _safe_filename(file_name: str) -> str:
    raw = PurePosixPath(str(file_name or "")).name.strip()
    if not raw:
        raise ValueError("file_name is required")

    # Keep readable filenames but remove unsafe characters and spaces.
    raw = raw.replace(" ", "-")
    safe = re.sub(r"[^A-Za-z0-9._-]", "", raw)
    safe = re.sub(r"-+", "-", safe).strip(".-_")

    if not safe:
        raise ValueError("file_name has no usable characters")

    extension = PurePosixPath(safe).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported image extension '{extension or '(none)'}'. Allowed: {allowed}")

    return safe.lower()


def _normalize_media_type(media_type: str) -> str:
    key = str(media_type or "general").strip().lower().replace("_", "-")
    return key if key in ALLOWED_MEDIA_TYPES else "general"


def prepare_media_reference(payload: MediaPrepareRequest) -> MediaPrepareResponse:
    config = get_media_storage_config()
    media_type = _normalize_media_type(payload.media_type)
    file_name = _safe_filename(payload.file_name)
    folder = ALLOWED_MEDIA_TYPES[media_type]
    object_key = f"{folder}/{file_name}"

    public_base_url = str(config.get("public_base_url") or "").rstrip("/")
    public_path = f"{public_base_url}/{object_key}" if public_base_url else object_key

    return MediaPrepareResponse(
        storage_mode=str(config["storage_mode"]),
        upload_prepared=False,
        media_type=media_type,
        file_name=file_name,
        object_key=object_key,
        public_path=public_path,
        field_value=object_key,
        message=(
            "Image key prepared. Binary upload is not enabled in Batch 24; "
            "S3/local file storage will be completed in the later image upload batch."
        ),
    )
