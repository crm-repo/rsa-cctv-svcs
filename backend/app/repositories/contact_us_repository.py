from typing import Optional

from app.database import get_table_name
from app.models.contact_us import ContactUsRecord
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class ContactUsRepository(InMemoryRepository[ContactUsRecord]):
    repository_mode = "mock"
    table_name = "mock_contact_us"

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


class DynamoDBContactUsRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("contact_us")
        self._repository = DynamoDBRepository(self.table_name, id_field="contact_us_id")

    @staticmethod
    def _to_model(item: dict) -> ContactUsRecord:
        return ContactUsRecord.model_validate(item)

    def list_visible(self) -> list[ContactUsRecord]:
        return [
            self._to_model(item)
            for item in self._repository.list_all()
            if item.get("show_flag") == "Y"
        ]

    def list_visible_by_type(self, contact_type: str) -> list[ContactUsRecord]:
        contact_type_key = contact_type.strip().lower()
        records = [
            record
            for record in self.list_visible()
            if record.contact_type.lower() == contact_type_key
        ]
        records.sort(key=lambda record: record.display_seq)
        return records

    def get_visible_company_contact(self) -> Optional[ContactUsRecord]:
        records = self.list_visible_by_type("Company Contact")
        return records[0] if records else None
