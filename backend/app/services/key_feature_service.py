from datetime import datetime, timezone
from typing import Optional

from app.models.key_feature import KeyFeature, KeyFeatureListResponse


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


def list_key_features(search: Optional[str] = None) -> KeyFeatureListResponse:
    features = list(MOCK_KEY_FEATURES)

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
    for feature in MOCK_KEY_FEATURES:
        if feature.key_feat_id == key_feat_id:
            return feature
    return None
