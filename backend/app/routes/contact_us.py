from fastapi import APIRouter

from app.models.contact_us import ContactPageResponse, ContactUsRecordListResponse
from app.services.contact_us_service import (
    get_public_contact_page,
    list_public_contact_persons,
    list_public_social_media,
)

router = APIRouter()


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
