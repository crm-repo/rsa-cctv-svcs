from datetime import datetime, timezone
from typing import Optional

from app.models.booking import Booking, BookingCreate, BookingListResponse, BookingUpdate
from app.repositories.booking_repository import BookingRepository
from app.services.customer_service import create_or_get_customer_from_booking
from app.services.id_service import generate_booking_id
from app.utils.normalization import clean_optional_text


# Temporary in-memory repository only.
# Later this will be replaced by DynamoDB using the same service-level behavior.
booking_repository = BookingRepository()
MOCK_BOOKINGS = booking_repository.items


def create_public_booking(booking_data: BookingCreate) -> Booking:
    customer = create_or_get_customer_from_booking(
        customer_name=booking_data.customer_name,
        contact_number=booking_data.contact_number,
        email_address=booking_data.email,
    )

    now = datetime.now(timezone.utc)

    booking = Booking(
        booking_id=generate_booking_id(),
        customer_id=customer.customer_id,
        customer_name=booking_data.customer_name.strip(),
        contact_number=booking_data.contact_number.strip(),
        email=clean_optional_text(booking_data.email),
        address=clean_optional_text(booking_data.address),
        preferred_date=booking_data.preferred_date,
        preferred_time=clean_optional_text(booking_data.preferred_time),
        service_interest=clean_optional_text(booking_data.service_interest),
        notes=clean_optional_text(booking_data.notes),
        booking_type="Site Visit Request",
        assigned_person=None,
        comments=None,
        status="New",
        created_at=now,
        updated_at=now,
    )

    booking_repository.add(booking)

    return booking


def list_mock_bookings(
    status: Optional[str] = None,
    assigned_person: Optional[str] = None,
    search: Optional[str] = None,
) -> BookingListResponse:
    bookings = booking_repository.list_filtered(
        status=status,
        assigned_person=assigned_person,
        search=search,
    )

    return BookingListResponse(items=bookings, total=len(bookings))


def get_mock_booking_by_id(booking_id: str) -> Optional[Booking]:
    return booking_repository.get_by_id(booking_id)


def update_mock_booking(booking_id: str, update_data: BookingUpdate) -> Optional[Booking]:
    booking = booking_repository.get_by_id(booking_id)

    if booking is None:
        return None

    if update_data.booking_type is not None:
        booking.booking_type = update_data.booking_type.strip()

    if update_data.assigned_person is not None:
        booking.assigned_person = clean_optional_text(update_data.assigned_person)

    if update_data.comments is not None:
        booking.comments = clean_optional_text(update_data.comments)

    if update_data.status is not None:
        booking.status = update_data.status

    booking.updated_at = datetime.now(timezone.utc)

    return booking
