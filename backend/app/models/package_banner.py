from typing import Optional

from pydantic import BaseModel, Field


class PackageBanner(BaseModel):
    package_banner_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_order: int = 0

    product_id: Optional[str] = None
    banner_image_path: str

    homepage_visible: str = Field(default="N", pattern="^(Y|N)$")
    promotions_hero_visible: str = Field(default="N", pattern="^(Y|N)$")


class PackageBannerListResponse(BaseModel):
    items: list[PackageBanner]
    total: int