from typing import Optional

from pydantic import BaseModel, Field


class PackageBanner(BaseModel):
    package_banner_id: str
    product_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    show_pack_flag: str = Field(pattern="^(Y|N)$")
    display_seq: int = 0
    product_name: str
    banner_image_path: str
    price: float
    sale_price: Optional[float] = None


class PackageBannerListResponse(BaseModel):
    items: list[PackageBanner]
    total: int
