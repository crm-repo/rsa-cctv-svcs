from typing import Literal, Optional

from app.models.package_banner import PackageBanner, PackageBannerListResponse


# Temporary mock data only.
# Later this will be replaced by DynamoDB.
MOCK_PACKAGE_BANNERS: list[PackageBanner] = [
    PackageBanner(
        package_banner_id="PKG-BANNER-001",
        show_flag="Y",
        display_order=1,
        product_id="PROD-003",
        banner_image_path="/assets/images/packages/dahua-4ch-package.jpg",
        homepage_visible="Y",
        promotions_hero_visible="Y",
    ),
    PackageBanner(
        package_banner_id="PKG-BANNER-002",
        show_flag="Y",
        display_order=2,
        product_id="PROD-007",
        banner_image_path="/assets/images/packages/hikvision-6ch-package.jpg",
        homepage_visible="Y",
        promotions_hero_visible="Y",
    ),
    PackageBanner(
        package_banner_id="PKG-BANNER-003",
        show_flag="Y",
        display_order=3,
        product_id="PROD-008",
        banner_image_path="/assets/images/packages/dahua-8ch-package.jpg",
        homepage_visible="Y",
        promotions_hero_visible="Y",
    ),
    PackageBanner(
        package_banner_id="PKG-BANNER-004",
        show_flag="Y",
        display_order=4,
        product_id="PROD-009",
        banner_image_path="/assets/images/packages/promo-extra-package.jpg",
        homepage_visible="N",
        promotions_hero_visible="Y",
    ),
    PackageBanner(
        package_banner_id="PKG-BANNER-005",
        show_flag="N",
        display_order=5,
        product_id="PROD-999",
        banner_image_path="/assets/images/packages/hidden-package.jpg",
        homepage_visible="Y",
        promotions_hero_visible="Y",
    ),
]


def list_public_package_banners(
    placement: Optional[Literal["homepage", "promotions"]] = None,
) -> PackageBannerListResponse:
    banners = [
        banner
        for banner in MOCK_PACKAGE_BANNERS
        if banner.show_flag == "Y"
    ]

    if placement == "homepage":
        banners = [
            banner
            for banner in banners
            if banner.homepage_visible == "Y"
        ]

    if placement == "promotions":
        banners = [
            banner
            for banner in banners
            if banner.promotions_hero_visible == "Y"
        ]

    banners.sort(key=lambda banner: banner.display_order)

    return PackageBannerListResponse(
        items=banners,
        total=len(banners),
    )


def get_public_package_banner_by_id(package_banner_id: str) -> Optional[PackageBanner]:
    for banner in MOCK_PACKAGE_BANNERS:
        if banner.package_banner_id == package_banner_id and banner.show_flag == "Y":
            return banner

    return None