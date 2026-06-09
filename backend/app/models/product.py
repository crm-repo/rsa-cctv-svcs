from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    display_order: int = 0

    product_name: str
    product_model: Optional[str] = None
    product_slug: Optional[str] = None

    category: str
    subcategory: Optional[str] = None

    brand_id: Optional[str] = None
    product_brand_name: Optional[str] = None

    description: Optional[str] = None
    features: list[str] = Field(default_factory=list)

    price: float
    old_price: Optional[float] = None
    sale_price: Optional[float] = None

    image_path: str
    brand_logo_path: Optional[str] = None

    stock_quantity: int = 0
    low_stock_threshold: int = 10

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    page: int
    per_page: int
    total_pages: int