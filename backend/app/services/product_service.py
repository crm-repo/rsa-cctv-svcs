from datetime import datetime, timezone
from math import ceil
from typing import Optional

from app.models.product import Product, ProductListResponse

# batch55b-admin-category-subcategory-brand-protection
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
            or (getattr(product, "subcategory_key", None) and search_value in product.subcategory_key.lower())
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



# --- Batch 20 admin CRUD helpers ---
import re
from typing import Any

from app.services.id_service import (
    generate_brand_id,
    generate_category_id,
    generate_key_feature_id,
    generate_product_id_for_category,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text_value = str(value).strip()
    return text_value or None


def _request_update_data(request: Any) -> dict[str, Any]:
    return request.model_dump(exclude_unset=True)



def _list_all_products_sorted() -> list[Product]:
    products = _get_product_repository().list_all()
    products.sort(key=lambda product: (product.display_seq, product.product_name.lower()))
    return products


def list_admin_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    sale: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 200,
) -> ProductListResponse:
    products = _list_all_products_sorted()

    if category and not _is_all_category(category):
        category_value = category.strip().lower()
        products = [product for product in products if product.category_key.lower() == category_value]

    if brand:
        brand_value = brand.strip().lower()
        products = [
            product
            for product in products
            if product.product_brand_key and product.product_brand_key.lower() == brand_value
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
            if search_value in product.product_id.lower()
            or search_value in product.product_name.lower()
            or (product.product_model and search_value in product.product_model.lower())
            or search_value in product.category_key.lower()
            or search_value in product.category_name.lower()
            or (getattr(product, "subcategory_key", None) and search_value in product.subcategory_key.lower())
            or (product.subcategory and search_value in product.subcategory.lower())
            or (product.product_brand_key and search_value in product.product_brand_key.lower())
            or (product.product_brand_name and search_value in product.product_brand_name.lower())
        ]

    total = len(products)
    total_pages = ceil(total / per_page) if total else 1
    start_index = (page - 1) * per_page
    return ProductListResponse(
        items=products[start_index : start_index + per_page],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


def get_admin_product_by_id(product_id: str) -> Optional[Product]:
    return _get_product_repository().get_by_id(product_id)


def save_admin_product_snapshot(data: dict[str, Any]) -> Product:
    """Persist product snapshot changes made by category/brand admin protection helpers."""
    product = Product.model_validate(data)
    return _get_product_repository().save_product(product)


def _resolve_admin_category(category_id: str | None = None, category_key: str | None = None, *, allow_hidden: bool = False):
    from app.services.category_service import get_admin_category_by_id, get_admin_category_by_key

    category = None
    if category_id:
        category = get_admin_category_by_id(category_id)
    if category is None and category_key:
        category = get_admin_category_by_key(category_key)
    if category is None:
        raise ValueError("A valid category_id or category_key is required.")
    if not allow_hidden and category.show_flag != "Y":
        raise ValueError("Selected category is hidden and cannot be assigned to a new product.")
    return category


def _resolve_admin_subcategory(category, subcategory_key: str | None = None, subcategory: str | None = None) -> tuple[str | None, str | None]:
    clean_key = _clean_text(subcategory_key)
    clean_name = _clean_text(subcategory)
    subcategories = getattr(category, "subcategories", None) or []
    if not clean_key and not clean_name:
        return None, None
    if not subcategories:
        return (_slugify(clean_name or clean_key), clean_name or clean_key)

    normalized_key = _slugify(clean_key or clean_name or "")
    normalized_name = (clean_name or "").strip().lower()
    for item in subcategories:
        item_key = item.subcategory_key.lower()
        item_name = item.subcategory_name.strip().lower()
        if item_key == normalized_key or item_name == normalized_name:
            return item.subcategory_key, item.subcategory_name
    raise ValueError(f"Selected subcategory is not valid for category '{category.category_name}'.")


def _resolve_admin_brand(brand_id: str | None = None, brand_key: str | None = None, *, allow_hidden: bool = False):
    from app.services.brand_service import get_admin_brand_by_id, get_admin_brand_by_key

    brand = None
    if brand_id:
        brand = get_admin_brand_by_id(brand_id)
    if brand is None and brand_key:
        brand = get_admin_brand_by_key(brand_key)
    if brand is not None and not allow_hidden and brand.show_flag != "Y":
        raise ValueError("Selected brand is hidden and cannot be assigned to a new product.")
    return brand


def _validated_features(data: dict[str, Any]) -> dict[str, str | None]:
    features: dict[str, str | None] = {}
    non_empty = 0
    for index in range(1, 11):
        key = f"feature_{index:02d}"
        value = _clean_text(data.get(key))
        features[key] = value
        if value:
            non_empty += 1
    if non_empty < 3:
        raise ValueError("At least 3 product features are required.")
    return features


def _build_product_name(data: dict[str, Any], brand_name: str | None, category_name: str, subcategory: str | None) -> str:
    explicit_name = _clean_text(data.get("product_name"))
    if explicit_name:
        return explicit_name
    parts = [brand_name, _clean_text(data.get("feature_01")), subcategory or category_name]
    generated = " ".join(part for part in parts if part)
    if not generated:
        raise ValueError("Product name is required.")
    return generated


def _next_unique_product_id(repository, category_prefix: str) -> str:
    for _ in range(100):
        candidate = generate_product_id_for_category(category_prefix)
        if repository.get_by_id(candidate) is None:
            return candidate
    raise ValueError("Unable to generate a unique product ID.")


def create_admin_product(request) -> Product:
    repository = _get_product_repository()
    data = request.model_dump()
    category = _resolve_admin_category(data.get("category_id"), data.get("category_key"), allow_hidden=False)
    brand = _resolve_admin_brand(data.get("brand_id"), data.get("product_brand_key"), allow_hidden=False)
    features = _validated_features(data)
    now = _now_utc()
    subcategory_key, subcategory = _resolve_admin_subcategory(category, data.get("subcategory_key"), data.get("subcategory"))
    product_name = _build_product_name(data, brand.brand_name if brand else None, category.category_name, subcategory)

    product = Product(
        product_id=_next_unique_product_id(repository, category.category_prefix),
        show_flag=data.get("show_flag") or "Y",
        show_pack_flag=data.get("show_pack_flag") or "N",
        display_seq=int(data.get("display_seq") or 0),
        product_name=product_name,
        product_model=_clean_text(data.get("product_model")),
        product_slug=_clean_text(data.get("product_slug")) or _slugify(product_name),
        category_id=category.category_id,
        category_key=category.category_key,
        category_name=category.category_name,
        category_prefix=category.category_prefix,
        subcategory_key=subcategory_key,
        subcategory=subcategory,
        brand_id=brand.brand_id if brand else None,
        product_brand_key=brand.brand_key if brand else None,
        product_brand_name=brand.brand_name if brand else None,
        brand_logo_path=brand.brand_logo_path if brand else None,
        description=_clean_text(data.get("description")),
        **features,
        price=float(data.get("price") or 0),
        sale_price=data.get("sale_price"),
        image_path=_clean_text(data.get("image_path")) or "assets/images/products/product-placeholder.png",
        stock_quantity=int(data.get("stock_quantity") or 0),
        low_stock_threshold=int(data.get("low_stock_threshold") or 10),
        meta_title=_clean_text(data.get("meta_title")) or product_name,
        meta_description=_clean_text(data.get("meta_description")),
        created_at=now,
        updated_at=now,
        created_by=_clean_text(data.get("updated_by")) or "admin",
        updated_by=_clean_text(data.get("updated_by")) or "admin",
    )
    return repository.save_product(product)


def update_admin_product(product_id: str, request) -> Optional[Product]:
    repository = _get_product_repository()
    existing = repository.get_by_id(product_id)
    if existing is None:
        return None

    data = existing.model_dump(mode="python")
    update_data = _request_update_data(request)
    for key, value in update_data.items():
        if key == "updated_by":
            continue
        data[key] = value

    category = _resolve_admin_category(
        data.get("category_id"),
        data.get("category_key"),
        allow_hidden=(existing.show_flag != "Y" or existing.category_key == data.get("category_key")),
    )
    data.update(
        category_id=category.category_id,
        category_key=category.category_key,
        category_name=category.category_name,
        category_prefix=category.category_prefix,
    )

    if "brand_id" in update_data or "product_brand_key" in update_data:
        allow_hidden_brand = bool(
            existing.product_brand_key
            and existing.product_brand_key == data.get("product_brand_key")
        )
        brand = _resolve_admin_brand(data.get("brand_id"), data.get("product_brand_key"), allow_hidden=allow_hidden_brand)
        data.update(
            brand_id=brand.brand_id if brand else None,
            product_brand_key=brand.brand_key if brand else None,
            product_brand_name=brand.brand_name if brand else None,
            brand_logo_path=brand.brand_logo_path if brand else None,
        )

    if "subcategory_key" in update_data or "subcategory" in update_data or "category_id" in update_data or "category_key" in update_data:
        subcategory_key, subcategory = _resolve_admin_subcategory(category, data.get("subcategory_key"), data.get("subcategory"))
        data["subcategory_key"] = subcategory_key
        data["subcategory"] = subcategory

    data.update(_validated_features(data))
    data["product_slug"] = _clean_text(data.get("product_slug")) or _slugify(data["product_name"])
    data["updated_at"] = _now_utc()
    data["updated_by"] = _clean_text(update_data.get("updated_by")) or "admin"

    product = Product.model_validate(data)
    return repository.save_product(product)
