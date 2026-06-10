"""Repository factory for RSA CMS / Mini-CRM.

Batch 8 introduces an explicit environment-based repository switch while
keeping mock mode as the safe default.

Supported modes:
- RSA_REPOSITORY_MODE=mock      local/in-memory repositories, default
- RSA_REPOSITORY_MODE=dynamodb  DynamoDB-backed CRM repositories, only after AWS setup
"""

from __future__ import annotations

from typing import Any

from app.database import get_repository_mode, get_repository_mode_summary
from app.repositories.booking_repository import BookingRepository, DynamoDBBookingRepository
from app.repositories.customer_repository import CustomerRepository, DynamoDBCustomerRepository
from app.repositories.inquiry_repository import DynamoDBInquiryRepository, InquiryRepository


def create_customer_repository() -> CustomerRepository | DynamoDBCustomerRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBCustomerRepository()
    return CustomerRepository()


def create_booking_repository() -> BookingRepository | DynamoDBBookingRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBBookingRepository()
    return BookingRepository()


def create_inquiry_repository() -> InquiryRepository | DynamoDBInquiryRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBInquiryRepository()
    return InquiryRepository()


def describe_repository(repository: Any) -> dict[str, str]:
    return {
        "class_name": repository.__class__.__name__,
        "repository_mode": getattr(repository, "repository_mode", get_repository_mode()),
        "table_name": getattr(repository, "table_name", ""),
    }


def get_crm_repository_summary() -> dict[str, Any]:
    """Return a safe local summary without making AWS calls."""

    customer_repository = create_customer_repository()
    booking_repository = create_booking_repository()
    inquiry_repository = create_inquiry_repository()

    return {
        "mode_summary": get_repository_mode_summary(),
        "repositories": {
            "customers": describe_repository(customer_repository),
            "bookings": describe_repository(booking_repository),
            "inquiries": describe_repository(inquiry_repository),
        },
        "aws_calls_made": False,
    }
