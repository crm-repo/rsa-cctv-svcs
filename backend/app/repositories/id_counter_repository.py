from datetime import datetime, timezone
from typing import Any

from app.database import TABLE_NAMES, get_repository_mode
from app.repositories.dynamodb_repository import DynamoDBRepository


# Temporary in-memory counter store for mock mode only.
MOCK_ID_COUNTERS: dict[str, dict[str, object]] = {}


class IdCounterRepository:
    """Mock ID counter repository.

    DynamoDB mode uses DynamoDBIdCounterRepository below with atomic increments.
    """

    def __init__(self, table_name: str = TABLE_NAMES.id_counters):
        self.table_name = table_name
        self.repository_mode = "mock"

    def get_next_number(self, id_prefix: str) -> int:
        normalized_prefix = id_prefix.strip().upper()
        now = datetime.now(timezone.utc)

        current_counter = MOCK_ID_COUNTERS.get(normalized_prefix)

        if current_counter is None:
            MOCK_ID_COUNTERS[normalized_prefix] = {
                "id_prefix": normalized_prefix,
                "last_number": 1,
                "updated_at": now,
            }
            return 1

        next_number = int(current_counter["last_number"]) + 1
        current_counter["last_number"] = next_number
        current_counter["updated_at"] = now

        return next_number

    def get_counter_snapshot(self) -> dict[str, dict[str, object]]:
        return {prefix: value.copy() for prefix, value in MOCK_ID_COUNTERS.items()}


class DynamoDBIdCounterRepository:
    """DynamoDB-backed ID counter repository with atomic increments.

    This is only used when RSA_REPOSITORY_MODE=dynamodb. It expects the
    rsa_id_counters table to already exist.
    """

    def __init__(self, table_name: str = TABLE_NAMES.id_counters):
        self.table_name = table_name
        self.repository_mode = "dynamodb"
        self.dynamodb = DynamoDBRepository(table_name=table_name, id_field="id_prefix")

    @property
    def table(self) -> Any:
        return self.dynamodb.table

    def get_next_number(self, id_prefix: str) -> int:
        normalized_prefix = id_prefix.strip().upper()
        now = datetime.now(timezone.utc).isoformat()

        response = self.table.update_item(
            Key={"id_prefix": normalized_prefix},
            UpdateExpression=(
                "SET last_number = if_not_exists(last_number, :zero) + :inc, "
                "updated_at = :updated_at"
            ),
            ExpressionAttributeValues={
                ":zero": 0,
                ":inc": 1,
                ":updated_at": now,
            },
            ReturnValues="UPDATED_NEW",
        )

        return int(response["Attributes"]["last_number"])

    def get_counter_snapshot(self) -> dict[str, dict[str, object]]:
        # Keep this intentionally lightweight. Full counter listing can be added
        # later if needed; ID generation only needs atomic get_next_number.
        return {}


def create_id_counter_repository() -> IdCounterRepository | DynamoDBIdCounterRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBIdCounterRepository()
    return IdCounterRepository()


id_counter_repository = create_id_counter_repository()


def get_next_number(id_prefix: str) -> int:
    """Backward-compatible wrapper used by id_service."""
    return id_counter_repository.get_next_number(id_prefix)


def get_counter_snapshot() -> dict[str, dict[str, object]]:
    """Return a copy of current counters for local debugging/tests."""
    return id_counter_repository.get_counter_snapshot()
