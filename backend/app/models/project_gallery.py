from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectGalleryItem(BaseModel):
    project_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0
    project_title: str
    project_description: Optional[str] = None
    image_path: str
    alt_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ProjectGalleryListResponse(BaseModel):
    items: list[ProjectGalleryItem]
    total: int


class ProjectGalleryAdminCreateRequest(BaseModel):
    show_flag: str = Field(default="Y", pattern="^(Y|N)$")
    display_seq: int = 0
    project_title: str
    project_description: Optional[str] = None
    image_path: str
    alt_text: Optional[str] = None
    updated_by: Optional[str] = "admin"


class ProjectGalleryAdminUpdateRequest(BaseModel):
    show_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    display_seq: Optional[int] = None
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    image_path: Optional[str] = None
    alt_text: Optional[str] = None
    updated_by: Optional[str] = "admin"
