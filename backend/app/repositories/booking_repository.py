from typing import Optional

from app.database import TABLE_NAMES
from app.models.booking import Booking
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


STATUS_CREATED_AT_INDEX_NAME = "status-created_at-index"


class BookingRepository(InMemoryRepository[Booking]):
    """Mock booking repository with status-created_at-index-ready list methods."""

    def __init__(self, initial_items: Optional[list[Booking]] = None, table_name: str = TABLE_NAMES.bookings):
        super().__init__(id_field="booking_id", initial_items=initial_items)
        self.table_name = table_name
        self.repository_mode = "mock"

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


class DynamoDBBookingRepository:
    """DynamoDB-backed booking repository for controlled future activation."""

    def __init__(self, table_name: str = TABLE_NAMES.bookings):
        self.table_name = table_name
        self.repository_mode = "dynamodb"
        self.dynamodb = DynamoDBRepository(table_name=table_name, id_field="booking_id")

    @staticmethod
    def _to_model(item: dict) -> Booking:
        return Booking(**item)

    def list_all(self) -> list[Booking]:
        bookings = [self._to_model(item) for item in self.dynamodb.list_all()]
        bookings.sort(key=lambda booking: booking.created_at, reverse=True)
        return bookings

    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        item = self.dynamodb.get_by_id(booking_id)
        return self._to_model(item) if item else None

    def add(self, booking: Booking) -> Booking:
        return self.save(booking)

    def save(self, booking: Booking) -> Booking:
        self.dynamodb.put_item(booking)
        return booking

    def list_by_status(self, status: str) -> list[Booking]:
        items = self.dynamodb.query_index(
            index_name=STATUS_CREATED_AT_INDEX_NAME,
            key_name="status",
            key_value=status.strip(),
            scan_index_forward=False,
        )
        return [self._to_model(item) for item in items]

    def list_filtered(
        self,
        status: Optional[str] = None,
        assigned_person: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Booking]:
        bookings = self.list_by_status(status) if status else self.list_all()

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
