from typing import Optional

from app.database import get_table_name
from app.models.category import Category
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class CategoryRepository(InMemoryRepository[Category]):
    repository_mode = "mock"
    table_name = "mock_categories"

    def __init__(self, initial_items: Optional[list[Category]] = None):
        super().__init__(id_field="category_id", initial_items=initial_items)

    def list_visible(self) -> list[Category]:
        return self.list_where(lambda category: category.show_flag == "Y")

    def get_visible_by_id(self, category_id: str) -> Optional[Category]:
        category = self.get_by_id(category_id)
        if category is None or category.show_flag != "Y":
            return None
        return category

    def get_visible_by_key(self, category_key: str) -> Optional[Category]:
        key = category_key.strip().lower()
        for category in self.list_visible():
            if category.category_key.lower() == key:
                return category
        return None

    def get_by_key(self, category_key: str) -> Optional[Category]:
        key = category_key.strip().lower()
        for category in self.list_all():
            if category.category_key.lower() == key:
                return category
        return None

    def save_category(self, category: Category) -> Category:
        return self.save(category)


class DynamoDBCategoryRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("categories")
        self._repository = DynamoDBRepository(self.table_name, id_field="category_id")

    @staticmethod
    def _to_model(item: dict) -> Category:
        return Category.model_validate(item)

    def list_all(self) -> list[Category]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def get_by_id(self, category_id: str) -> Optional[Category]:
        item = self._repository.get_by_id(category_id)
        return self._to_model(item) if item is not None else None

    def save_category(self, category: Category) -> Category:
        self._repository.put_item(category)
        return category

    def list_visible(self) -> list[Category]:
        return [category for category in self.list_all() if category.show_flag == "Y"]

    def get_visible_by_id(self, category_id: str) -> Optional[Category]:
        category = self.get_by_id(category_id)
        if category is None or category.show_flag != "Y":
            return None
        return category

    def get_visible_by_key(self, category_key: str) -> Optional[Category]:
        key = category_key.strip().lower()
        for category in self.list_visible():
            if category.category_key.lower() == key:
                return category
        return None

    def get_by_key(self, category_key: str) -> Optional[Category]:
        key = category_key.strip().lower()
        for category in self.list_all():
            if category.category_key.lower() == key:
                return category
        return None
