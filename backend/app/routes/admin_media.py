from __future__ import annotations

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
