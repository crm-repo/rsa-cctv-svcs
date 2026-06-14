from __future__ import annotations

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
