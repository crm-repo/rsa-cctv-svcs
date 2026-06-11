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



# --- Batch 20 admin CRUD helpers ---
import re
from typing import Any

from app.services.id_service import (
    generate_brand_id,
    generate_category_id,
    generate_key_feature_id,
    generate_product_id_for_category,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _request_update_data(request: Any) -> dict[str, Any]:
    return request.model_dump(exclude_unset=True)



def list_admin_brands(search: Optional[str] = None) -> BrandListResponse:
    brands = _get_brand_repository().list_all()
    if search:
        search_value = search.strip().lower()
        brands = [
            brand
            for brand in brands
            if search_value in brand.brand_name.lower()
            or search_value in brand.brand_key.lower()
            or (brand.description and search_value in brand.description.lower())
        ]
    brands.sort(key=lambda brand: (brand.display_seq, brand.brand_name.lower()))
    return BrandListResponse(items=brands, total=len(brands))


def get_admin_brand_by_id(brand_id: str) -> Optional[Brand]:
    return _get_brand_repository().get_by_id(brand_id)


def get_admin_brand_by_key(brand_key: str) -> Optional[Brand]:
    repository = _get_brand_repository()
    if hasattr(repository, "get_by_key"):
        return repository.get_by_key(brand_key)
    key = brand_key.strip().lower()
    for brand in repository.list_all():
        if brand.brand_key.lower() == key:
            return brand
    return None


def _next_unique_brand_id(repository) -> str:
    for _ in range(100):
        candidate = generate_brand_id()
        if repository.get_by_id(candidate) is None:
            return candidate
    raise ValueError("Unable to generate a unique brand ID.")


def create_admin_brand(request) -> Brand:
    repository = _get_brand_repository()
    data = request.model_dump()
    now = _now_utc()
    brand_name = _clean_text(data.get("brand_name"))
    if not brand_name:
        raise ValueError("Brand name is required.")
    brand_key = _clean_text(data.get("brand_key")) or _slugify(brand_name)
    brand = Brand(
        brand_id=_next_unique_brand_id(repository),
        show_flag=data.get("show_flag") or "Y",
        display_seq=int(data.get("display_seq") or 0),
        brand_name=brand_name,
        brand_key=brand_key,
        brand_logo_path=_clean_text(data.get("brand_logo_path")),
        description=_clean_text(data.get("description")),
        meta_title=_clean_text(data.get("meta_title")) or brand_name,
        meta_description=_clean_text(data.get("meta_description")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_brand(brand)


def update_admin_brand(brand_id: str, request) -> Optional[Brand]:
    repository = _get_brand_repository()
    existing = repository.get_by_id(brand_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = _request_update_data(request)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = value
    if data.get("brand_name") and not data.get("brand_key"):
        data["brand_key"] = _slugify(data["brand_name"])
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    brand = Brand.model_validate(data)
    return repository.save_brand(brand)
