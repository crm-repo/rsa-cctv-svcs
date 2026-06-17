from datetime import datetime, timezone
from typing import Optional

from app.models.key_feature import KeyFeature, KeyFeatureListResponse
from app.repositories.repository_factory import create_key_feature_repository


MOCK_KEY_FEATURES: list[KeyFeature] = [
    KeyFeature(
        key_feat_id="KFEA-0000001",
        key_feat_name="6 MP AcuSense",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000002",
        key_feat_name="Smart IR Night Vision",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000003",
        key_feat_name="Weatherproof Outdoor Housing",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000004",
        key_feat_name="4K Ultra HD Recording",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000005",
        key_feat_name="Remote Mobile Viewing",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000006",
        key_feat_name="Motion Detection Alerts",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000007",
        key_feat_name="Installation Included",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    KeyFeature(
        key_feat_id="KFEA-0000008",
        key_feat_name="Warranty Included",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
]


def _get_key_feature_repository():
    return create_key_feature_repository(initial_items=MOCK_KEY_FEATURES)


def list_key_features(search: Optional[str] = None) -> KeyFeatureListResponse:
    repository = _get_key_feature_repository()
    if search:
        features = repository.search_by_name(search)
    else:
        features = repository.list_all()

    if search:
        search_value = search.strip().lower()
        features = [
            feature
            for feature in features
            if search_value in feature.key_feat_name.lower()
            or search_value in feature.key_feat_id.lower()
        ]

    features.sort(key=lambda feature: feature.key_feat_name.lower())
    return KeyFeatureListResponse(items=features, total=len(features))


def get_key_feature_by_id(key_feat_id: str) -> Optional[KeyFeature]:
    return _get_key_feature_repository().get_by_id(key_feat_id)



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



def _next_unique_key_feature_id(repository) -> str:
    for _ in range(100):
        candidate = generate_key_feature_id()
        if repository.get_by_id(candidate) is None:
            return candidate
    raise ValueError("Unable to generate a unique key feature ID.")


def create_admin_key_feature(request) -> KeyFeature:
    repository = _get_key_feature_repository()
    data = request.model_dump()
    name = _clean_text(data.get("key_feat_name"))
    if not name:
        raise ValueError("Key feature name is required.")
    now = _now_utc()
    feature = KeyFeature(
        key_feat_id=_next_unique_key_feature_id(repository),
        key_feat_name=name,
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_key_feature(feature)


def update_admin_key_feature(key_feat_id: str, request) -> Optional[KeyFeature]:
    repository = _get_key_feature_repository()
    existing = repository.get_by_id(key_feat_id)
    if existing is None:
        return None
    data = existing.model_dump(mode="python")
    update_data = _request_update_data(request)
    if "key_feat_name" in update_data:
        data["key_feat_name"] = _clean_text(update_data.get("key_feat_name")) or data["key_feat_name"]
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"
    feature = KeyFeature.model_validate(data)
    return repository.save_key_feature(feature)

# --- batch59b-full-admin-delete-actions ---
def delete_admin_key_feature(key_feat_id: str) -> bool:
    repository = _get_key_feature_repository()
    existing = repository.get_by_id(key_feat_id)
    if existing is None:
        return False

    from app.repositories.repository_factory import create_product_repository

    feature_name = str(getattr(existing, "key_feat_name", "") or "").strip().lower()
    if feature_name:
        for product in create_product_repository().list_all():
            for index in range(1, 11):
                product_feature = str(getattr(product, f"feature_{index:02d}", "") or "").strip().lower()
                if product_feature and product_feature == feature_name:
                    raise ValueError("Key feature cannot be deleted because one or more products use it.")

    if not hasattr(repository, "delete_key_feature"):
        raise ValueError("Key feature repository delete support is unavailable.")
    return bool(repository.delete_key_feature(key_feat_id))
