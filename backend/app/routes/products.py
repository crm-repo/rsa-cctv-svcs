from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.product import Product, ProductListResponse
from app.services.product_service import get_public_product_by_id, list_public_products

router = APIRouter()


@router.get("/products", response_model=ProductListResponse)
def get_products(
    category: Optional[str] = Query(default=None),
    brand: Optional[str] = Query(default=None),
    sale: Optional[bool] = Query(
        default=None,
        description="Filters products by sale status. Sale is derived from sale_price, not a separate flag.",
    ),
    search: Optional[str] = Query(default=None),
    sort: str = Query(
        default="default",
        pattern="^(default|price_low|price_high|newly_added|on_sale)$",
    ),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=12, ge=1, le=50),
):
    return list_public_products(
        category=category,
        brand=brand,
        sale=sale,
        search=search,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = get_public_product_by_id(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product