from typing import Optional

from app.models.package_banner import PackageBanner, PackageBannerListResponse
from app.services.product_service import get_public_product_by_id, list_public_package_products_for_banner


def _product_to_package_banner(product) -> PackageBanner:
    return PackageBanner(
        package_banner_id=product.product_id,
        product_id=product.product_id,
        show_flag=product.show_flag,
        show_pack_flag=product.show_pack_flag,
        display_seq=product.display_seq,
        product_name=product.product_name,
        banner_image_path=product.image_path,
        price=product.price,
        sale_price=product.sale_price,
    )


def list_public_package_banners(placement: Optional[str] = None) -> PackageBannerListResponse:
    # Phase 8 v5 rule:
    # package banners are derived from rsa_products, not a separate table.
    # placement is accepted for backward-compatible API calls but both homepage
    # and promotions use the same show_pack_flag rule.
    package_products = list_public_package_products_for_banner()
    banners = [_product_to_package_banner(product) for product in package_products]
    return PackageBannerListResponse(items=banners, total=len(banners))


def get_public_package_banner_by_id(package_banner_id: str) -> Optional[PackageBanner]:
    product = get_public_product_by_id(package_banner_id)

    if (
        product is None
        or product.category_key != "packages"
        or product.show_pack_flag != "Y"
    ):
        return None

    return _product_to_package_banner(product)
