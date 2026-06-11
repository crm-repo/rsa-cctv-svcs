from fastapi import APIRouter, HTTPException, status

from app.models.about import About, AboutAdminCreateRequest, AboutAdminUpdateRequest, AboutListResponse
from app.services.about_service import (
    create_admin_about,
    get_admin_about_by_id,
    get_public_about,
    list_admin_about,
    update_admin_about,
)

router = APIRouter()


@router.get("/admin/about", response_model=AboutListResponse)
def get_admin_about_records():
    return list_admin_about()


@router.post("/admin/about", response_model=About, status_code=status.HTTP_201_CREATED)
def create_about_admin(request: AboutAdminCreateRequest):
    try:
        return create_admin_about(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/about/{about_id}", response_model=About)
def get_admin_about(about_id: str):
    about = get_admin_about_by_id(about_id)
    if about is None:
        raise HTTPException(status_code=404, detail="About content not found")
    return about


@router.put("/admin/about/{about_id}", response_model=About)
def update_about_admin(about_id: str, request: AboutAdminUpdateRequest):
    about = update_admin_about(about_id, request)
    if about is None:
        raise HTTPException(status_code=404, detail="About content not found")
    return about


@router.get("/about", response_model=About)
def get_about():
    about = get_public_about()
    if about is None:
        raise HTTPException(status_code=404, detail="About content not found")
    return about
