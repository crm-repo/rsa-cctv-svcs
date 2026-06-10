from typing import Optional

from app.models.service import Service
from app.repositories.base_repository import InMemoryRepository


class ServiceRepository(InMemoryRepository[Service]):
    def __init__(self, initial_items: Optional[list[Service]] = None):
        super().__init__(id_field="service_id", initial_items=initial_items)

    def list_visible_sorted(self) -> list[Service]:
        services = self.list_where(lambda service: service.show_flag == "Y")
        services.sort(key=lambda service: service.display_seq)
        return services

    def get_visible_by_slug(self, service_slug: str) -> Optional[Service]:
        slug = service_slug.strip().lower()
        for service in self.items:
            if service.show_flag == "Y" and service.service_slug.lower() == slug:
                return service
        return None
