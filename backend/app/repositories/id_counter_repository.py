from datetime import datetime, timezone

from app.database import TABLE_NAMES


# Temporary in-memory counter store only.
# Later this will be replaced by DynamoDB atomic counter updates in rsa_id_counters.
MOCK_ID_COUNTERS: dict[str, dict[str, object]] = {}


class IdCounterRepository:
    """DynamoDB-ready ID counter repository interface.

    Current implementation uses memory only. Future implementation should use
    DynamoDB UpdateItem with an atomic increment on rsa_id_counters.
    """

    def __init__(self, table_name: str = TABLE_NAMES.id_counters):
        self.table_name = table_name

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


id_counter_repository = IdCounterRepository()


def get_next_number(id_prefix: str) -> int:
    """Backward-compatible wrapper used by id_service."""
    return id_counter_repository.get_next_number(id_prefix)


def get_counter_snapshot() -> dict[str, dict[str, object]]:
    """Return a copy of current in-memory counters for local debugging/tests."""
    return id_counter_repository.get_counter_snapshot()
