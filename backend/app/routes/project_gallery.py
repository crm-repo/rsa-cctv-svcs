from fastapi import APIRouter

from app.models.project_gallery import ProjectGalleryListResponse
from app.services.project_gallery_service import list_public_project_gallery

router = APIRouter()


@router.get("/project-gallery", response_model=ProjectGalleryListResponse)
def get_project_gallery():
    items = list_public_project_gallery()
    return ProjectGalleryListResponse(items=items, total=len(items))
