from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Brand(BaseModel):
    brand_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0
    brand_name: str
    brand_key: str
    brand_logo_path: Optional[str] = None
    description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class BrandListResponse(BaseModel):
    items: list[Brand]
    total: int
