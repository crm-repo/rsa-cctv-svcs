from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.product import (
    Product,
    ProductAdminCreateRequest,
    ProductAdminUpdateRequest,
    ProductListResponse,
)
from app.services.product_service import (
    create_admin_product,
    get_admin_product_by_id,
    get_public_product_by_id,
    list_admin_products,
    list_public_products,
    update_admin_product,
)

router = APIRouter()


@router.get("/admin/products", response_model=ProductListResponse)
def get_admin_products(
    category: Optional[str] = Query(default=None),
    brand: Optional[str] = Query(default=None),
    sale: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=200, ge=1, le=500),
):
    return list_admin_products(category=category, brand=brand, sale=sale, search=search, page=page, per_page=per_page)


@router.post("/admin/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product_admin(request: ProductAdminCreateRequest):
    try:
        return create_admin_product(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/products/{product_id}", response_model=Product)
def get_admin_product(product_id: str):
    product = get_admin_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/admin/products/{product_id}", response_model=Product)
def update_product_admin(product_id: str, request: ProductAdminUpdateRequest):
    try:
        product = update_admin_product(product_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


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

# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_admin_59b(product_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.product_service import delete_admin_product
    try:
        deleted = delete_admin_product(product_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
