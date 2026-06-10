"""Database helpers for RSA CMS / Mini-CRM.

Batch 5 keeps all local APIs mock/in-memory, but adds safe DynamoDB table
configuration helpers for review and setup scripts.

Important:
- Importing this file does not create AWS resources.
- Local API testing does not require AWS credentials.
- DynamoDB resources are created only when an explicit script is run with
  an execute flag.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Optional


DEFAULT_AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
DEFAULT_READ_CAPACITY_UNITS = int(os.getenv("DYNAMODB_DEFAULT_RCU", "1"))
DEFAULT_WRITE_CAPACITY_UNITS = int(os.getenv("DYNAMODB_DEFAULT_WCU", "1"))


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


def get_dynamodb_resource(region_name: Optional[str] = None) -> Any:
    """Return a boto3 DynamoDB resource lazily.

    This is intentionally not called by the current mock APIs. It is here so
    the repository layer can switch to DynamoDB in a later batch without
    changing route/service code.
    """

    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
        raise RuntimeError("boto3 is required for DynamoDB access. Install backend requirements first.") from exc

    return boto3.resource("dynamodb", region_name=region_name or get_aws_region())


def get_dynamodb_client(region_name: Optional[str] = None) -> Any:
    """Return a boto3 DynamoDB client lazily."""

    try:
        import boto3  # type: ignore
    except ImportError as exc:  # pragma: no cover - only relevant if dependency missing
        raise RuntimeError("boto3 is required for DynamoDB access. Install backend requirements first.") from exc

    return boto3.client("dynamodb", region_name=region_name or get_aws_region())


def get_dynamodb_table(table_name: str, region_name: Optional[str] = None) -> Any:
    """Return a DynamoDB table handle.

    This does not create the table. It only prepares a table object for future
    reads/writes after DynamoDB resources are created.
    """

    return get_dynamodb_resource(region_name=region_name).Table(table_name)
