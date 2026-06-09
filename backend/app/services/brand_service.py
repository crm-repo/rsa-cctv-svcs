from typing import Optional

from app.models.brand import Brand, BrandListResponse


# Temporary mock data only.
# Later this will be replaced by DynamoDB.
MOCK_BRANDS: list[Brand] = [
    Brand(
        brand_id="BRAND-001",
        show_flag="Y",
        display_order=1,
        brand_name="Dahua",
        brand_key="dahua",
        logo_path="/assets/images/brands/dahua.png",
        description="Trusted CCTV and security product brand.",
        website_url="https://www.dahuasecurity.com",
        featured_brand="Y",
    ),
    Brand(
        brand_id="BRAND-002",
        show_flag="Y",
        display_order=2,
        brand_name="Hikvision",
        brand_key="hikvision",
        logo_path="/assets/images/brands/hikvision.png",
        description="CCTV cameras, recorders, and security solutions.",
        website_url="https://www.hikvision.com",
        featured_brand="Y",
    ),
    Brand(
        brand_id="BRAND-003",
        show_flag="Y",
        display_order=3,
        brand_name="D-Link",
        brand_key="d-link",
        logo_path="/assets/images/brands/dlink.png",
        description="Networking products used for CCTV and office network installations.",
        website_url="https://www.dlink.com",
        featured_brand="Y",
    ),
    Brand(
        brand_id="BRAND-004",
        show_flag="Y",
        display_order=4,
        brand_name="Uniview",
        brand_key="uniview",
        logo_path="/assets/images/brands/uniview.png",
        description="Video surveillance and IP security solutions.",
        website_url="https://www.uniview.com",
        featured_brand="Y",
    ),
    Brand(
        brand_id="BRAND-005",
        show_flag="Y",
        display_order=5,
        brand_name="EZVIZ",
        brand_key="ezviz",
        logo_path="/assets/images/brands/ezviz.png",
        description="Smart home cameras and security devices.",
        website_url="https://www.ezviz.com",
        featured_brand="Y",
    ),
    Brand(
        brand_id="BRAND-006",
        show_flag="N",
        display_order=6,
        brand_name="Hidden Test Brand",
        brand_key="hidden-test-brand",
        logo_path="/assets/images/brands/hidden.png",
        description="This brand should not appear in public API results.",
        website_url=None,
        featured_brand="N",
    ),
]


def list_public_brands(
    featured_only: Optional[bool] = None,
    search: Optional[str] = None,
) -> BrandListResponse:
    brands = [brand for brand in MOCK_BRANDS if brand.show_flag == "Y"]

    if featured_only is not None:
        if featured_only:
            brands = [brand for brand in brands if brand.featured_brand == "Y"]
        else:
            brands = [brand for brand in brands if brand.featured_brand == "N"]

    if search:
        search_key = search.lower().strip()

        brands = [
            brand
            for brand in brands
            if search_key in brand.brand_name.lower()
            or search_key in brand.brand_key.lower()
            or search_key in (brand.description or "").lower()
        ]

    brands.sort(key=lambda brand: brand.display_order)

    return BrandListResponse(
        items=brands,
        total=len(brands),
    )


def get_public_brand_by_id(brand_id: str) -> Optional[Brand]:
    for brand in MOCK_BRANDS:
        if brand.brand_id == brand_id and brand.show_flag == "Y":
            return brand

    return None


def get_public_brand_by_key(brand_key: str) -> Optional[Brand]:
    for brand in MOCK_BRANDS:
        if brand.brand_key == brand_key and brand.show_flag == "Y":
            return brand

    return None