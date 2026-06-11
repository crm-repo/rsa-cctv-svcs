from typing import Optional

from app.database import get_table_name
from app.models.service import Service
from app.repositories.base_repository import InMemoryRepository
from app.repositories.dynamodb_repository import DynamoDBRepository


class ServiceRepository(InMemoryRepository[Service]):
    repository_mode = "mock"
    table_name = "mock_services"

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

    def save_service(self, service: Service) -> Service:
        return self.save(service)


class DynamoDBServiceRepository:
    repository_mode = "dynamodb"

    def __init__(self):
        self.table_name = get_table_name("services")
        self._repository = DynamoDBRepository(self.table_name, id_field="service_id")

    @staticmethod
    def _to_model(item: dict) -> Service:
        return Service.model_validate(item)

    def list_all(self) -> list[Service]:
        return [self._to_model(item) for item in self._repository.list_all()]

    def get_by_id(self, service_id: str) -> Optional[Service]:
        item = self._repository.get_by_id(service_id)
        return self._to_model(item) if item is not None else None

    def list_visible_sorted(self) -> list[Service]:
        services = [service for service in self.list_all() if service.show_flag == "Y"]
        services.sort(key=lambda service: service.display_seq)
        return services

    def get_visible_by_slug(self, service_slug: str) -> Optional[Service]:
        slug = service_slug.strip().lower()
        for service in self.list_visible_sorted():
            if service.service_slug.lower() == slug:
                return service
        return None

    def save_service(self, service: Service) -> Service:
        self._repository.put_item(service)
        return service
