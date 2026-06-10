from typing import Optional

from app.database import TABLE_NAMES
from app.models.booking import Booking
from app.repositories.base_repository import InMemoryRepository


class BookingRepository(InMemoryRepository[Booking]):
    """Booking repository with status-created_at-index-ready list methods."""

    def __init__(self, initial_items: Optional[list[Booking]] = None, table_name: str = TABLE_NAMES.bookings):
        super().__init__(id_field="booking_id", initial_items=initial_items)
        self.table_name = table_name

    def list_by_status(self, status: str) -> list[Booking]:
        status_key = status.strip().lower()
        return self.list_where(lambda booking: booking.status.lower() == status_key)

    def list_filtered(
        self,
        status: Optional[str] = None,
        assigned_person: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Booking]:
        bookings = self.list_all()

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
        return bookings
