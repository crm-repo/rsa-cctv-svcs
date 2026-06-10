from fastapi import APIRouter, HTTPException

from app.models.service import Service, ServiceListResponse
from app.services.service_service import get_public_service_by_slug, list_public_services

router = APIRouter()


@router.get("/services", response_model=ServiceListResponse)
def get_services():
    items = list_public_services()
    return ServiceListResponse(items=items, total=len(items))


@router.get("/services/{service_slug}", response_model=Service)
def get_service_by_slug(service_slug: str):
    service = get_public_service_by_slug(service_slug)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
