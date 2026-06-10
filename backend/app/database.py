"""Database helpers for RSA CMS / Mini-CRM.

Batch 8 keeps the application on mock/in-memory repositories by default, while
adding an explicit repository mode switch for later DynamoDB testing.

Important:
- Importing this file does not create AWS resources.
- Local API testing does not require AWS credentials.
- DynamoDB table creation still happens only from scripts with explicit flags.
- Repository mode defaults to ``mock`` until you intentionally set
  RSA_REPOSITORY_MODE=dynamodb after tables, seed data, and AWS credentials
  are ready. RSA_DATA_BACKEND/DATA_BACKEND remain backward-compatible aliases.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Optional


DEFAULT_AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
DEFAULT_READ_CAPACITY_UNITS = int(os.getenv("DYNAMODB_DEFAULT_RCU", "1"))
DEFAULT_WRITE_CAPACITY_UNITS = int(os.getenv("DYNAMODB_DEFAULT_WCU", "1"))
DEFAULT_REPOSITORY_MODE = "mock"
VALID_REPOSITORY_MODES = {"mock", "dynamodb"}

# Backward-compatible names retained from Batch 7.
DEFAULT_DATA_BACKEND = DEFAULT_REPOSITORY_MODE
VALID_DATA_BACKENDS = VALID_REPOSITORY_MODES


@dataclass(frozen=True)
class DynamoDBTableNames:
    products: str = os.getenv("DYNAMODB_PRODUCTS_TABLE", "rsa_products")
    brands: str = os.getenv("DYNAMODB_BRANDS_TABLE", "rsa_brands")
    categories: str = os.getenv("DYNAMODB_CATEGORIES_TABLE", "rsa_categories")
    key_features: str = os.getenv("DYNAMODB_KEY_FEATURES_TABLE", "rsa_key_features")
    customers: str = os.getenv("DYNAMODB_CUSTOMERS_TABLE", "rsa_customers")
    bookings: str = os.getenv("DYNAMODB_BOOKINGS_TABLE", "rsa_bookings")
    inquiries: str = os.getenv("DYNAMODB_INQUIRIES_TABLE", "rsa_inquiries")
    about: str = os.getenv("DYNAMODB_ABOUT_TABLE", "rsa_about")
    project_gallery: str = os.getenv("DYNAMODB_PROJECT_GALLERY_TABLE", "rsa_project_gallery")
    services: str = os.getenv("DYNAMODB_SERVICES_TABLE", "rsa_services")
    contact_us: str = os.getenv("DYNAMODB_CONTACT_US_TABLE", "rsa_contact_us")
    id_counters: str = os.getenv("DYNAMODB_ID_COUNTERS_TABLE", "rsa_id_counters")


TABLE_NAMES = DynamoDBTableNames()

# Logical table keys used by scripts and future repositories.
DYNAMODB_TABLE_NAME_MAP: dict[str, str] = {
    "products": TABLE_NAMES.products,
    "brands": TABLE_NAMES.brands,
    "categories": TABLE_NAMES.categories,
    "key_features": TABLE_NAMES.key_features,
    "customers": TABLE_NAMES.customers,
    "bookings": TABLE_NAMES.bookings,
    "inquiries": TABLE_NAMES.inquiries,
    "about": TABLE_NAMES.about,
    "project_gallery": TABLE_NAMES.project_gallery,
    "services": TABLE_NAMES.services,
    "contact_us": TABLE_NAMES.contact_us,
    "id_counters": TABLE_NAMES.id_counters,
}

# Phase 8 Final v5 approved key/index configuration.
# Attribute types: S = String, N = Number.
DYNAMODB_TABLE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "products": {
        "table_name": TABLE_NAMES.products,
        "hash_key": ("product_id", "S"),
        "gsis": [
            {
                "index_name": "category_key-display_seq-index",
                "hash_key": ("category_key", "S"),
                "range_key": ("display_seq", "N"),
            },
            {
                "index_name": "product_brand_key-display_seq-index",
                "hash_key": ("product_brand_key", "S"),
                "range_key": ("display_seq", "N"),
            },
        ],
    },
    "brands": {
        "table_name": TABLE_NAMES.brands,
        "hash_key": ("brand_id", "S"),
        "gsis": [],
    },
    "categories": {
        "table_name": TABLE_NAMES.categories,
        "hash_key": ("category_id", "S"),
        "gsis": [],
    },
    "key_features": {
        "table_name": TABLE_NAMES.key_features,
        "hash_key": ("key_feat_id", "S"),
        "gsis": [],
    },
    "customers": {
        "table_name": TABLE_NAMES.customers,
        "hash_key": ("customer_id", "S"),
        "gsis": [
            {
                "index_name": "contact_number_normalized-index",
                "hash_key": ("contact_number_normalized", "S"),
            },
        ],
    },
    "bookings": {
        "table_name": TABLE_NAMES.bookings,
        "hash_key": ("booking_id", "S"),
        "gsis": [
            {
                "index_name": "status-created_at-index",
                "hash_key": ("status", "S"),
                "range_key": ("created_at", "S"),
            },
        ],
    },
    "inquiries": {
        "table_name": TABLE_NAMES.inquiries,
        "hash_key": ("inquiry_id", "S"),
        "gsis": [
            {
                "index_name": "status-created_at-index",
                "hash_key": ("status", "S"),
                "range_key": ("created_at", "S"),
            },
        ],
    },
    "about": {
        "table_name": TABLE_NAMES.about,
        "hash_key": ("about_id", "S"),
        "gsis": [],
    },
    "project_gallery": {
        "table_name": TABLE_NAMES.project_gallery,
        "hash_key": ("project_id", "S"),
        "gsis": [],
    },
    "services": {
        "table_name": TABLE_NAMES.services,
        "hash_key": ("service_id", "S"),
        "gsis": [],
    },
    "contact_us": {
        "table_name": TABLE_NAMES.contact_us,
        "hash_key": ("contact_us_id", "S"),
        "gsis": [],
    },
    "id_counters": {
        "table_name": TABLE_NAMES.id_counters,
        "hash_key": ("id_prefix", "S"),
        "gsis": [],
    },
}


def get_aws_region() -> str:
    return os.getenv("AWS_REGION", DEFAULT_AWS_REGION)


def get_default_read_capacity_units() -> int:
    return int(os.getenv("DYNAMODB_DEFAULT_RCU", str(DEFAULT_READ_CAPACITY_UNITS)))


def get_default_write_capacity_units() -> int:
    return int(os.getenv("DYNAMODB_DEFAULT_WCU", str(DEFAULT_WRITE_CAPACITY_UNITS)))


def _read_repository_mode_from_env() -> tuple[str, str]:
    """Return repository mode and the environment variable that supplied it.

    RSA_REPOSITORY_MODE is the Phase 8 Batch 8 preferred name. The older
    RSA_DATA_BACKEND and DATA_BACKEND aliases remain supported so previous
    local scripts do not break.
    """

    for env_name in ("RSA_REPOSITORY_MODE", "RSA_DATA_BACKEND", "DATA_BACKEND"):
        raw_value = os.getenv(env_name)
        if raw_value is not None and raw_value.strip() != "":
            return raw_value.strip().lower(), env_name

    return DEFAULT_REPOSITORY_MODE, "default"


def get_repository_mode() -> str:
    """Return current repository mode.

    Accepted values are:
    - mock: default local/in-memory behavior
    - dynamodb: AWS DynamoDB-backed repository behavior

    Keep this as ``mock`` until DynamoDB tables are created, seed data is
    loaded, and read/write smoke tests pass.
    """

    repository_mode, _source = _read_repository_mode_from_env()
    if repository_mode not in VALID_REPOSITORY_MODES:
        valid = ", ".join(sorted(VALID_REPOSITORY_MODES))
        raise ValueError(f"Invalid repository mode '{repository_mode}'. Valid values: {valid}")
    return repository_mode


def get_repository_mode_source() -> str:
    _repository_mode, source = _read_repository_mode_from_env()
    return source


def get_data_backend() -> str:
    """Backward-compatible alias for Batch 7 scripts."""

    return get_repository_mode()


def is_dynamodb_repository_mode_enabled() -> bool:
    return get_repository_mode() == "dynamodb"


def is_dynamodb_backend_enabled() -> bool:
    """Backward-compatible alias for Batch 7 scripts."""

    return is_dynamodb_repository_mode_enabled()


def get_repository_mode_summary() -> dict[str, Any]:
    repository_mode = get_repository_mode()
    return {
        "repository_mode": repository_mode,
        "repository_mode_source": get_repository_mode_source(),
        "data_backend": repository_mode,
        "is_dynamodb_repository_mode_enabled": is_dynamodb_repository_mode_enabled(),
        "is_dynamodb_backend_enabled": is_dynamodb_backend_enabled(),
        "aws_region": get_aws_region(),
        "table_prefix": "rsa_",
        "table_count": len(DYNAMODB_TABLE_NAME_MAP),
        "table_names": DYNAMODB_TABLE_NAME_MAP.copy(),
        "safety_note": "mock is the safe default; use dynamodb only after AWS tables and seed data are ready.",
    }


def get_table_name(logical_name: str) -> str:
    try:
        return DYNAMODB_TABLE_NAME_MAP[logical_name]
    except KeyError as exc:
        valid = ", ".join(sorted(DYNAMODB_TABLE_NAME_MAP.keys()))
        raise KeyError(f"Unknown DynamoDB logical table name '{logical_name}'. Valid names: {valid}") from exc


def get_table_definition(logical_name: str) -> dict[str, Any]:
    try:
        return DYNAMODB_TABLE_DEFINITIONS[logical_name]
    except KeyError as exc:
        valid = ", ".join(sorted(DYNAMODB_TABLE_DEFINITIONS.keys()))
        raise KeyError(f"Unknown DynamoDB table definition '{logical_name}'. Valid names: {valid}") from exc


def list_table_definitions() -> dict[str, dict[str, Any]]:
    return DYNAMODB_TABLE_DEFINITIONS.copy()


def get_dynamodb_resource(region_name: Optional[str] = None, endpoint_url: Optional[str] = None) -> Any:
    """Return a boto3 DynamoDB resource lazily.

    This helper only prepares a resource handle. It does not create tables,
    read data, or write data by itself.
    """

    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
        raise RuntimeError("boto3 is required for DynamoDB access. Install backend requirements first.") from exc

    resolved_endpoint_url = endpoint_url or os.getenv("DYNAMODB_ENDPOINT_URL") or None
    return boto3.resource(
        "dynamodb",
        region_name=region_name or get_aws_region(),
        endpoint_url=resolved_endpoint_url,
    )


def get_dynamodb_client(region_name: Optional[str] = None, endpoint_url: Optional[str] = None) -> Any:
    """Return a boto3 DynamoDB client lazily."""

    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
        raise RuntimeError("boto3 is required for DynamoDB access. Install backend requirements first.") from exc

    resolved_endpoint_url = endpoint_url or os.getenv("DYNAMODB_ENDPOINT_URL") or None
    return boto3.client(
        "dynamodb",
        region_name=region_name or get_aws_region(),
        endpoint_url=resolved_endpoint_url,
    )


def get_aws_sts_client(region_name: Optional[str] = None) -> Any:
    """Return a boto3 STS client lazily for read-only credential checks."""

    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
        raise RuntimeError("boto3 is required for AWS access. Install backend requirements first.") from exc

    return boto3.client("sts", region_name=region_name or get_aws_region())


def get_dynamodb_table(table_name: str, region_name: Optional[str] = None, endpoint_url: Optional[str] = None) -> Any:
    """Return a DynamoDB table handle.

    This does not create the table. It only prepares a table object for future
    reads/writes after DynamoDB resources are created.
    """

    return get_dynamodb_resource(region_name=region_name, endpoint_url=endpoint_url).Table(table_name)


def get_dynamodb_table_by_logical_name(logical_name: str, region_name: Optional[str] = None) -> Any:
    return get_dynamodb_table(get_table_name(logical_name), region_name=region_name)
