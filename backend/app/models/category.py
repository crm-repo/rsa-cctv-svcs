from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Category(BaseModel):
    category_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0
    category_name: str
    category_key: str
    category_prefix: str = Field(min_length=4, max_length=4)
    icon_code: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CategoryListResponse(BaseModel):
    items: list[Category]
    total: int
