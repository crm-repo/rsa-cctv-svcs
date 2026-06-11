"""Repository factory for RSA CMS / Mini-CRM.

Batch 15 extends the repository mode switch beyond CRM writes so public catalog
and CMS read APIs can also run against DynamoDB when explicitly enabled.

Supported modes:
- RSA_REPOSITORY_MODE=mock      local/in-memory repositories, default
- RSA_REPOSITORY_MODE=dynamodb  DynamoDB-backed repositories, only after AWS setup
"""

from __future__ import annotations

from typing import Any, Optional

from app.database import get_repository_mode, get_repository_mode_summary
from app.models.about import About
from app.models.brand import Brand
from app.models.category import Category
from app.models.contact_us import ContactUsRecord
from app.models.key_feature import KeyFeature
from app.models.product import Product
from app.models.project_gallery import ProjectGalleryItem
from app.models.service import Service
from app.repositories.about_repository import AboutRepository, DynamoDBAboutRepository
from app.repositories.booking_repository import BookingRepository, DynamoDBBookingRepository
from app.repositories.brand_repository import BrandRepository, DynamoDBBrandRepository
from app.repositories.category_repository import CategoryRepository, DynamoDBCategoryRepository
from app.repositories.contact_us_repository import ContactUsRepository, DynamoDBContactUsRepository
from app.repositories.customer_repository import CustomerRepository, DynamoDBCustomerRepository
from app.repositories.id_counter_repository import DynamoDBIdCounterRepository, IdCounterRepository
from app.repositories.inquiry_repository import DynamoDBInquiryRepository, InquiryRepository
from app.repositories.key_feature_repository import DynamoDBKeyFeatureRepository, KeyFeatureRepository
from app.repositories.product_repository import DynamoDBProductRepository, ProductRepository
from app.repositories.project_gallery_repository import DynamoDBProjectGalleryRepository, ProjectGalleryRepository
from app.repositories.service_repository import DynamoDBServiceRepository, ServiceRepository


def create_product_repository(initial_items: Optional[list[Product]] = None) -> ProductRepository | DynamoDBProductRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBProductRepository()
    return ProductRepository(initial_items=initial_items)


def create_brand_repository(initial_items: Optional[list[Brand]] = None) -> BrandRepository | DynamoDBBrandRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBBrandRepository()
    return BrandRepository(initial_items=initial_items)


def create_category_repository(initial_items: Optional[list[Category]] = None) -> CategoryRepository | DynamoDBCategoryRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBCategoryRepository()
    return CategoryRepository(initial_items=initial_items)


def create_key_feature_repository(initial_items: Optional[list[KeyFeature]] = None) -> KeyFeatureRepository | DynamoDBKeyFeatureRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBKeyFeatureRepository()
    return KeyFeatureRepository(initial_items=initial_items)


def create_about_repository(initial_items: Optional[list[About]] = None) -> AboutRepository | DynamoDBAboutRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBAboutRepository()
    return AboutRepository(initial_items=initial_items)


def create_project_gallery_repository(initial_items: Optional[list[ProjectGalleryItem]] = None) -> ProjectGalleryRepository | DynamoDBProjectGalleryRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBProjectGalleryRepository()
    return ProjectGalleryRepository(initial_items=initial_items)


def create_service_repository(initial_items: Optional[list[Service]] = None) -> ServiceRepository | DynamoDBServiceRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBServiceRepository()
    return ServiceRepository(initial_items=initial_items)


def create_contact_us_repository(initial_items: Optional[list[ContactUsRecord]] = None) -> ContactUsRepository | DynamoDBContactUsRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBContactUsRepository()
    return ContactUsRepository(initial_items=initial_items)


def create_customer_repository() -> CustomerRepository | DynamoDBCustomerRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBCustomerRepository()
    return CustomerRepository()


def create_booking_repository() -> BookingRepository | DynamoDBBookingRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBBookingRepository()
    return BookingRepository()


def create_inquiry_repository() -> InquiryRepository | DynamoDBInquiryRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBInquiryRepository()
    return InquiryRepository()


def create_id_counter_repository() -> IdCounterRepository | DynamoDBIdCounterRepository:
    if get_repository_mode() == "dynamodb":
        return DynamoDBIdCounterRepository()
    return IdCounterRepository()


def describe_repository(repository: Any) -> dict[str, str]:
    return {
        "class_name": repository.__class__.__name__,
        "repository_mode": getattr(repository, "repository_mode", get_repository_mode()),
        "table_name": getattr(repository, "table_name", ""),
    }


def get_crm_repository_summary() -> dict[str, Any]:
    """Return a safe local summary without making AWS calls."""

    customer_repository = create_customer_repository()
    booking_repository = create_booking_repository()
    inquiry_repository = create_inquiry_repository()

    return {
        "mode_summary": get_repository_mode_summary(),
        "repositories": {
            "customers": describe_repository(customer_repository),
            "bookings": describe_repository(booking_repository),
            "inquiries": describe_repository(inquiry_repository),
        },
        "aws_calls_made": False,
    }


def get_public_repository_summary() -> dict[str, Any]:
    """Return selected public read repository classes without reading AWS."""

    return {
        "mode_summary": get_repository_mode_summary(),
        "repositories": {
            "products": describe_repository(create_product_repository()),
            "brands": describe_repository(create_brand_repository()),
            "categories": describe_repository(create_category_repository()),
            "key_features": describe_repository(create_key_feature_repository()),
            "about": describe_repository(create_about_repository()),
            "project_gallery": describe_repository(create_project_gallery_repository()),
            "services": describe_repository(create_service_repository()),
            "contact_us": describe_repository(create_contact_us_repository()),
        },
        "aws_calls_made": False,
    }
