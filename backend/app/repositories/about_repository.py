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

    def save_about(self, about: About) -> About:
        return self.save(about)


class DynamoDBAboutRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("about")
        self._repository = DynamoDBRepository(self.table_name, id_field="about_id")

    @staticmethod
    def _to_model(item: dict) -> About:
        return About.model_validate(item)

    def list_all(self) -> list[About]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def get_by_id(self, about_id: str) -> Optional[About]:
        item = self._repository.get_by_id(about_id)
        return self._to_model(item) if item is not None else None

    def get_visible_about(self) -> Optional[About]:
        for about in self.list_all():
            if about.show_flag == "Y":
                return about
        return None

    def save_about(self, about: About) -> About:
        self._repository.put_item(about)
        return about
