from datetime import datetime, timezone
from typing import Literal, Optional

from app.models.customer import Customer, CustomerListResponse


# Temporary in-memory storage only.
# Later this will be replaced by DynamoDB.
MOCK_CUSTOMERS: list[Customer] = []


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


def _generate_customer_id() -> str:
    next_number = len(MOCK_CUSTOMERS) + 1
    return f"CUST-{next_number:06d}"


def _normalize_contact_number(contact_number: str) -> str:
    return (
        contact_number.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def _normalize_email(email_address: Optional[str]) -> Optional[str]:
    if email_address is None or email_address.strip() == "":
        return None

    return email_address.strip().lower()


def _find_existing_customer(
    contact_number: str,
    email_address: Optional[str] = None,
) -> Optional[Customer]:
    normalized_contact = _normalize_contact_number(contact_number)
    normalized_email = _normalize_email(email_address)

    for customer in MOCK_CUSTOMERS:
        customer_contact = _normalize_contact_number(customer.contact_number)
        customer_email = _normalize_email(customer.email_address)

        contact_matches = customer_contact == normalized_contact
        email_matches = (
            normalized_email is not None
            and customer_email is not None
            and customer_email == normalized_email
        )

        if contact_matches or email_matches:
            return customer

    return None


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

    if existing_customer is not None:
        # Keep the original source and status, but fill missing email if the new lead provided one.
        if existing_customer.email_address is None and email_address:
            existing_customer.email_address = email_address.strip()

        existing_customer.updated_at = now
        return existing_customer

    customer = Customer(
        customer_id=_generate_customer_id(),
        customer_name=customer_name.strip(),
        customer_status="Prospect",
        customer_category=None,
        email_address=email_address.strip() if email_address else None,
        contact_number=contact_number.strip(),
        customer_from=customer_from,
        sales_person=None,
        repeat_customer="N",
        created_at=now,
        updated_at=now,
    )

    MOCK_CUSTOMERS.append(customer)

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
    customers = MOCK_CUSTOMERS.copy()

    if customer_status:
        customers = [
            customer
            for customer in customers
            if customer.customer_status.lower() == customer_status.lower().strip()
        ]

    if customer_from:
        customers = [
            customer
            for customer in customers
            if customer.customer_from.lower() == customer_from.lower().strip()
        ]

    if search:
        search_key = search.lower().strip()

        customers = [
            customer
            for customer in customers
            if search_key in customer.customer_name.lower()
            or search_key in customer.contact_number.lower()
            or search_key in (customer.email_address or "").lower()
        ]

    customers.sort(key=lambda customer: customer.created_at, reverse=True)

    return CustomerListResponse(
        items=customers,
        total=len(customers),
    )


def get_mock_customer_by_id(customer_id: str) -> Optional[Customer]:
    for customer in MOCK_CUSTOMERS:
        if customer.customer_id == customer_id:
            return customer

    return None
