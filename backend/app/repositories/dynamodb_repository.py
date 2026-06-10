"""Reusable DynamoDB repository helpers for RSA CMS / Mini-CRM.

Batch 7 implements a small, generic DynamoDB repository boundary, but the
application still uses mock/in-memory repositories by default. These helpers are
for later controlled repository switching after AWS table creation and seed-data
checks.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from app.database import get_dynamodb_table


class DynamoDBRepositoryError(RuntimeError):
    """Raised when a DynamoDB repository operation cannot be completed."""


def _to_dynamodb_value(value: Any) -> Any:
    """Convert Python/Pydantic values to DynamoDB-friendly values."""

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        # DynamoDB does not accept Python float. Use Decimal from string to avoid
        # binary floating-point artifacts.
        return Decimal(str(value))

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: converted
            for key, inner_value in value.items()
            if (converted := _to_dynamodb_value(inner_value)) is not None
        }

    if isinstance(value, list):
        return [converted for item in value if (converted := _to_dynamodb_value(item)) is not None]

    return value


def to_dynamodb_item(item: Any) -> dict[str, Any]:
    """Convert a Pydantic model or mapping into a DynamoDB Item dictionary."""

    if hasattr(item, "model_dump"):
        raw_item = item.model_dump(mode="python")
    elif isinstance(item, dict):
        raw_item = item
    else:
        raise TypeError(f"Unsupported DynamoDB item type: {type(item)!r}")

    converted: dict[str, Any] = {}
    for key, value in raw_item.items():
        dynamodb_value = _to_dynamodb_value(value)
        if dynamodb_value is not None:
            converted[key] = dynamodb_value

    return converted


class DynamoDBRepository:
    """Small generic DynamoDB repository.

    This class is intentionally table-shape agnostic. Specific repositories can
    compose it later when RSA_DATA_BACKEND=dynamodb is enabled.
    """

    def __init__(self, table_name: str, id_field: str, region_name: Optional[str] = None):
        self.table_name = table_name
        self.id_field = id_field
        self.region_name = region_name
        self._table: Optional[Any] = None

    @property
    def table(self) -> Any:
        if self._table is None:
            self._table = get_dynamodb_table(self.table_name, region_name=self.region_name)
        return self._table

    def get_by_id(self, item_id: str) -> Optional[dict[str, Any]]:
        response = self.table.get_item(Key={self.id_field: item_id})
        return response.get("Item")

    def put_item(self, item: Any) -> dict[str, Any]:
        dynamodb_item = to_dynamodb_item(item)

        if self.id_field not in dynamodb_item or dynamodb_item[self.id_field] in (None, ""):
            raise DynamoDBRepositoryError(
                f"Cannot put item into {self.table_name}; missing primary key field '{self.id_field}'."
            )

        self.table.put_item(Item=dynamodb_item)
        return dynamodb_item

    def update_item(self, item_id: str, update_data: dict[str, Any]) -> Optional[dict[str, Any]]:
        cleaned_update_data = {
            key: _to_dynamodb_value(value)
            for key, value in update_data.items()
            if key != self.id_field and value is not None
        }

        if not cleaned_update_data:
            return self.get_by_id(item_id)

        expression_attribute_names = {f"#{key}": key for key in cleaned_update_data.keys()}
        expression_attribute_values = {f":{key}": value for key, value in cleaned_update_data.items()}
        update_expression = "SET " + ", ".join(
            f"#{key} = :{key}" for key in cleaned_update_data.keys()
        )

        response = self.table.update_item(
            Key={self.id_field: item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes")

    def delete_by_id(self, item_id: str) -> None:
        self.table.delete_item(Key={self.id_field: item_id})

    def list_all(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        scan_kwargs: dict[str, Any] = {}
        if limit is not None:
            scan_kwargs["Limit"] = limit

        while True:
            response = self.table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            if limit is not None and len(items) >= limit:
                return items[:limit]

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                return items

            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

    def query_index(
        self,
        index_name: str,
        key_name: str,
        key_value: Any,
        limit: Optional[int] = None,
        scan_index_forward: bool = False,
    ) -> list[dict[str, Any]]:
        try:
            from boto3.dynamodb.conditions import Key  # type: ignore
        except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
            raise RuntimeError("boto3 is required for DynamoDB query helpers.") from exc

        query_kwargs: dict[str, Any] = {
            "IndexName": index_name,
            "KeyConditionExpression": Key(key_name).eq(key_value),
            "ScanIndexForward": scan_index_forward,
        }
        if limit is not None:
            query_kwargs["Limit"] = limit

        response = self.table.query(**query_kwargs)
        return response.get("Items", [])
