from typing import Optional

from app.models.inquiry import Inquiry
from app.repositories.base_repository import InMemoryRepository


class InquiryRepository(InMemoryRepository[Inquiry]):
    def __init__(self, initial_items: Optional[list[Inquiry]] = None):
        super().__init__(id_field="inquiry_id", initial_items=initial_items)

    def list_by_status(self, status: str) -> list[Inquiry]:
        status_key = status.strip().lower()
        return self.list_where(lambda inquiry: inquiry.status.lower() == status_key)
