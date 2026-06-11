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
