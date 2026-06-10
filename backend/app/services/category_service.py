from datetime import datetime, timezone
from typing import Optional

from app.models.category import Category, CategoryListResponse


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


def list_public_categories(search: Optional[str] = None) -> CategoryListResponse:
    categories = [category for category in MOCK_CATEGORIES if category.show_flag == "Y"]

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
    for category in MOCK_CATEGORIES:
        if category.category_id == category_id and category.show_flag == "Y":
            return category
    return None


def get_public_category_by_key(category_key: str) -> Optional[Category]:
    requested_key = category_key.strip().lower()
    for category in MOCK_CATEGORIES:
        if category.category_key.lower() == requested_key and category.show_flag == "Y":
            return category
    return None
