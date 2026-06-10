from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.category import Category, CategoryListResponse
from app.services.category_service import (
    get_public_category_by_id,
    get_public_category_by_key,
    list_public_categories,
)

router = APIRouter()


@router.get("/categories", response_model=CategoryListResponse)
def get_categories(search: Optional[str] = Query(default=None)):
    return list_public_categories(search=search)


@router.get("/categories/key/{category_key}", response_model=Category)
def get_category_by_key(category_key: str):
    category = get_public_category_by_key(category_key)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: str):
    category = get_public_category_by_id(category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category
