from typing import Optional

from app.models.contact_us import ContactUsRecord
from app.repositories.base_repository import InMemoryRepository


class ContactUsRepository(InMemoryRepository[ContactUsRecord]):
    def __init__(self, initial_items: Optional[list[ContactUsRecord]] = None):
        super().__init__(id_field="contact_us_id", initial_items=initial_items)

    def list_visible(self) -> list[ContactUsRecord]:
        return self.list_where(lambda record: record.show_flag == "Y")

    def list_visible_by_type(self, contact_type: str) -> list[ContactUsRecord]:
        contact_type_key = contact_type.strip().lower()
        records = self.list_where(
            lambda record: record.show_flag == "Y" and record.contact_type.lower() == contact_type_key
        )
        records.sort(key=lambda record: record.display_seq)
        return records

    def get_visible_company_contact(self) -> Optional[ContactUsRecord]:
        records = self.list_visible_by_type("Company Contact")
        return records[0] if records else None
