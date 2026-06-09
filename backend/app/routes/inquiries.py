from fastapi import APIRouter, status

from app.models.inquiry import Inquiry, InquiryCreate
from app.services.inquiry_service import create_public_inquiry

router = APIRouter()


@router.post("/inquiries", response_model=Inquiry, status_code=status.HTTP_201_CREATED)
def submit_inquiry(inquiry_data: InquiryCreate):
    return create_public_inquiry(inquiry_data)