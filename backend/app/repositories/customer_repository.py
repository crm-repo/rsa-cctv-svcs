from typing import Optional

from app.database import TABLE_NAMES
from app.models.customer import Customer
from app.repositories.base_repository import InMemoryRepository
from app.utils.normalization import normalize_contact_number, normalize_email


class CustomerRepository(InMemoryRepository[Customer]):
    """Customer repository with DynamoDB-ready method names.

    Final launch matching uses contact_number_normalized-index. Email is stored
    normalized later but is not a launch GSI.
    """

    def __init__(self, initial_items: Optional[list[Customer]] = None, table_name: str = TABLE_NAMES.customers):
        super().__init__(id_field="customer_id", initial_items=initial_items)
        self.table_name = table_name

    def find_by_contact_number_normalized(self, contact_number: str) -> Optional[Customer]:
        normalized_contact = normalize_contact_number(contact_number)

        for customer in self.items:
            if normalize_contact_number(customer.contact_number) == normalized_contact:
                return customer

        return None

    def find_by_contact_number(self, contact_number: str) -> Optional[Customer]:
        return self.find_by_contact_number_normalized(contact_number)

    def list_filtered(
        self,
        customer_status: Optional[str] = None,
        customer_from: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[Customer]:
        customers = self.list_all()

        if customer_status:
            customers = [
                customer
                for customer in customers
                if customer.customer_status.lower() == customer_status.lower().strip()
            ]

        if customer_from:
            customers = [
                customer
                for customer in customers
                if customer.customer_from.lower() == customer_from.lower().strip()
            ]

        if search:
            search_key = search.lower().strip()
            customers = [
                customer
                for customer in customers
                if search_key in customer.customer_name.lower()
                or search_key in customer.contact_number.lower()
                or search_key in (customer.email_address or "").lower()
                or search_key in normalize_contact_number(customer.contact_number).lower()
                or search_key in (normalize_email(customer.email_address) or "")
            ]

        customers.sort(key=lambda customer: customer.created_at, reverse=True)
        return customers
