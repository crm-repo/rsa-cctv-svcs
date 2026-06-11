from datetime import datetime, timezone
from typing import Optional

from app.models.brand import Brand, BrandListResponse
from app.repositories.repository_factory import create_brand_repository

now = datetime.now(timezone.utc)

MOCK_BRANDS: list[Brand] = [
    Brand(
        brand_id="BRND-0000001",
        show_flag="Y",
        display_seq=10,
        brand_name="Hikvision",
        brand_key="hikvision",
        brand_logo_path="assets/images/brands/hikvision-logo.png",
        description="Video surveillance cameras, DVR/NVR recorders, and security solutions.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Brand(
        brand_id="BRND-0000002",
        show_flag="Y",
        display_seq=20,
        brand_name="Dahua",
        brand_key="dahua",
        brand_logo_path="assets/images/brands/dahua-logo.png",
        description="CCTV cameras, recorders, and security equipment for residential and commercial use.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Brand(
        brand_id="BRND-0000003",
        show_flag="Y",
        display_seq=30,
        brand_name="HiLook",
        brand_key="hilook",
        brand_logo_path="assets/images/brands/hilook-logo.png",
        description="Practical and affordable CCTV solutions for homes and small businesses.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
    Brand(
        brand_id="BRND-0000004",
        show_flag="Y",
        display_seq=40,
        brand_name="TP-Link",
        brand_key="tp-link",
        brand_logo_path="assets/images/brands/tp-link-logo.png",
        description="Networking and surveillance accessories for connected CCTV installations.",
        created_at=now,
        updated_at=now,
        created_by="system",
        updated_by="system",
    ),
]


def _get_brand_repository():
    return create_brand_repository(initial_items=MOCK_BRANDS)


def list_public_brands(search: Optional[str] = None) -> BrandListResponse:
    brands = _get_brand_repository().list_visible()

    if search:
        search_value = search.strip().lower()
        brands = [
            brand
            for brand in brands
            if search_value in brand.brand_name.lower()
            or search_value in brand.brand_key.lower()
            or (brand.description and search_value in brand.description.lower())
        ]

    brands.sort(key=lambda brand: brand.display_seq)
    return BrandListResponse(items=brands, total=len(brands))


def get_public_brand_by_id(brand_id: str) -> Optional[Brand]:
    return _get_brand_repository().get_visible_by_id(brand_id)


def get_public_brand_by_key(brand_key: str) -> Optional[Brand]:
    return _get_brand_repository().get_visible_by_key(brand_key)
