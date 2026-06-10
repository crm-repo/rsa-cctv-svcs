from typing import Optional

from app.models.key_feature import KeyFeature
from app.repositories.base_repository import InMemoryRepository


class KeyFeatureRepository(InMemoryRepository[KeyFeature]):
    def __init__(self, initial_items: Optional[list[KeyFeature]] = None):
        super().__init__(id_field="key_feat_id", initial_items=initial_items)

    def search_by_name(self, search: str) -> list[KeyFeature]:
        search_key = search.strip().lower()
        return self.list_where(lambda feature: search_key in feature.key_feat_name.lower())
