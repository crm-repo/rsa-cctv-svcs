from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.media import MediaPrepareRequest, MediaPrepareResponse
from app.services.media_service import get_media_storage_config, prepare_media_reference


router = APIRouter(prefix="/admin/media")


@router.get("/config")
def get_config():
    """Return public-safe media upload/storage preparation config."""

    return get_media_storage_config()


@router.post("/prepare-upload", response_model=MediaPrepareResponse)
def prepare_upload(payload: MediaPrepareRequest):
    """Prepare a future media key/path from a selected local filename.

    Batch 24 does not upload binary image data yet. It only avoids asking admin
    users to manually type project-folder paths and prepares the key/path that
    the later S3 upload batch will use.
    """

    try:
        return prepare_media_reference(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
