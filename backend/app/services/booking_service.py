from datetime import datetime, timezone
from typing import Optional

from app.models.booking import Booking, BookingCreate, BookingListResponse, BookingUpdate
from app.services.customer_service import create_or_get_customer_from_booking


# Temporary in-memory storage only.
# Later this will be replaced by DynamoDB.
MOCK_BOOKINGS: list[Booking] = []


def _generate_booking_id() -> str:
    next_number = len(MOCK_BOOKINGS) + 1
    return f"BOOK-{next_number:06d}"


def create_public_booking(booking_data: BookingCreate) -> Booking:
    customer = create_or_get_customer_from_booking(
        customer_name=booking_data.customer_name,
        contact_number=booking_data.contact_number,
        email_address=booking_data.email,
    )

    now = datetime.now(timezone.utc)

    booking = Booking(
        booking_id=_generate_booking_id(),
        customer_id=customer.customer_id,
        customer_name=booking_data.customer_name.strip(),
        contact_number=booking_data.contact_number.strip(),
        email=booking_data.email,
        address=booking_data.address.strip() if booking_data.address else None,
        preferred_date=booking_data.preferred_date,
        preferred_time=booking_data.preferred_time.strip() if booking_data.preferred_time else None,
        service_interest=booking_data.service_interest.strip() if booking_data.service_interest else None,
        notes=booking_data.notes.strip() if booking_data.notes else None,
        booking_type="Site Visit Request",
        assigned_person=None,
        comments=None,
        status="New",
        created_at=now,
        updated_at=now,
    )

    MOCK_BOOKINGS.append(booking)

    return booking


def list_mock_bookings(
    status: Optional[str] = None,
    assigned_person: Optional[str] = None,
    search: Optional[str] = None,
) -> BookingListResponse:
    bookings = MOCK_BOOKINGS.copy()

    if status:
        status_key = status.lower().strip()
        bookings = [booking for booking in bookings if booking.status.lower() == status_key]

    if assigned_person:
        assigned_person_key = assigned_person.lower().strip()
        bookings = [
            booking
            for booking in bookings
            if (booking.assigned_person or "").lower() == assigned_person_key
        ]

    if search:
        search_key = search.lower().strip()
        bookings = [
            booking
            for booking in bookings
            if search_key in booking.booking_id.lower()
            or search_key in booking.customer_name.lower()
            or search_key in booking.contact_number.lower()
            or search_key in (booking.email or "").lower()
            or search_key in (booking.service_interest or "").lower()
            or search_key in (booking.address or "").lower()
        ]

    bookings.sort(key=lambda booking: booking.created_at, reverse=True)

    return BookingListResponse(items=bookings, total=len(bookings))


def get_mock_booking_by_id(booking_id: str) -> Optional[Booking]:
    for booking in MOCK_BOOKINGS:
        if booking.booking_id == booking_id:
            return booking

    return None


def update_mock_booking(booking_id: str, update_data: BookingUpdate) -> Optional[Booking]:
    booking = get_mock_booking_by_id(booking_id)

    if booking is None:
        return None

    if update_data.booking_type is not None:
        booking.booking_type = update_data.booking_type.strip()

    if update_data.assigned_person is not None:
        cleaned_assigned_person = update_data.assigned_person.strip()
        booking.assigned_person = cleaned_assigned_person or None

    if update_data.comments is not None:
        cleaned_comments = update_data.comments.strip()
        booking.comments = cleaned_comments or None

    if update_data.status is not None:
        booking.status = update_data.status

    booking.updated_at = datetime.now(timezone.utc)

    return booking
