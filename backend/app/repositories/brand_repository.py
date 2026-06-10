from typing import Optional

from app.models.brand import Brand
from app.repositories.base_repository import InMemoryRepository


class BrandRepository(InMemoryRepository[Brand]):
    def __init__(self, initial_items: Optional[list[Brand]] = None):
        super().__init__(id_field="brand_id", initial_items=initial_items)

    def list_visible(self) -> list[Brand]:
        return self.list_where(lambda brand: brand.show_flag == "Y")

    def get_visible_by_id(self, brand_id: str) -> Optional[Brand]:
        brand = self.get_by_id(brand_id)
        if brand is None or brand.show_flag != "Y":
            return None
        return brand
