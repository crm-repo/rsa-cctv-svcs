from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.project_gallery import (
    ProjectGalleryAdminCreateRequest,
    ProjectGalleryAdminUpdateRequest,
    ProjectGalleryItem,
    ProjectGalleryListResponse,
)
from app.services.project_gallery_service import (
    create_admin_project,
    get_admin_project_by_id,
    list_admin_project_gallery,
    list_public_project_gallery,
    update_admin_project,
)

router = APIRouter()


@router.get("/admin/project-gallery", response_model=ProjectGalleryListResponse)
def get_admin_project_gallery(search: Optional[str] = Query(default=None)):
    return list_admin_project_gallery(search=search)


@router.post("/admin/project-gallery", response_model=ProjectGalleryItem, status_code=status.HTTP_201_CREATED)
def create_project_admin(request: ProjectGalleryAdminCreateRequest):
    try:
        return create_admin_project(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/project-gallery/{project_id}", response_model=ProjectGalleryItem)
def get_admin_project(project_id: str):
    project = get_admin_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project gallery item not found")
    return project


@router.put("/admin/project-gallery/{project_id}", response_model=ProjectGalleryItem)
def update_project_admin(project_id: str, request: ProjectGalleryAdminUpdateRequest):
    project = update_admin_project(project_id, request)
    if project is None:
        raise HTTPException(status_code=404, detail="Project gallery item not found")
    return project


@router.get("/project-gallery", response_model=ProjectGalleryListResponse)
def get_project_gallery():
    items = list_public_project_gallery()
    return ProjectGalleryListResponse(items=items, total=len(items))
