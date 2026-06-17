from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.key_feature import (
    KeyFeature,
    KeyFeatureAdminCreateRequest,
    KeyFeatureAdminUpdateRequest,
    KeyFeatureListResponse,
)
from app.services.key_feature_service import (
    create_admin_key_feature,
    get_key_feature_by_id,
    list_key_features,
    update_admin_key_feature,
)

router = APIRouter()


@router.get("/admin/key-features", response_model=KeyFeatureListResponse)
def get_admin_key_features(search: Optional[str] = Query(default=None)):
    return list_key_features(search=search)


@router.post("/admin/key-features", response_model=KeyFeature, status_code=status.HTTP_201_CREATED)
def create_key_feature_admin(request: KeyFeatureAdminCreateRequest):
    try:
        return create_admin_key_feature(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/key-features/{key_feat_id}", response_model=KeyFeature)
def get_admin_key_feature(key_feat_id: str):
    key_feature = get_key_feature_by_id(key_feat_id)
    if key_feature is None:
        raise HTTPException(status_code=404, detail="Key feature not found")
    return key_feature


@router.put("/admin/key-features/{key_feat_id}", response_model=KeyFeature)
def update_key_feature_admin(key_feat_id: str, request: KeyFeatureAdminUpdateRequest):
    try:
        key_feature = update_admin_key_feature(key_feat_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if key_feature is None:
        raise HTTPException(status_code=404, detail="Key feature not found")
    return key_feature


@router.get("/key-features", response_model=KeyFeatureListResponse)
def get_key_features(search: Optional[str] = Query(default=None)):
    return list_key_features(search=search)


@router.get("/key-features/{key_feat_id}", response_model=KeyFeature)
def get_key_feature(key_feat_id: str):
    key_feature = get_key_feature_by_id(key_feat_id)

    if key_feature is None:
        raise HTTPException(status_code=404, detail="Key feature not found")

    return key_feature

# --- batch59b-full-admin-delete-actions ---
from fastapi import Depends as _Batch59BDepends, Response as _Batch59BResponse
from app.auth.admin_auth import require_admin_group as _batch59b_require_admin_group


@router.delete("/admin/key-features/{key_feat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_key_feature_admin_59b(key_feat_id: str, _admin=_Batch59BDepends(_batch59b_require_admin_group)):
    from app.services.key_feature_service import delete_admin_key_feature
    try:
        deleted = delete_admin_key_feature(key_feat_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Key feature not found")
    return _Batch59BResponse(status_code=status.HTTP_204_NO_CONTENT)
