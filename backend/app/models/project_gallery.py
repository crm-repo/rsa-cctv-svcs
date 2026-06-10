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
