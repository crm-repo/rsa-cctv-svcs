from typing import Optional

from app.database import TABLE_NAMES
from app.models.inquiry import Inquiry
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


STATUS_CREATED_AT_INDEX_NAME = "status-created_at-index"


class InquiryRepository(InMemoryRepository[Inquiry]):
    """Mock inquiry repository with status-created_at-index-ready list methods."""

    def __init__(self, initial_items: Optional[list[Inquiry]] = None, table_name: str = TABLE_NAMES.inquiries):
        super().__init__(id_field="inquiry_id", initial_items=initial_items)
        self.table_name = table_name
        self.repository_mode = "mock"

    def list_by_status(self, status: str) -> list[Inquiry]:
        status_key = status.strip().lower()
        return self.list_where(lambda inquiry: inquiry.status.lower() == status_key)

    def list_filtered(
        self,
        status: Optional[str] = None,
        assigned_person: Optional[str] = None,
        source_page: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Inquiry]:
        inquiries = self.list_all()

        if status:
            status_key = status.lower().strip()
            inquiries = [inquiry for inquiry in inquiries if inquiry.status.lower() == status_key]

        if assigned_person:
            assigned_person_key = assigned_person.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if (inquiry.assigned_person or "").lower() == assigned_person_key
            ]

        if source_page:
            source_page_key = source_page.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if (inquiry.source_page or "").lower() == source_page_key
            ]

        if search:
            search_key = search.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if search_key in inquiry.inquiry_id.lower()
                or search_key in inquiry.customer_name.lower()
                or search_key in inquiry.contact_number.lower()
                or search_key in (inquiry.email or "").lower()
                or search_key in (inquiry.subject or "").lower()
                or search_key in (inquiry.message or "").lower()
                or search_key in (inquiry.product_id or "").lower()
            ]

        inquiries.sort(key=lambda inquiry: inquiry.created_at, reverse=True)
        return inquiries


class DynamoDBInquiryRepository:
    """DynamoDB-backed inquiry repository for controlled future activation."""

    def __init__(self, table_name: str = TABLE_NAMES.inquiries):
        self.table_name = table_name
        self.repository_mode = "dynamodb"
        self.dynamodb = DynamoDBRepository(table_name=table_name, id_field="inquiry_id")

    @staticmethod
    def _to_model(item: dict) -> Inquiry:
        return Inquiry(**item)

    def list_all(self) -> list[Inquiry]:
        inquiries = [self._to_model(item) for item in self.dynamodb.list_all()]
        inquiries.sort(key=lambda inquiry: inquiry.created_at, reverse=True)
        return inquiries

    def get_by_id(self, inquiry_id: str) -> Optional[Inquiry]:
        item = self.dynamodb.get_by_id(inquiry_id)
        return self._to_model(item) if item else None

    def add(self, inquiry: Inquiry) -> Inquiry:
        return self.save(inquiry)

    def save(self, inquiry: Inquiry) -> Inquiry:
        self.dynamodb.put_item(inquiry)
        return inquiry

    def list_by_status(self, status: str) -> list[Inquiry]:
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
        source_page: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Inquiry]:
        inquiries = self.list_by_status(status) if status else self.list_all()

        if assigned_person:
            assigned_person_key = assigned_person.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if (inquiry.assigned_person or "").lower() == assigned_person_key
            ]

        if source_page:
            source_page_key = source_page.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if (inquiry.source_page or "").lower() == source_page_key
            ]

        if search:
            search_key = search.lower().strip()
            inquiries = [
                inquiry
                for inquiry in inquiries
                if search_key in inquiry.inquiry_id.lower()
                or search_key in inquiry.customer_name.lower()
                or search_key in inquiry.contact_number.lower()
                or search_key in (inquiry.email or "").lower()
                or search_key in (inquiry.subject or "").lower()
                or search_key in (inquiry.message or "").lower()
                or search_key in (inquiry.product_id or "").lower()
            ]

        inquiries.sort(key=lambda inquiry: inquiry.created_at, reverse=True)
        return inquiries
