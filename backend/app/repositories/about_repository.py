from typing import Optional

from app.models.about import About
from app.repositories.base_repository import InMemoryRepository


class AboutRepository(InMemoryRepository[About]):
    def __init__(self, initial_items: Optional[list[About]] = None):
        super().__init__(id_field="about_id", initial_items=initial_items)

    def get_visible_about(self) -> Optional[About]:
        for about in self.items:
            if about.show_flag == "Y":
                return about
        return None
