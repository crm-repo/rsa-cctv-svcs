from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.brand import Brand, BrandListResponse
from app.services.brand_service import (
    get_public_brand_by_id,
    get_public_brand_by_key,
    list_public_brands,
)

router = APIRouter()


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
