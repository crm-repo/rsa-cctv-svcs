from typing import Optional

from app.models.customer import Customer
from app.repositories.base_repository import InMemoryRepository


class CustomerRepository(InMemoryRepository[Customer]):
    def __init__(self, initial_items: Optional[list[Customer]] = None):
        super().__init__(id_field="customer_id", initial_items=initial_items)

    @staticmethod
    def normalize_contact_number(contact_number: str) -> str:
        return (
            contact_number.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

    @staticmethod
    def normalize_email(email_address: Optional[str]) -> Optional[str]:
        if email_address is None or email_address.strip() == "":
            return None
        return email_address.strip().lower()

    def find_by_contact_number(self, contact_number: str) -> Optional[Customer]:
        normalized_contact = self.normalize_contact_number(contact_number)

        for customer in self.items:
            if self.normalize_contact_number(customer.contact_number) == normalized_contact:
                return customer

        return None

    def find_by_contact_number_or_email(
        self,
        contact_number: str,
        email_address: Optional[str],
    ) -> Optional[Customer]:
        normalized_contact = self.normalize_contact_number(contact_number)
        normalized_email = self.normalize_email(email_address)

        for customer in self.items:
            contact_matches = self.normalize_contact_number(customer.contact_number) == normalized_contact
            email_matches = (
                normalized_email is not None
                and self.normalize_email(customer.email_address) == normalized_email
            )

            if contact_matches or email_matches:
                return customer

        return None
