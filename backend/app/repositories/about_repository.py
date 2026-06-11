from typing import Optional

from app.database import get_table_name
from app.models.about import About
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class AboutRepository(InMemoryRepository[About]):
    repository_mode = "mock"
    table_name = "mock_about"

    def __init__(self, initial_items: Optional[list[About]] = None):
        super().__init__(id_field="about_id", initial_items=initial_items)

    def get_visible_about(self) -> Optional[About]:
        for about in self.items:
            if about.show_flag == "Y":
                return about
        return None


class DynamoDBAboutRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("about")
        self._repository = DynamoDBRepository(self.table_name, id_field="about_id")

    @staticmethod
    def _to_model(item: dict) -> About:
        return About.model_validate(item)

    def get_visible_about(self) -> Optional[About]:
        for item in self._repository.list_all():
            about = self._to_model(item)
            if about.show_flag == "Y":
                return about
        return None
