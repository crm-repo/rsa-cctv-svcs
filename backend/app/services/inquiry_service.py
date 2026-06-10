from datetime import datetime, timezone
from typing import Optional

from app.models.inquiry import Inquiry, InquiryCreate, InquiryListResponse, InquiryUpdate
from app.services.id_service import generate_inquiry_id
from app.services.customer_service import create_or_get_customer_from_inquiry


# Temporary in-memory storage only.
# Later this will be replaced by DynamoDB.
MOCK_INQUIRIES: list[Inquiry] = []



def create_public_inquiry(inquiry_data: InquiryCreate) -> Inquiry:
    customer = create_or_get_customer_from_inquiry(
        customer_name=inquiry_data.customer_name,
        contact_number=inquiry_data.contact_number,
        email_address=inquiry_data.email,
    )

    now = datetime.now(timezone.utc)

    inquiry = Inquiry(
        inquiry_id=generate_inquiry_id(),
        customer_id=customer.customer_id,
        product_id=inquiry_data.product_id.strip() if inquiry_data.product_id else None,
        customer_name=inquiry_data.customer_name.strip(),
        contact_number=inquiry_data.contact_number.strip(),
        email=inquiry_data.email,
        subject=inquiry_data.subject.strip() if inquiry_data.subject else None,
        message=inquiry_data.message.strip() if inquiry_data.message else None,
        source_page=inquiry_data.source_page.strip() if inquiry_data.source_page else None,
        assigned_person=None,
        status="New",
        created_at=now,
        updated_at=now,
    )

    MOCK_INQUIRIES.append(inquiry)

    return inquiry


def list_mock_inquiries(
    status: Optional[str] = None,
    assigned_person: Optional[str] = None,
    source_page: Optional[str] = None,
    search: Optional[str] = None,
) -> InquiryListResponse:
    inquiries = MOCK_INQUIRIES.copy()

    if status:
        status_key = status.lower().strip()
        inquiries = [inquiry for inquiry in inquiries if inquiry.status.lower() == status_key]

    if assigned_person:
        assigned_person_key = assigned_person.lower().strip()
        inquiries = [
            inquiry
            for inquiry in inquiries
            if (inquiry.assigned_person or "").lower() == assigned_person_key
        ]

    if source_page:
        source_page_key = source_page.lower().strip()
        inquiries = [
            inquiry
            for inquiry in inquiries
            if (inquiry.source_page or "").lower() == source_page_key
        ]

    if search:
        search_key = search.lower().strip()
        inquiries = [
            inquiry
            for inquiry in inquiries
            if search_key in inquiry.inquiry_id.lower()
            or search_key in inquiry.customer_name.lower()
            or search_key in inquiry.contact_number.lower()
            or search_key in (inquiry.email or "").lower()
            or search_key in (inquiry.subject or "").lower()
            or search_key in (inquiry.message or "").lower()
            or search_key in (inquiry.product_id or "").lower()
        ]

    inquiries.sort(key=lambda inquiry: inquiry.created_at, reverse=True)

    return InquiryListResponse(items=inquiries, total=len(inquiries))


def get_mock_inquiry_by_id(inquiry_id: str) -> Optional[Inquiry]:
    for inquiry in MOCK_INQUIRIES:
        if inquiry.inquiry_id == inquiry_id:
            return inquiry

    return None


def update_mock_inquiry(inquiry_id: str, update_data: InquiryUpdate) -> Optional[Inquiry]:
    inquiry = get_mock_inquiry_by_id(inquiry_id)

    if inquiry is None:
        return None

    if update_data.assigned_person is not None:
        cleaned_assigned_person = update_data.assigned_person.strip()
        inquiry.assigned_person = cleaned_assigned_person or None

    if update_data.status is not None:
        inquiry.status = update_data.status

    inquiry.updated_at = datetime.now(timezone.utc)

    return inquiry
