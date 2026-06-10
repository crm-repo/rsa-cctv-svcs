from typing import Optional

from app.models.project_gallery import ProjectGalleryItem
from app.repositories.base_repository import InMemoryRepository


class ProjectGalleryRepository(InMemoryRepository[ProjectGalleryItem]):
    def __init__(self, initial_items: Optional[list[ProjectGalleryItem]] = None):
        super().__init__(id_field="project_id", initial_items=initial_items)

    def list_visible_sorted(self) -> list[ProjectGalleryItem]:
        items = self.list_where(lambda item: item.show_flag == "Y")
        items.sort(key=lambda item: item.display_seq)
        return items
