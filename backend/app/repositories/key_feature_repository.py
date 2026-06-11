from typing import Optional

from app.database import get_table_name
from app.models.key_feature import KeyFeature
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class KeyFeatureRepository(InMemoryRepository[KeyFeature]):
    repository_mode = "mock"
    table_name = "mock_key_features"

    def __init__(self, initial_items: Optional[list[KeyFeature]] = None):
        super().__init__(id_field="key_feat_id", initial_items=initial_items)

    def search_by_name(self, search: str) -> list[KeyFeature]:
        search_key = search.strip().lower()
        return self.list_where(lambda feature: search_key in feature.key_feat_name.lower())


class DynamoDBKeyFeatureRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("key_features")
        self._repository = DynamoDBRepository(self.table_name, id_field="key_feat_id")

    @staticmethod
    def _to_model(item: dict) -> KeyFeature:
        return KeyFeature.model_validate(item)

    def list_all(self) -> list[KeyFeature]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def get_by_id(self, key_feat_id: str) -> Optional[KeyFeature]:
        item = self._repository.get_by_id(key_feat_id)
        return self._to_model(item) if item is not None else None

    def search_by_name(self, search: str) -> list[KeyFeature]:
        search_key = search.strip().lower()
        return [
            feature
            for feature in self.list_all()
            if search_key in feature.key_feat_name.lower()
        ]
