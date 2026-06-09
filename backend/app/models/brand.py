from typing import Optional

from pydantic import BaseModel, Field


class Brand(BaseModel):
    brand_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_order: int = 0

    brand_name: str
    brand_key: str
    logo_path: str

    description: Optional[str] = None
    website_url: Optional[str] = None
    featured_brand: str = Field(default="N", pattern="^(Y|N)$")


class BrandListResponse(BaseModel):
    items: list[Brand]
    total: int