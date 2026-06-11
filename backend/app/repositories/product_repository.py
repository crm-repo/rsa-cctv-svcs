from typing import Optional

from app.database import get_table_name
from app.models.product import Product
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class ProductRepository(InMemoryRepository[Product]):
    repository_mode = "mock"
    table_name = "mock_products"

    def __init__(self, initial_items: Optional[list[Product]] = None):
        super().__init__(id_field="product_id", initial_items=initial_items)

    def list_visible(self) -> list[Product]:
        return self.list_where(lambda product: product.show_flag == "Y")

    def get_visible_by_id(self, product_id: str) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product is None or product.show_flag != "Y":
            return None
        return product


class DynamoDBProductRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("products")
        self._repository = DynamoDBRepository(self.table_name, id_field="product_id")

    @staticmethod
    def _to_model(item: dict) -> Product:
        return Product.model_validate(item)

    def list_all(self) -> list[Product]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def list_visible(self) -> list[Product]:
        return [product for product in self.list_all() if product.show_flag == "Y"]

    def get_visible_by_id(self, product_id: str) -> Optional[Product]:
        item = self._repository.get_by_id(product_id)
        if item is None:
            return None
        product = self._to_model(item)
        if product.show_flag != "Y":
            return None
        return product
