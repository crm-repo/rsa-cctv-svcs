from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KeyFeature(BaseModel):
    key_feat_id: str
    key_feat_name: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class KeyFeatureListResponse(BaseModel):
    items: list[KeyFeature]
    total: int
