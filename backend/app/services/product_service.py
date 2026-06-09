import math
from typing import Optional

from app.models.product import Product, ProductListResponse


# Temporary mock data only.
# Later this will be replaced by DynamoDB.
MOCK_PRODUCTS: list[Product] = [
    Product(
        product_id="PROD-001",
        show_flag="Y",
        display_order=1,
        product_name="Dahua 2MP Full HD Bullet Camera",
        product_model="DH-HAC-B1A21P",
        product_slug="dahua-2mp-full-hd-bullet-camera",
        category="cctv",
        subcategory="2MP Bullet Camera",
        brand_id="BRAND-001",
        product_brand_name="dahua",
        description="Reliable 2MP CCTV bullet camera for residential and small business use.",
        features=["2MP Full HD", "Night Vision", "Weather Resistant", "Indoor/Outdoor"],
        price=2450.00,
        old_price=None,
        sale_price=None,
        image_path="/assets/images/products/dahua-2mp-bullet.jpg",
        brand_logo_path="/assets/images/brands/dahua.png",
        stock_quantity=25,
        low_stock_threshold=10,
    ),
    Product(
        product_id="PROD-002",
        show_flag="Y",
        display_order=2,
        product_name="Hikvision 4MP Dome Camera",
        product_model="DS-2CE76D0T",
        product_slug="hikvision-4mp-dome-camera",
        category="cctv",
        subcategory="4MP Dome Camera",
        brand_id="BRAND-002",
        product_brand_name="hikvision",
        description="Compact dome camera suitable for indoor security installations.",
        features=["4MP Resolution", "IR Night Vision", "Wide Angle", "Ceiling Mount"],
        price=3200.00,
        old_price=3600.00,
        sale_price=2950.00,
        image_path="/assets/images/products/hikvision-4mp-dome.jpg",
        brand_logo_path="/assets/images/brands/hikvision.png",
        stock_quantity=8,
        low_stock_threshold=10,
    ),
    Product(
        product_id="PROD-003",
        show_flag="Y",
        display_order=3,
        product_name="Dahua 4 Channel CCTV Package",
        product_model="RSA-PKG-4CH-DAHUA",
        product_slug="dahua-4-channel-cctv-package",
        category="packages",
        subcategory="4 Channel CCTV Package",
        brand_id="BRAND-001",
        product_brand_name="dahua",
        description="Recommended CCTV package for homes and small shops.",
        features=["4 Cameras", "Recorder Included", "Mobile View", "Basic Installation Included"],
        price=18500.00,
        old_price=21000.00,
        sale_price=17500.00,
        image_path="/assets/images/packages/dahua-4ch-package.jpg",
        brand_logo_path="/assets/images/brands/dahua.png",
        stock_quantity=5,
        low_stock_threshold=3,
    ),
    Product(
        product_id="PROD-004",
        show_flag="Y",
        display_order=4,
        product_name="Hikvision 8 Channel NVR",
        product_model="DS-7608NI",
        product_slug="hikvision-8-channel-nvr",
        category="recorders",
        subcategory="Network Video Recorder",
        brand_id="BRAND-002",
        product_brand_name="hikvision",
        description="8 channel NVR for IP CCTV camera systems.",
        features=["8 Channel", "IP Camera Support", "Remote Viewing", "HDMI Output"],
        price=7800.00,
        old_price=None,
        sale_price=None,
        image_path="/assets/images/products/hikvision-8ch-nvr.jpg",
        brand_logo_path="/assets/images/brands/hikvision.png",
        stock_quantity=12,
        low_stock_threshold=5,
    ),
    Product(
        product_id="PROD-005",
        show_flag="Y",
        display_order=5,
        product_name="D-Link Network Switch",
        product_model="DGS-1008A",
        product_slug="dlink-network-switch",
        category="networking",
        subcategory="Network Switch",
        brand_id="BRAND-003",
        product_brand_name="d-link",
        description="Network switch for CCTV and office network installations.",
        features=["8 Ports", "Gigabit Speed", "Plug and Play", "Compact Design"],
        price=1800.00,
        old_price=None,
        sale_price=None,
        image_path="/assets/images/products/dlink-switch.jpg",
        brand_logo_path="/assets/images/brands/dlink.png",
        stock_quantity=30,
        low_stock_threshold=10,
    ),
    Product(
        product_id="PROD-006",
        show_flag="N",
        display_order=6,
        product_name="Hidden Test Product",
        product_model="HIDDEN-001",
        product_slug="hidden-test-product",
        category="accessories",
        subcategory="Hidden Item",
        brand_id="BRAND-999",
        product_brand_name="test",
        description="This product should not appear in public API results.",
        features=["Hidden product"],
        price=999.00,
        old_price=None,
        sale_price=None,
        image_path="/assets/images/products/hidden.jpg",
        brand_logo_path=None,
        stock_quantity=1,
        low_stock_threshold=1,
    ),
]


def _is_on_sale(product: Product) -> bool:
    return product.sale_price is not None


def _effective_price(product: Product) -> float:
    return product.sale_price if product.sale_price is not None else product.price


def list_public_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    sale: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "default",
    page: int = 1,
    per_page: int = 12,
) -> ProductListResponse:
    products = [product for product in MOCK_PRODUCTS if product.show_flag == "Y"]

    if category and category.lower() not in ["all", "all-products", "all_products"]:
        category_key = category.lower().strip()
        products = [
            product
            for product in products
            if product.category.lower() == category_key
        ]

    if brand:
        brand_key = brand.lower().strip()
        products = [
            product
            for product in products
            if (product.product_brand_name or "").lower() == brand_key
        ]

    if sale is not None:
        if sale:
            products = [product for product in products if _is_on_sale(product)]
        else:
            products = [product for product in products if not _is_on_sale(product)]

    if search:
        search_key = search.lower().strip()

        def matches_search(product: Product) -> bool:
            searchable_values = [
                product.product_name,
                product.product_model or "",
                product.category,
                product.subcategory or "",
                " ".join(product.features),
            ]

            return any(search_key in value.lower() for value in searchable_values)

        products = [product for product in products if matches_search(product)]

    if sort == "price_low":
        products.sort(key=_effective_price)
    elif sort == "price_high":
        products.sort(key=_effective_price, reverse=True)
    elif sort == "newly_added":
        products.sort(key=lambda product: product.display_order, reverse=True)
    elif sort == "on_sale":
        products.sort(
            key=lambda product: (
                0 if _is_on_sale(product) else 1,
                product.display_order,
            )
        )
    else:
        products.sort(key=lambda product: product.display_order)

    total = len(products)
    total_pages = max(math.ceil(total / per_page), 1)

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_items = products[start_index:end_index]

    return ProductListResponse(
        items=paginated_items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


def get_public_product_by_id(product_id: str) -> Optional[Product]:
    for product in MOCK_PRODUCTS:
        if product.product_id == product_id and product.show_flag == "Y":
            return product

    return None