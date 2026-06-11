from __future__ import annotations

from pydantic import BaseModel, Field


class MediaPrepareRequest(BaseModel):
    media_type: str = Field(..., description="Logical media area such as products, brands, gallery, services, about")
    file_name: str = Field(..., description="Original filename selected by admin")
    content_type: str | None = None
    size_bytes: int | None = None


class MediaPrepareResponse(BaseModel):
    storage_mode: str
    upload_prepared: bool
    media_type: str
    file_name: str
    object_key: str
    public_path: str
    field_value: str
    message: str
