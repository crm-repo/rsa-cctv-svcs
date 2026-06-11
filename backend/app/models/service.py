from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Service(BaseModel):
    service_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0

    service_title: str
    service_slug: str
    short_description: str
    service_description: Optional[str] = None

    image_path: Optional[str] = None
    icon_path: Optional[str] = None

    cta_label: Optional[str] = None
    cta_url: Optional[str] = None

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ServiceListResponse(BaseModel):
    items: list[Service]
    total: int


class ServiceAdminCreateRequest(BaseModel):
    show_flag: str = Field(default="Y", pattern="^(Y|N)$")
    display_seq: int = 0
    service_title: str
    service_slug: Optional[str] = None
    short_description: str
    service_description: Optional[str] = None
    image_path: Optional[str] = None
    icon_path: Optional[str] = None
    cta_label: Optional[str] = None
    cta_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"


class ServiceAdminUpdateRequest(BaseModel):
    show_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    display_seq: Optional[int] = None
    service_title: Optional[str] = None
    service_slug: Optional[str] = None
    short_description: Optional[str] = None
    service_description: Optional[str] = None
    image_path: Optional[str] = None
    icon_path: Optional[str] = None
    cta_label: Optional[str] = None
    cta_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"
