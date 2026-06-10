from typing import Optional

from app.models.booking import Booking
from app.repositories.base_repository import InMemoryRepository


class BookingRepository(InMemoryRepository[Booking]):
    def __init__(self, initial_items: Optional[list[Booking]] = None):
        super().__init__(id_field="booking_id", initial_items=initial_items)

    def list_by_status(self, status: str) -> list[Booking]:
        status_key = status.strip().lower()
        return self.list_where(lambda booking: booking.status.lower() == status_key)
