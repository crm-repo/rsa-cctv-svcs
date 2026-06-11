from typing import Optional

from app.database import get_table_name
from app.models.brand import Brand
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class BrandRepository(InMemoryRepository[Brand]):
    repository_mode = "mock"
    table_name = "mock_brands"

    def __init__(self, initial_items: Optional[list[Brand]] = None):
        super().__init__(id_field="brand_id", initial_items=initial_items)

    def list_visible(self) -> list[Brand]:
        return self.list_where(lambda brand: brand.show_flag == "Y")

    def get_visible_by_id(self, brand_id: str) -> Optional[Brand]:
        brand = self.get_by_id(brand_id)
        if brand is None or brand.show_flag != "Y":
            return None
        return brand

    def get_visible_by_key(self, brand_key: str) -> Optional[Brand]:
        normalized_key = brand_key.strip().lower()
        for brand in self.list_visible():
            if brand.brand_key.lower() == normalized_key:
                return brand
        return None


class DynamoDBBrandRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("brands")
        self._repository = DynamoDBRepository(self.table_name, id_field="brand_id")

    @staticmethod
    def _to_model(item: dict) -> Brand:
        return Brand.model_validate(item)

    def list_all(self) -> list[Brand]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def list_visible(self) -> list[Brand]:
        return [brand for brand in self.list_all() if brand.show_flag == "Y"]

    def get_visible_by_id(self, brand_id: str) -> Optional[Brand]:
        item = self._repository.get_by_id(brand_id)
        if item is None:
            return None
        brand = self._to_model(item)
        if brand.show_flag != "Y":
            return None
        return brand

    def get_visible_by_key(self, brand_key: str) -> Optional[Brand]:
        normalized_key = brand_key.strip().lower()
        for brand in self.list_visible():
            if brand.brand_key.lower() == normalized_key:
                return brand
        return None
