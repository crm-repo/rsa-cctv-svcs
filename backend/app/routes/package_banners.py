from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.package_banner import PackageBanner, PackageBannerListResponse
from app.services.package_banner_service import (
    get_public_package_banner_by_id,
    list_public_package_banners,
)

router = APIRouter()


@router.get("/package-banners", response_model=PackageBannerListResponse)
def get_package_banners(
    placement: Optional[Literal["homepage", "promotions"]] = Query(
        default=None,
        description="Accepted for backward compatibility. Phase 8 v5 uses show_pack_flag for both homepage and promotions placement.",
    ),
):
    return list_public_package_banners(placement=placement)


@router.get("/package-banners/{package_banner_id}", response_model=PackageBanner)
def get_package_banner(package_banner_id: str):
    package_banner = get_public_package_banner_by_id(package_banner_id)

    if package_banner is None:
        raise HTTPException(status_code=404, detail="Package banner not found")

    return package_banner
