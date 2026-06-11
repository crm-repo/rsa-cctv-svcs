from datetime import datetime, timezone
from typing import Optional

from app.models.category import Category, CategoryListResponse
from app.repositories.repository_factory import create_category_repository


MOCK_CATEGORIES: list[Category] = [
    Category(
        category_id="CATG-0000001",
        show_flag="Y",
        display_seq=1,
        category_name="CCTV Cameras",
        category_key="cctv",
        category_prefix="CCTV",
        icon_code="fa-solid fa-video",
        description="CCTV camera products including dome, bullet, turret, and PTZ cameras.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000002",
        show_flag="Y",
        display_seq=2,
        category_name="Recorders",
        category_key="recorders",
        category_prefix="RECO",
        icon_code="fa-solid fa-hard-drive",
        description="NVR and DVR recorder products.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000003",
        show_flag="Y",
        display_seq=3,
        category_name="Packages/Kits",
        category_key="packages",
        category_prefix="PACK",
        icon_code="fa-solid fa-box",
        description="CCTV package and kit offers.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000004",
        show_flag="Y",
        display_seq=4,
        category_name="Networking",
        category_key="networking",
        category_prefix="NETW",
        icon_code="fa-solid fa-network-wired",
        description="Networking equipment for CCTV systems.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000005",
        show_flag="Y",
        display_seq=5,
        category_name="Accessories",
        category_key="accessories",
        category_prefix="ACCS",
        icon_code="fa-solid fa-screwdriver-wrench",
        description="CCTV accessories and installation items.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000006",
        show_flag="Y",
        display_seq=6,
        category_name="Power Supply",
        category_key="power",
        category_prefix="POWR",
        icon_code="fa-solid fa-plug",
        description="Power adapters, power supplies, and CCTV power accessories.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000007",
        show_flag="Y",
        display_seq=7,
        category_name="Storage",
        category_key="storage",
        category_prefix="STOR",
        icon_code="fa-solid fa-database",
        description="Storage drives and recording media.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Category(
        category_id="CATG-0000008",
        show_flag="N",
        display_seq=99,
        category_name="Hidden Test Category",
        category_key="hidden-test",
        category_prefix="HIDE",
        icon_code="fa-solid fa-eye-slash",
        description="Hidden category used to verify show_flag filtering.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
]


def _get_category_repository():
    return create_category_repository(initial_items=MOCK_CATEGORIES)


def list_public_categories(search: Optional[str] = None) -> CategoryListResponse:
    categories = _get_category_repository().list_visible()

    if search:
        search_value = search.strip().lower()
        categories = [
            category
            for category in categories
            if search_value in category.category_name.lower()
            or search_value in category.category_key.lower()
            or search_value in category.category_prefix.lower()
        ]

    categories.sort(key=lambda category: category.display_seq)
    return CategoryListResponse(items=categories, total=len(categories))


def get_public_category_by_id(category_id: str) -> Optional[Category]:
    return _get_category_repository().get_visible_by_id(category_id)


def get_public_category_by_key(category_key: str) -> Optional[Category]:
    return _get_category_repository().get_visible_by_key(category_key)



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



def list_admin_categories(search: Optional[str] = None) -> CategoryListResponse:
    categories = _get_category_repository().list_all()

    if search:
        search_value = search.strip().lower()
        categories = [
            category
            for category in categories
            if search_value in category.category_name.lower()
            or search_value in category.category_key.lower()
            or search_value in category.category_prefix.lower()
        ]

    categories.sort(key=lambda category: (category.display_seq, category.category_name.lower()))
    return CategoryListResponse(items=categories, total=len(categories))


def get_admin_category_by_id(category_id: str) -> Optional[Category]:
    return _get_category_repository().get_by_id(category_id)


def get_admin_category_by_key(category_key: str) -> Optional[Category]:
    repository = _get_category_repository()
    if hasattr(repository, "get_by_key"):
        return repository.get_by_key(category_key)
    key = category_key.strip().lower()
    for category in repository.list_all():
        if category.category_key.lower() == key:
            return category
    return None


def _next_unique_category_id(repository) -> str:
    for _ in range(100):
        candidate = generate_category_id()
        if repository.get_by_id(candidate) is None:
            return candidate
    raise ValueError("Unable to generate a unique category ID.")


def create_admin_category(request) -> Category:
    repository = _get_category_repository()
    data = request.model_dump()
    now = _now_utc()
    category_name = _clean_text(data.get("category_name"))
    if not category_name:
        raise ValueError("Category name is required.")
    category_key = _clean_text(data.get("category_key")) or _slugify(category_name)
    category_prefix = _clean_text(data.get("category_prefix"))
    if not category_prefix or len(category_prefix) != 4:
        raise ValueError("Category prefix must be 4 characters.")

    category = Category(
        category_id=_next_unique_category_id(repository),
        show_flag=data.get("show_flag") or "Y",
        display_seq=int(data.get("display_seq") or 0),
        category_name=category_name,
        category_key=category_key,
        category_prefix=category_prefix.upper(),
        icon_code=_clean_text(data.get("icon_code")),
        description=_clean_text(data.get("description")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_category(category)


def update_admin_category(category_id: str, request) -> Optional[Category]:
    repository = _get_category_repository()
    existing = repository.get_by_id(category_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = _request_update_data(request)
    for key, value in update_data.items():
        if key != "updated_by":
            data[key] = value
    if data.get("category_name") and not data.get("category_key"):
        data["category_key"] = _slugify(data["category_name"])
    if data.get("category_prefix"):
        data["category_prefix"] = str(data["category_prefix"]).upper()
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    category = Category.model_validate(data)
    return repository.save_category(category)
