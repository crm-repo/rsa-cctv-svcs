from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.service import Service, ServiceAdminCreateRequest, ServiceAdminUpdateRequest, ServiceListResponse
from app.services.service_service import (
    create_admin_service,
    get_admin_service_by_id,
    get_public_service_by_slug,
    list_admin_services,
    list_public_services,
    update_admin_service,
)

router = APIRouter()


@router.get("/admin/services", response_model=ServiceListResponse)
def get_admin_services(search: Optional[str] = Query(default=None)):
    items = list_admin_services(search=search)
    return ServiceListResponse(items=items, total=len(items))


@router.post("/admin/services", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service_admin(request: ServiceAdminCreateRequest):
    try:
        return create_admin_service(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/services/{service_id}", response_model=Service)
def get_admin_service(service_id: str):
    service = get_admin_service_by_id(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.put("/admin/services/{service_id}", response_model=Service)
def update_service_admin(service_id: str, request: ServiceAdminUpdateRequest):
    service = update_admin_service(service_id, request)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


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
