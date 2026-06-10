from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.key_feature import KeyFeature, KeyFeatureListResponse
from app.services.key_feature_service import get_key_feature_by_id, list_key_features

router = APIRouter()


@router.get("/key-features", response_model=KeyFeatureListResponse)
def get_key_features(search: Optional[str] = Query(default=None)):
    return list_key_features(search=search)


@router.get("/key-features/{key_feat_id}", response_model=KeyFeature)
def get_key_feature(key_feat_id: str):
    key_feature = get_key_feature_by_id(key_feat_id)

    if key_feature is None:
        raise HTTPException(status_code=404, detail="Key feature not found")

    return key_feature
