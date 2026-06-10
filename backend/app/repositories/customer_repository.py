from typing import Optional

from app.database import TABLE_NAMES
from app.models.customer import Customer
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository
from app.utils.normalization import normalize_contact_number, normalize_email


CONTACT_NUMBER_INDEX_NAME = "contact_number_normalized-index"


class CustomerRepository(InMemoryRepository[Customer]):
    """Mock customer repository with DynamoDB-ready method names."""

    def __init__(self, initial_items: Optional[list[Customer]] = None, table_name: str = TABLE_NAMES.customers):
        super().__init__(id_field="customer_id", initial_items=initial_items)
        self.table_name = table_name
        self.repository_mode = "mock"

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


class DynamoDBCustomerRepository:
    """DynamoDB-backed customer repository for controlled future activation.

    This class is only used when RSA_REPOSITORY_MODE=dynamodb. The default mode
    remains mock, so local development does not need AWS credentials.
    """

    def __init__(self, table_name: str = TABLE_NAMES.customers):
        self.table_name = table_name
        self.repository_mode = "dynamodb"
        self.dynamodb = DynamoDBRepository(table_name=table_name, id_field="customer_id")

    @staticmethod
    def _to_model(item: dict) -> Customer:
        return Customer(**item)

    @staticmethod
    def _to_item(customer: Customer) -> dict:
        item = customer.model_dump(mode="python")
        item["contact_number_normalized"] = normalize_contact_number(customer.contact_number)
        normalized_email = normalize_email(customer.email_address)
        if normalized_email:
            item["email_address_normalized"] = normalized_email
        return item

    def list_all(self) -> list[Customer]:
        return [self._to_model(item) for item in self.dynamodb.list_all()]

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        item = self.dynamodb.get_by_id(customer_id)
        return self._to_model(item) if item else None

    def add(self, customer: Customer) -> Customer:
        return self.save(customer)

    def save(self, customer: Customer) -> Customer:
        self.dynamodb.put_item(self._to_item(customer))
        return customer

    def find_by_contact_number_normalized(self, contact_number: str) -> Optional[Customer]:
        normalized_contact = normalize_contact_number(contact_number)
        items = self.dynamodb.query_index(
            index_name=CONTACT_NUMBER_INDEX_NAME,
            key_name="contact_number_normalized",
            key_value=normalized_contact,
            limit=1,
            scan_index_forward=False,
        )
        return self._to_model(items[0]) if items else None

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
            status_key = customer_status.lower().strip()
            customers = [customer for customer in customers if customer.customer_status.lower() == status_key]

        if customer_from:
            source_key = customer_from.lower().strip()
            customers = [customer for customer in customers if customer.customer_from.lower() == source_key]

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
