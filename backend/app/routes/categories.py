from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.category import (
    Category,
    CategoryAdminCreateRequest,
    CategoryAdminUpdateRequest,
    CategoryListResponse,
)
from app.services.category_service import (
    create_admin_category,
    get_admin_category_by_id,
    get_admin_category_by_key,
    get_public_category_by_id,
    get_public_category_by_key,
    list_admin_categories,
    list_public_categories,
    update_admin_category,
)

router = APIRouter()


@router.get("/admin/categories", response_model=CategoryListResponse)
def get_admin_categories(search: Optional[str] = Query(default=None)):
    return list_admin_categories(search=search)


@router.post("/admin/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category_admin(request: CategoryAdminCreateRequest):
    try:
        return create_admin_category(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/categories/key/{category_key}", response_model=Category)
def get_admin_category_key(category_key: str):
    category = get_admin_category_by_key(category_key)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/admin/categories/{category_id}", response_model=Category)
def get_admin_category(category_id: str):
    category = get_admin_category_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/admin/categories/{category_id}", response_model=Category)
def update_category_admin(category_id: str, request: CategoryAdminUpdateRequest):
    try:
        category = update_admin_category(category_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


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

# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_admin_59b(category_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.category_service import delete_admin_category
    try:
        deleted = delete_admin_category(category_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
