from datetime import datetime, timezone

from app.models.inquiry import Inquiry, InquiryCreate
from app.services.customer_service import create_or_get_customer_from_inquiry


# Temporary in-memory storage only.
# Later this will be replaced by DynamoDB.
MOCK_INQUIRIES: list[Inquiry] = []


def _generate_inquiry_id() -> str:
    next_number = len(MOCK_INQUIRIES) + 1
    return f"INQ-{next_number:06d}"


def create_public_inquiry(inquiry_data: InquiryCreate) -> Inquiry:
    customer = create_or_get_customer_from_inquiry(
        customer_name=inquiry_data.customer_name,
        contact_number=inquiry_data.contact_number,
        email_address=inquiry_data.email,
    )

    now = datetime.now(timezone.utc)

    inquiry = Inquiry(
        inquiry_id=_generate_inquiry_id(),
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
    )

    MOCK_INQUIRIES.append(inquiry)

    return inquiry
