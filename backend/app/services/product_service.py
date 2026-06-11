from datetime import datetime, timezone
from math import ceil
from typing import Optional

from app.models.product import Product, ProductListResponse
from app.repositories.repository_factory import create_product_repository


MOCK_PRODUCTS: list[Product] = [
    Product(
        product_id="CCTV-0000001",
        show_flag="Y",
        show_pack_flag="N",
        display_seq=1,
        product_name="Hikvision 6 MP AcuSense Fixed Bullet Camera",
        product_model="DS-2CD2063G2-IU",
        product_slug="hikvision-6mp-acusense-fixed-bullet-camera",
        category_id="CATG-0000001",
        category_key="cctv",
        category_name="CCTV Cameras",
        category_prefix="CCTV",
        subcategory="Fixed Bullet Camera",
        brand_id="BRND-0000002",
        product_brand_key="hikvision",
        product_brand_name="Hikvision",
        brand_logo_path="/assets/images/brands/hikvision.png",
        description="Manually managed product description placeholder for the Hikvision bullet camera.",
        feature_01="6 MP AcuSense",
        feature_02="Smart IR Night Vision",
        feature_03="Weatherproof Outdoor Housing",
        feature_04="Built-in Microphone",
        price=185.00,
        sale_price=165.00,
        image_path="/assets/images/products/hikvision-6mp-bullet.png",
        stock_quantity=18,
        low_stock_threshold=5,
        meta_title="Hikvision 6 MP AcuSense Fixed Bullet Camera",
        meta_description="Hikvision 6 MP AcuSense fixed bullet CCTV camera.",
        created_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="CCTV-0000002",
        show_flag="Y",
        show_pack_flag="N",
        display_seq=2,
        product_name="Dahua 5 MP Starlight Eyeball Camera",
        product_model="IPC-HDW3549H-AS-PV",
        product_slug="dahua-5mp-starlight-eyeball-camera",
        category_id="CATG-0000001",
        category_key="cctv",
        category_name="CCTV Cameras",
        category_prefix="CCTV",
        subcategory="Eyeball Camera",
        brand_id="BRND-0000001",
        product_brand_key="dahua",
        product_brand_name="Dahua",
        brand_logo_path="/assets/images/brands/dahua.png",
        description="Manually managed product description placeholder for the Dahua eyeball camera.",
        feature_01="5 MP Full Color",
        feature_02="Smart IR Night Vision",
        feature_03="Motion Detection Alerts",
        feature_04="Built-in Active Deterrence",
        price=145.00,
        sale_price=None,
        image_path="/assets/images/products/dahua-5mp-eyeball.png",
        stock_quantity=8,
        low_stock_threshold=5,
        meta_title="Dahua 5 MP Starlight Eyeball Camera",
        meta_description="Dahua 5 MP Starlight eyeball CCTV camera.",
        created_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 2, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="RECO-0000001",
        show_flag="Y",
        show_pack_flag="N",
        display_seq=3,
        product_name="Dahua 8 Channel WizSense NVR",
        product_model="NVR2108HS-I2",
        product_slug="dahua-8-channel-wizsense-nvr",
        category_id="CATG-0000002",
        category_key="recorders",
        category_name="Recorders",
        category_prefix="RECO",
        subcategory="Network Video Recorder",
        brand_id="BRND-0000001",
        product_brand_key="dahua",
        product_brand_name="Dahua",
        brand_logo_path="/assets/images/brands/dahua.png",
        description="Manually managed product description placeholder for the Dahua NVR.",
        feature_01="8 Channel Recording",
        feature_02="4K Ultra HD Recording",
        feature_03="Remote Mobile Viewing",
        feature_04="Smart Motion Detection",
        price=220.00,
        sale_price=199.00,
        image_path="/assets/images/products/dahua-8ch-nvr.png",
        stock_quantity=4,
        low_stock_threshold=5,
        meta_title="Dahua 8 Channel WizSense NVR",
        meta_description="Dahua 8 channel WizSense network video recorder.",
        created_at=datetime(2026, 6, 3, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 3, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="RECO-0000002",
        show_flag="Y",
        show_pack_flag="N",
        display_seq=4,
        product_name="Hikvision 16 Channel PoE NVR",
        product_model="DS-7616NI-K2/16P",
        product_slug="hikvision-16-channel-poe-nvr",
        category_id="CATG-0000002",
        category_key="recorders",
        category_name="Recorders",
        category_prefix="RECO",
        subcategory="PoE Network Video Recorder",
        brand_id="BRND-0000002",
        product_brand_key="hikvision",
        product_brand_name="Hikvision",
        brand_logo_path="/assets/images/brands/hikvision.png",
        description="Manually managed product description placeholder for the Hikvision NVR.",
        feature_01="16 Channel PoE",
        feature_02="4K Ultra HD Recording",
        feature_03="Remote Mobile Viewing",
        feature_04="Plug and Play Setup",
        price=390.00,
        sale_price=None,
        image_path="/assets/images/products/hikvision-16ch-poe-nvr.png",
        stock_quantity=6,
        low_stock_threshold=5,
        meta_title="Hikvision 16 Channel PoE NVR",
        meta_description="Hikvision 16 channel PoE network video recorder.",
        created_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 4, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="PACK-0000001",
        show_flag="Y",
        show_pack_flag="Y",
        display_seq=5,
        product_name="Dahua 4 Camera CCTV Package",
        product_model="RSA-PACK-DAHUA-4CH",
        product_slug="dahua-4-camera-cctv-package",
        category_id="CATG-0000003",
        category_key="packages",
        category_name="Packages/Kits",
        category_prefix="PACK",
        subcategory="4 Camera Package",
        brand_id="BRND-0000001",
        product_brand_key="dahua",
        product_brand_name="Dahua",
        brand_logo_path="/assets/images/brands/dahua.png",
        description="Manually managed package description placeholder.",
        feature_01="4 Camera Bundle",
        feature_02="Installation Included",
        feature_03="Remote Mobile Viewing",
        feature_04="Warranty Included",
        price=850.00,
        sale_price=799.00,
        image_path="/assets/images/packages/dahua-4-camera-package.png",
        stock_quantity=10,
        low_stock_threshold=3,
        meta_title="Dahua 4 Camera CCTV Package",
        meta_description="Dahua 4 camera CCTV package with installation.",
        created_at=datetime(2026, 6, 5, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 5, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="PACK-0000002",
        show_flag="Y",
        show_pack_flag="Y",
        display_seq=6,
        product_name="Hikvision 8 Camera CCTV Package",
        product_model="RSA-PACK-HIK-8CH",
        product_slug="hikvision-8-camera-cctv-package",
        category_id="CATG-0000003",
        category_key="packages",
        category_name="Packages/Kits",
        category_prefix="PACK",
        subcategory="8 Camera Package",
        brand_id="BRND-0000002",
        product_brand_key="hikvision",
        product_brand_name="Hikvision",
        brand_logo_path="/assets/images/brands/hikvision.png",
        description="Manually managed package description placeholder.",
        feature_01="8 Camera Bundle",
        feature_02="Installation Included",
        feature_03="Smart IR Night Vision",
        feature_04="Warranty Included",
        price=1450.00,
        sale_price=1299.00,
        image_path="/assets/images/packages/hikvision-8-camera-package.png",
        stock_quantity=7,
        low_stock_threshold=3,
        meta_title="Hikvision 8 Camera CCTV Package",
        meta_description="Hikvision 8 camera CCTV package with installation.",
        created_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 6, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="PACK-0000003",
        show_flag="Y",
        show_pack_flag="N",
        display_seq=7,
        product_name="Uniview 6 Camera CCTV Package",
        product_model="RSA-PACK-UNV-6CH",
        product_slug="uniview-6-camera-cctv-package",
        category_id="CATG-0000003",
        category_key="packages",
        category_name="Packages/Kits",
        category_prefix="PACK",
        subcategory="6 Camera Package",
        brand_id="BRND-0000004",
        product_brand_key="uniview",
        product_brand_name="Uniview",
        brand_logo_path="/assets/images/brands/uniview.png",
        description="Manually managed package description placeholder.",
        feature_01="6 Camera Bundle",
        feature_02="Installation Included",
        feature_03="Remote Mobile Viewing",
        feature_04="Warranty Included",
        price=1180.00,
        sale_price=1099.00,
        image_path="/assets/images/packages/uniview-6-camera-package.png",
        stock_quantity=5,
        low_stock_threshold=3,
        meta_title="Uniview 6 Camera CCTV Package",
        meta_description="Uniview 6 camera CCTV package with installation.",
        created_at=datetime(2026, 6, 7, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 7, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
    Product(
        product_id="CCTV-0000003",
        show_flag="N",
        show_pack_flag="N",
        display_seq=99,
        product_name="Hidden Test CCTV Camera",
        product_model="HIDDEN-CAM-001",
        product_slug="hidden-test-cctv-camera",
        category_id="CATG-0000001",
        category_key="cctv",
        category_name="CCTV Cameras",
        category_prefix="CCTV",
        subcategory="Hidden Test Camera",
        brand_id="BRND-0000001",
        product_brand_key="dahua",
        product_brand_name="Dahua",
        brand_logo_path="/assets/images/brands/dahua.png",
        description="Hidden product used to verify show_flag filtering.",
        feature_01="Hidden Feature 1",
        feature_02="Hidden Feature 2",
        feature_03="Hidden Feature 3",
        price=99.00,
        sale_price=None,
        image_path="/assets/images/products/hidden-test-camera.png",
        stock_quantity=1,
        low_stock_threshold=1,
        created_at=datetime(2026, 6, 8, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 8, tzinfo=timezone.utc),
        created_by="system",
        updated_by="system",
    ),
]


def _is_on_sale(product: Product) -> bool:
    return product.sale_price is not None


def _effective_price(product: Product) -> float:
    return product.sale_price if product.sale_price is not None else product.price


def _feature_values(product: Product) -> list[str]:
    return [
        feature
        for feature in [
            product.feature_01,
            product.feature_02,
            product.feature_03,
            product.feature_04,
            product.feature_05,
            product.feature_06,
            product.feature_07,
            product.feature_08,
            product.feature_09,
            product.feature_10,
        ]
        if feature
    ]


def _is_all_category(category: str) -> bool:
    normalized = category.strip().lower()
    return normalized in {"all", "all-products", "all products"}


def _get_product_repository():
    return create_product_repository(initial_items=MOCK_PRODUCTS)


def list_public_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    sale: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "default",
    page: int = 1,
    per_page: int = 12,
) -> ProductListResponse:
    products = _get_product_repository().list_visible()

    if category and not _is_all_category(category):
        category_value = category.strip().lower()
        products = [
            product
            for product in products
            if product.category_key.lower() == category_value
        ]

    if brand:
        brand_value = brand.strip().lower()
        products = [
            product
            for product in products
            if product.product_brand_key
            and product.product_brand_key.lower() == brand_value
        ]

    if sale is True:
        products = [product for product in products if _is_on_sale(product)]
    elif sale is False:
        products = [product for product in products if not _is_on_sale(product)]

    if search:
        search_value = search.strip().lower()
        products = [
            product
            for product in products
            if search_value in product.product_name.lower()
            or (product.product_model and search_value in product.product_model.lower())
            or search_value in product.category_key.lower()
            or search_value in product.category_name.lower()
            or (product.subcategory and search_value in product.subcategory.lower())
            or (product.product_brand_key and search_value in product.product_brand_key.lower())
            or (product.product_brand_name and search_value in product.product_brand_name.lower())
            or any(search_value in feature.lower() for feature in _feature_values(product))
        ]

    if sort == "price_low":
        products.sort(key=_effective_price)
    elif sort == "price_high":
        products.sort(key=_effective_price, reverse=True)
    elif sort == "newly_added":
        products.sort(key=lambda product: product.created_at, reverse=True)
    elif sort == "on_sale":
        products.sort(key=lambda product: (not _is_on_sale(product), product.display_seq))
    else:
        products.sort(key=lambda product: product.display_seq)

    total = len(products)
    total_pages = ceil(total / per_page) if total else 1
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_products = products[start_index:end_index]

    return ProductListResponse(
        items=paginated_products,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


def get_public_product_by_id(product_id: str) -> Optional[Product]:
    return _get_product_repository().get_visible_by_id(product_id)


def list_public_package_products_for_banner() -> list[Product]:
    package_products = [
        product
        for product in _get_product_repository().list_visible()
        if product.category_key == "packages"
        and product.show_pack_flag == "Y"
    ]
    package_products.sort(key=lambda product: product.display_seq)
    return package_products
