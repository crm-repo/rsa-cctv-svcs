from typing import Optional

from app.models.product import Product
from app.repositories.base_repository import InMemoryRepository


class ProductRepository(InMemoryRepository[Product]):
    def __init__(self, initial_items: Optional[list[Product]] = None):
        super().__init__(id_field="product_id", initial_items=initial_items)

    def list_visible(self) -> list[Product]:
        return self.list_where(lambda product: product.show_flag == "Y")

    def get_visible_by_id(self, product_id: str) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product is None or product.show_flag != "Y":
            return None
        return product
