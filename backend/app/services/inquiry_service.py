from datetime import datetime, timezone
from typing import Optional

from app.models.inquiry import Inquiry, InquiryCreate, InquiryListResponse, InquiryUpdate
from app.repositories.inquiry_repository import InquiryRepository
from app.services.customer_service import create_or_get_customer_from_inquiry
from app.services.id_service import generate_inquiry_id
from app.utils.normalization import clean_optional_text


# Temporary in-memory repository only.
# Later this will be replaced by DynamoDB using the same service-level behavior.
inquiry_repository = InquiryRepository()
MOCK_INQUIRIES = inquiry_repository.items


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
        product_id=clean_optional_text(inquiry_data.product_id),
        customer_name=inquiry_data.customer_name.strip(),
        contact_number=inquiry_data.contact_number.strip(),
        email=clean_optional_text(inquiry_data.email),
        subject=clean_optional_text(inquiry_data.subject),
        message=clean_optional_text(inquiry_data.message),
        source_page=clean_optional_text(inquiry_data.source_page),
        assigned_person=None,
        status="New",
        created_at=now,
        updated_at=now,
    )

    inquiry_repository.add(inquiry)

    return inquiry


def list_mock_inquiries(
    status: Optional[str] = None,
    assigned_person: Optional[str] = None,
    source_page: Optional[str] = None,
    search: Optional[str] = None,
) -> InquiryListResponse:
    inquiries = inquiry_repository.list_filtered(
        status=status,
        assigned_person=assigned_person,
        source_page=source_page,
        search=search,
    )

    return InquiryListResponse(items=inquiries, total=len(inquiries))


def get_mock_inquiry_by_id(inquiry_id: str) -> Optional[Inquiry]:
    return inquiry_repository.get_by_id(inquiry_id)


def update_mock_inquiry(inquiry_id: str, update_data: InquiryUpdate) -> Optional[Inquiry]:
    inquiry = inquiry_repository.get_by_id(inquiry_id)

    if inquiry is None:
        return None

    if update_data.assigned_person is not None:
        inquiry.assigned_person = clean_optional_text(update_data.assigned_person)

    if update_data.status is not None:
        inquiry.status = update_data.status

    inquiry.updated_at = datetime.now(timezone.utc)

    return inquiry
