"""Database helpers for RSA CMS / Mini-CRM.

Batch 4 keeps local APIs mock/in-memory, but prepares the backend for
DynamoDB wiring. Nothing in this file creates AWS resources or requires
AWS credentials during local testing unless a caller explicitly asks for a
DynamoDB resource/table.
"""

from dataclasses import dataclass
import os
from typing import Any, Optional


DEFAULT_AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")


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


def get_aws_region() -> str:
    return os.getenv("AWS_REGION", DEFAULT_AWS_REGION)


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


def get_dynamodb_table(table_name: str, region_name: Optional[str] = None) -> Any:
    """Return a DynamoDB table handle.

    This does not create the table. It only prepares a table object for future
    reads/writes after DynamoDB resources are created.
    """

    return get_dynamodb_resource(region_name=region_name).Table(table_name)
