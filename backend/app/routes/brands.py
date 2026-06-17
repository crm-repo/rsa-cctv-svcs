from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.brand import Brand, BrandAdminCreateRequest, BrandAdminUpdateRequest, BrandListResponse
from app.services.brand_service import (
    create_admin_brand,
    get_admin_brand_by_id,
    get_admin_brand_by_key,
    get_public_brand_by_id,
    get_public_brand_by_key,
    list_admin_brands,
    list_public_brands,
    update_admin_brand,
)

router = APIRouter()


@router.get("/admin/brands", response_model=BrandListResponse)
def get_admin_brands(search: Optional[str] = Query(default=None)):
    return list_admin_brands(search=search)


@router.post("/admin/brands", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_brand_admin(request: BrandAdminCreateRequest):
    try:
        return create_admin_brand(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/brands/key/{brand_key}", response_model=Brand)
def get_admin_brand_key(brand_key: str):
    brand = get_admin_brand_by_key(brand_key)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/admin/brands/{brand_id}", response_model=Brand)
def get_admin_brand(brand_id: str):
    brand = get_admin_brand_by_id(brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.put("/admin/brands/{brand_id}", response_model=Brand)
def update_brand_admin(brand_id: str, request: BrandAdminUpdateRequest):
    try:
        brand = update_admin_brand(brand_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/brands", response_model=BrandListResponse)
def get_brands(search: Optional[str] = Query(default=None)):
    return list_public_brands(search=search)


@router.get("/brands/key/{brand_key}", response_model=Brand)
def get_brand_by_key(brand_key: str):
    brand = get_public_brand_by_key(brand_key)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/brands/{brand_id}", response_model=Brand)
def get_brand(brand_id: str):
    brand = get_public_brand_by_id(brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand_admin_59b(brand_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.brand_service import delete_admin_brand
    try:
        deleted = delete_admin_brand(brand_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Brand not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
