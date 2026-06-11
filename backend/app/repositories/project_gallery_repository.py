from typing import Optional

from app.database import get_table_name
from app.models.project_gallery import ProjectGalleryItem
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class ProjectGalleryRepository(InMemoryRepository[ProjectGalleryItem]):
    repository_mode = "mock"
    table_name = "mock_project_gallery"

    def __init__(self, initial_items: Optional[list[ProjectGalleryItem]] = None):
        super().__init__(id_field="project_id", initial_items=initial_items)

    def list_visible_sorted(self) -> list[ProjectGalleryItem]:
        items = self.list_where(lambda item: item.show_flag == "Y")
        items.sort(key=lambda item: item.display_seq)
        return items


class DynamoDBProjectGalleryRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("project_gallery")
        self._repository = DynamoDBRepository(self.table_name, id_field="project_id")

    @staticmethod
    def _to_model(item: dict) -> ProjectGalleryItem:
        return ProjectGalleryItem.model_validate(item)

    def list_visible_sorted(self) -> list[ProjectGalleryItem]:
        items = [self._to_model(item) for item in self._repository.list_all()]
        items = [item for item in items if item.show_flag == "Y"]
        items.sort(key=lambda item: item.display_seq)
        return items
