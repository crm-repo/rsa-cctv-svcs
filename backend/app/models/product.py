from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# batch55b-admin-category-subcategory-brand-protection


class Product(BaseModel):
    product_id: str
    show_flag: str = Field(pattern="^(Y|N)$")
    show_pack_flag: str = Field(default="N", pattern="^(Y|N)$")
    display_seq: int = 0

    product_name: str
    product_model: Optional[str] = None
    product_slug: Optional[str] = None

    category_id: str
    category_key: str
    category_name: str
    category_prefix: str
    subcategory_key: Optional[str] = None
    subcategory: Optional[str] = None

    brand_id: Optional[str] = None
    product_brand_key: Optional[str] = None
    product_brand_name: Optional[str] = None
    brand_logo_path: Optional[str] = None

    description: Optional[str] = None

    feature_01: str
    feature_02: str
    feature_03: str
    feature_04: Optional[str] = None
    feature_05: Optional[str] = None
    feature_06: Optional[str] = None
    feature_07: Optional[str] = None
    feature_08: Optional[str] = None
    feature_09: Optional[str] = None
    feature_10: Optional[str] = None

    price: Optional[float] = None
    sale_price: Optional[float] = None

    image_path: str

    stock_quantity: int = 0
    low_stock_threshold: int = 10

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    page: int
    per_page: int
    total_pages: int



class ProductAdminCreateRequest(BaseModel):
    show_flag: str = Field(default="Y", pattern="^(Y|N)$")
    show_pack_flag: str = Field(default="N", pattern="^(Y|N)$")
    display_seq: int = 0

    product_name: Optional[str] = None
    product_model: Optional[str] = None
    product_slug: Optional[str] = None

    category_id: Optional[str] = None
    category_key: Optional[str] = None
    subcategory_key: Optional[str] = None
    subcategory: Optional[str] = None

    brand_id: Optional[str] = None
    product_brand_key: Optional[str] = None

    description: Optional[str] = None

    feature_01: Optional[str] = None
    feature_02: Optional[str] = None
    feature_03: Optional[str] = None
    feature_04: Optional[str] = None
    feature_05: Optional[str] = None
    feature_06: Optional[str] = None
    feature_07: Optional[str] = None
    feature_08: Optional[str] = None
    feature_09: Optional[str] = None
    feature_10: Optional[str] = None

    price: Optional[float] = None
    sale_price: Optional[float] = None

    image_path: Optional[str] = None
    stock_quantity: int = 0
    low_stock_threshold: int = 10

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"


class ProductAdminUpdateRequest(BaseModel):
    show_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    show_pack_flag: Optional[str] = Field(default=None, pattern="^(Y|N)$")
    display_seq: Optional[int] = None

    product_name: Optional[str] = None
    product_model: Optional[str] = None
    product_slug: Optional[str] = None

    category_id: Optional[str] = None
    category_key: Optional[str] = None
    subcategory_key: Optional[str] = None
    subcategory: Optional[str] = None

    brand_id: Optional[str] = None
    product_brand_key: Optional[str] = None

    description: Optional[str] = None

    feature_01: Optional[str] = None
    feature_02: Optional[str] = None
    feature_03: Optional[str] = None
    feature_04: Optional[str] = None
    feature_05: Optional[str] = None
    feature_06: Optional[str] = None
    feature_07: Optional[str] = None
    feature_08: Optional[str] = None
    feature_09: Optional[str] = None
    feature_10: Optional[str] = None

    price: Optional[float] = None
    sale_price: Optional[float] = None

    image_path: Optional[str] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None

    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    updated_by: Optional[str] = "admin"
