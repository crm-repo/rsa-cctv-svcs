from datetime import datetime, timezone
from typing import Literal, Optional

from app.models.customer import Customer, CustomerListResponse
from app.repositories.repository_factory import create_customer_repository
from app.services.id_service import generate_customer_id
from app.utils.normalization import clean_optional_text, normalize_contact_number, normalize_email


# Repository is selected by RSA_REPOSITORY_MODE. Default is mock.
customer_repository = create_customer_repository()
MOCK_CUSTOMERS = getattr(customer_repository, "items", [])


CustomerSource = Literal[
    "Inquiries",
    "Booking Request",
    "Social Media",
    "Referral",
    "Others",
    "Walk-In",
    "Phone Call",
    "Email",
]


def _normalize_contact_number(contact_number: str) -> str:
    return normalize_contact_number(contact_number)


def _normalize_email(email_address: Optional[str]) -> Optional[str]:
    return normalize_email(email_address)


def _find_existing_customer(
    contact_number: str,
    email_address: Optional[str] = None,
) -> Optional[Customer]:
    # Phase 8 v5 launch matching uses contact number only.
    # Email is stored/normalized for future use but does not drive matching at launch.
    return customer_repository.find_by_contact_number_normalized(contact_number)


def create_or_get_customer_from_lead(
    customer_name: str,
    contact_number: str,
    email_address: Optional[str],
    customer_from: CustomerSource,
) -> Customer:
    existing_customer = _find_existing_customer(
        contact_number=contact_number,
        email_address=email_address,
    )

    now = datetime.now(timezone.utc)
    cleaned_email = clean_optional_text(email_address)

    if existing_customer is not None:
        # Keep the original source and status, but fill missing email if the new lead provided one.
        if existing_customer.email_address is None and cleaned_email:
            existing_customer.email_address = cleaned_email

        existing_customer.updated_at = now
        customer_repository.save(existing_customer)
        return existing_customer

    customer = Customer(
        customer_id=generate_customer_id(),
        customer_name=customer_name.strip(),
        customer_status="Prospect",
        customer_category=None,
        email_address=cleaned_email,
        contact_number=contact_number.strip(),
        customer_from=customer_from,
        sales_person=None,
        repeat_customer="N",
        created_at=now,
        updated_at=now,
    )

    customer_repository.add(customer)

    return customer


def create_or_get_customer_from_booking(
    customer_name: str,
    contact_number: str,
    email_address: Optional[str],
) -> Customer:
    return create_or_get_customer_from_lead(
        customer_name=customer_name,
        contact_number=contact_number,
        email_address=email_address,
        customer_from="Booking Request",
    )


def create_or_get_customer_from_inquiry(
    customer_name: str,
    contact_number: str,
    email_address: Optional[str],
) -> Customer:
    return create_or_get_customer_from_lead(
        customer_name=customer_name,
        contact_number=contact_number,
        email_address=email_address,
        customer_from="Inquiries",
    )


def list_mock_customers(
    customer_status: Optional[str] = None,
    customer_from: Optional[str] = None,
    search: Optional[str] = None,
) -> CustomerListResponse:
    customers = customer_repository.list_filtered(
        customer_status=customer_status,
        customer_from=customer_from,
        search=search,
    )

    return CustomerListResponse(
        items=customers,
        total=len(customers),
    )


def get_mock_customer_by_id(customer_id: str) -> Optional[Customer]:
    return customer_repository.get_by_id(customer_id)
