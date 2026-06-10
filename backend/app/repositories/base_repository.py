from collections.abc import Callable
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class InMemoryRepository(Generic[T]):
    """Small reusable in-memory repository helper.

    This is intentionally simple. It prepares the codebase for the final
    Route -> Service -> Repository -> DynamoDB shape, without creating AWS
    resources yet.
    """

    def __init__(self, id_field: str, initial_items: Optional[list[T]] = None):
        self.id_field = id_field
        self.items: list[T] = initial_items if initial_items is not None else []

    def list_all(self) -> list[T]:
        return self.items.copy()

    def list_where(self, predicate: Callable[[T], bool]) -> list[T]:
        return [item for item in self.items if predicate(item)]

    def get_by_id(self, item_id: str) -> Optional[T]:
        for item in self.items:
            if getattr(item, self.id_field) == item_id:
                return item
        return None

    def add(self, item: T) -> T:
        self.items.append(item)
        return item

    def update(self, item_id: str, update_callback: Callable[[T], T]) -> Optional[T]:
        item = self.get_by_id(item_id)
        if item is None:
            return None
        return update_callback(item)

    def delete(self, item_id: str) -> bool:
        item = self.get_by_id(item_id)
        if item is None:
            return False
        self.items.remove(item)
        return True

    def count(self) -> int:
        return len(self.items)
