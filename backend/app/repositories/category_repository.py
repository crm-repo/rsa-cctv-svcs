from typing import Optional

from app.models.category import Category
from app.repositories.base_repository import InMemoryRepository


class CategoryRepository(InMemoryRepository[Category]):
    def __init__(self, initial_items: Optional[list[Category]] = None):
        super().__init__(id_field="category_id", initial_items=initial_items)

    def list_visible(self) -> list[Category]:
        return self.list_where(lambda category: category.show_flag == "Y")

    def get_visible_by_key(self, category_key: str) -> Optional[Category]:
        key = category_key.strip().lower()
        for category in self.list_visible():
            if category.category_key.lower() == key:
                return category
        return None
