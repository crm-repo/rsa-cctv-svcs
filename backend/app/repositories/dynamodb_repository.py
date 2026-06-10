"""DynamoDB repository placeholders.

These classes are intentionally lightweight in Batch 4. They document the
future DynamoDB boundary while keeping current local APIs in memory. Later
batches can implement these methods with boto3 after table creation and AWS
cost/config review.
"""

from typing import Any, Optional

from app.database import get_dynamodb_table


class DynamoDBRepository:
    def __init__(self, table_name: str, id_field: str):
        self.table_name = table_name
        self.id_field = id_field
        self._table: Optional[Any] = None

    @property
    def table(self) -> Any:
        if self._table is None:
            self._table = get_dynamodb_table(self.table_name)
        return self._table

    def get_by_id(self, item_id: str) -> Any:
        raise NotImplementedError("DynamoDB access will be implemented after table/config review.")

    def put_item(self, item: Any) -> Any:
        raise NotImplementedError("DynamoDB access will be implemented after table/config review.")

    def update_item(self, item_id: str, update_data: dict[str, Any]) -> Any:
        raise NotImplementedError("DynamoDB access will be implemented after table/config review.")
