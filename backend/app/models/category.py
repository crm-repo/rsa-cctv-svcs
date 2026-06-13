from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# batch55b-admin-category-subcategory-brand-protection
class CategorySubcategory(BaseModel):
    subcategory_key: str
    subcategory_name: str
    display_seq: int = 0


class Category(BaseModel):
    category_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0
    category_name: str
    category_key: str
    category_prefix: str = Field(min_length=4, max_length=4)
    icon_code: Optional[str] = None
    description: Optional[str] = None
    subcategories: list[CategorySubcategory] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CategoryListResponse(BaseModel):
    items: list[Category]
    total: int



class CategoryAdminCreateRequest(BaseModel):
    show_flag: str = Field(default="Y", pattern="^(Y|N)$")
    display_seq: int = 0
    category_name: str
    category_key: Optional[str] = None
    category_prefix: str = Field(min_length=4, max_length=4)
    icon_code: Optional[str] = None
    description: Optional[str] = None
    subcategories: list[CategorySubcategory] = Field(default_factory=list)
    updated_by: Optional[str] = "admin"


class CategoryAdminUpdateRequest(BaseModel):
    show_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    display_seq: Optional[int] = None
    category_name: Optional[str] = None
    category_key: Optional[str] = None
    category_prefix: Optional[str] = Field(default=None, min_length=4, max_length=4)
    icon_code: Optional[str] = None
    description: Optional[str] = None
    subcategories: Optional[list[CategorySubcategory]] = None
    updated_by: Optional[str] = "admin"
