from datetime import datetime, timezone

from app.models.booking import Booking, BookingCreate


# Temporary in-memory storage only.
# Later this will be replaced by DynamoDB.
MOCK_BOOKINGS: list[Booking] = []


def _generate_booking_id() -> str:
    next_number = len(MOCK_BOOKINGS) + 1
    return f"BOOK-{next_number:06d}"


def create_public_booking(booking_data: BookingCreate) -> Booking:
    now = datetime.now(timezone.utc)

    booking = Booking(
        booking_id=_generate_booking_id(),
        customer_id=None,  # Future: auto-created or linked customer ID
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