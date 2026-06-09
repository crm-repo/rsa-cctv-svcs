from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.inquiry import Inquiry, InquiryCreate, InquiryListResponse, InquiryUpdate
from app.services.inquiry_service import (
    create_public_inquiry,
    get_mock_inquiry_by_id,
    list_mock_inquiries,
    update_mock_inquiry,
)

router = APIRouter()


@router.post("/inquiries", response_model=Inquiry, status_code=status.HTTP_201_CREATED)
def submit_inquiry(inquiry_data: InquiryCreate):
    return create_public_inquiry(inquiry_data)


@router.get("/inquiries", response_model=InquiryListResponse)
def get_inquiries(
    status: Optional[str] = Query(default=None),
    assigned_person: Optional[str] = Query(default=None),
    source_page: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    return list_mock_inquiries(
        status=status,
        assigned_person=assigned_person,
        source_page=source_page,
        search=search,
    )


@router.get("/inquiries/{inquiry_id}", response_model=Inquiry)
def get_inquiry(inquiry_id: str):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    inquiry = get_mock_inquiry_by_id(inquiry_id)

    if inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    return inquiry


@router.put("/inquiries/{inquiry_id}", response_model=Inquiry)
def update_inquiry(inquiry_id: str, update_data: InquiryUpdate):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    inquiry = update_mock_inquiry(inquiry_id=inquiry_id, update_data=update_data)

    if inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    return inquiry
