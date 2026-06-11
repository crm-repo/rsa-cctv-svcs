from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.contact_us import (
    ContactPageResponse,
    ContactUsAdminCreateRequest,
    ContactUsAdminUpdateRequest,
    ContactUsRecord,
    ContactUsRecordListResponse,
)
from app.services.contact_us_service import (
    create_admin_contact_record,
    get_admin_contact_record_by_id,
    get_public_contact_page,
    list_admin_contact_records,
    list_public_contact_persons,
    list_public_social_media,
    update_admin_contact_record,
)

router = APIRouter()


@router.get("/admin/contact-us", response_model=ContactUsRecordListResponse)
def get_admin_contact_us(search: Optional[str] = Query(default=None), contact_type: Optional[str] = Query(default=None)):
    return list_admin_contact_records(search=search, contact_type=contact_type)


@router.post("/admin/contact-us", response_model=ContactUsRecord, status_code=status.HTTP_201_CREATED)
def create_contact_us_admin(request: ContactUsAdminCreateRequest):
    try:
        return create_admin_contact_record(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/contact-us/{contact_us_id}", response_model=ContactUsRecord)
def get_admin_contact_us_record(contact_us_id: str):
    record = get_admin_contact_record_by_id(contact_us_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return record


@router.put("/admin/contact-us/{contact_us_id}", response_model=ContactUsRecord)
def update_contact_us_admin(contact_us_id: str, request: ContactUsAdminUpdateRequest):
    record = update_admin_contact_record(contact_us_id, request)
    if record is None:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return record


@router.get("/contact", response_model=ContactPageResponse)
def get_contact():
    return get_public_contact_page()


@router.get("/contact-persons", response_model=ContactUsRecordListResponse)
def get_contact_persons():
    items = list_public_contact_persons()
    return ContactUsRecordListResponse(items=items, total=len(items))


@router.get("/social-media", response_model=ContactUsRecordListResponse)
def get_social_media():
    items = list_public_social_media()
    return ContactUsRecordListResponse(items=items, total=len(items))
