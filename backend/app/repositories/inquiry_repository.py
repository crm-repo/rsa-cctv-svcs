from typing import Optional

from app.database import TABLE_NAMES
from app.models.inquiry import Inquiry
from app.repositories.base_repository import InMemoryRepository


class InquiryRepository(InMemoryRepository[Inquiry]):
    """Inquiry repository with status-created_at-index-ready list methods."""

    def __init__(self, initial_items: Optional[list[Inquiry]] = None, table_name: str = TABLE_NAMES.inquiries):
        super().__init__(id_field="inquiry_id", initial_items=initial_items)
        self.table_name = table_name

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
