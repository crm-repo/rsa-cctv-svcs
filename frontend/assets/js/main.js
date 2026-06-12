const RSA_PUBLIC_CATALOG_DYNAMIC_VERSION = "batch49b-api-page-limit-fix";
const mobileMenuButton = document.getElementById("mobileMenuButton");
const mobileMenu = document.getElementById("mobileMenu");
const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

if (mobileMenuButton && mobileMenu && mobileMenuOverlay) {
  mobileMenuButton.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
    mobileMenuOverlay.classList.toggle("hidden");

    mobileMenuButton.innerHTML = mobileMenu.classList.contains("hidden") ? "☰" : "×";
  });

  mobileMenuOverlay.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
    mobileMenuOverlay.classList.add("hidden");
    mobileMenuButton.innerHTML = "☰";
  });

  const mobileMenuLinks = mobileMenu.querySelectorAll("a");

  mobileMenuLinks.forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenu.classList.add("hidden");
      mobileMenuOverlay.classList.add("hidden");
      mobileMenuButton.innerHTML = "☰";
    });
  });
}

/* =========================
   FEATURED PRODUCTS PAGING
   Dots + left/right arrows
========================= */

const featuredGrid = document.getElementById("featuredProductsGrid");
const featuredDotsContainer = document.getElementById("featuredProductsDots");
const featuredPrevBtn = document.querySelector(".home-featured-arrow-prev");
const featuredNextBtn = document.querySelector(".home-featured-arrow-next");

if (featuredGrid && featuredDotsContainer) {
  const productCards = Array.from(featuredGrid.querySelectorAll(".featured-product-card"));
  let currentPage = 0;

  let featuredTouchStartX = 0;
  let featuredTouchEndX = 0;

  function getProductsPerPage() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches
      ? 6
      : 5;
  }

  function isFeaturedMobileView() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches;
  }

  function updateFeaturedArrows(totalPages) {
    if (!featuredPrevBtn || !featuredNextBtn) return;

    if (!isFeaturedMobileView() || totalPages <= 1) {
      featuredPrevBtn.classList.add("is-hidden");
      featuredNextBtn.classList.add("is-hidden");
      return;
    }

    if (currentPage <= 0) {
      featuredPrevBtn.classList.add("is-hidden");
    } else {
      featuredPrevBtn.classList.remove("is-hidden");
    }

    if (currentPage >= totalPages - 1) {
      featuredNextBtn.classList.add("is-hidden");
    } else {
      featuredNextBtn.classList.remove("is-hidden");
    }
  }

  function renderFeaturedProducts() {
    const perPage = getProductsPerPage();
    const totalPages = Math.ceil(productCards.length / perPage);

    if (currentPage >= totalPages) {
      currentPage = totalPages - 1;
    }

    if (currentPage < 0) {
      currentPage = 0;
    }

    productCards.forEach((card, index) => {
      const start = currentPage * perPage;
      const end = start + perPage;

      card.style.display = index >= start && index < end ? "grid" : "none";
    });

    featuredDotsContainer.innerHTML = "";

    for (let i = 0; i < totalPages; i++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "featured-dot";

      if (i === currentPage) {
        dot.classList.add("active");
      }

      dot.addEventListener("click", () => {
        currentPage = i;
        renderFeaturedProducts();
      });

      featuredDotsContainer.appendChild(dot);
    }

    updateFeaturedArrows(totalPages);
  }

  if (featuredNextBtn) {
    featuredNextBtn.addEventListener("click", () => {
      const perPage = getProductsPerPage();
      const totalPages = Math.ceil(productCards.length / perPage);

      if (currentPage < totalPages - 1) {
        currentPage++;
        renderFeaturedProducts();
      }
    });
  }

  if (featuredPrevBtn) {
    featuredPrevBtn.addEventListener("click", () => {
      if (currentPage > 0) {
        currentPage--;
        renderFeaturedProducts();
      }
    });
  }

  featuredGrid.addEventListener("touchstart", (event) => {
    featuredTouchStartX = event.touches[0].clientX;
  });

  featuredGrid.addEventListener("touchend", (event) => {
    featuredTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = featuredTouchStartX - featuredTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    const perPage = getProductsPerPage();
    const totalPages = Math.ceil(productCards.length / perPage);

    if (swipeDistance > 0 && currentPage < totalPages - 1) {
      currentPage++;
    } else if (swipeDistance < 0 && currentPage > 0) {
      currentPage--;
    }

    renderFeaturedProducts();
  });

  renderFeaturedProducts();

  let lastFeaturedPerPage = getProductsPerPage();

  window.addEventListener("resize", () => {
    const currentPerPage = getProductsPerPage();

    if (currentPerPage !== lastFeaturedPerPage) {
      lastFeaturedPerPage = currentPerPage;
      currentPage = 0;
      renderFeaturedProducts();
    }
  });
}

/* =========================
   PROMO PRODUCTS PAGING
   Dots + left/right arrows
========================= */

const promoGrid = document.getElementById("promoProductsGrid");
const promoDotsContainer = document.getElementById("promoProductsDots");
const promoPrevBtn = document.querySelector(".home-promo-arrow-prev");
const promoNextBtn = document.querySelector(".home-promo-arrow-next");

if (promoGrid && promoDotsContainer) {
  const promoCards = Array.from(promoGrid.querySelectorAll(".promo-product-card"));
  let currentPromoPage = 0;
  let promoTouchStartX = 0;
  let promoTouchEndX = 0;

  function getPromoProductsPerPage() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches
      ? 6
      : 5;
  }

  function isPromoMobileView() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches;
  }

  function updatePromoArrows(totalPages) {
    if (!promoPrevBtn || !promoNextBtn) return;

    if (!isPromoMobileView() || totalPages <= 1) {
      promoPrevBtn.classList.add("is-hidden");
      promoNextBtn.classList.add("is-hidden");
      return;
    }

    if (currentPromoPage <= 0) {
      promoPrevBtn.classList.add("is-hidden");
    } else {
      promoPrevBtn.classList.remove("is-hidden");
    }

    if (currentPromoPage >= totalPages - 1) {
      promoNextBtn.classList.add("is-hidden");
    } else {
      promoNextBtn.classList.remove("is-hidden");
    }
  }

  function renderPromoProducts() {
    const perPage = getPromoProductsPerPage();
    const totalPages = Math.ceil(promoCards.length / perPage);

    if (currentPromoPage >= totalPages) {
      currentPromoPage = totalPages - 1;
    }

    if (currentPromoPage < 0) {
      currentPromoPage = 0;
    }

    promoCards.forEach((card, index) => {
      const start = currentPromoPage * perPage;
      const end = start + perPage;

      card.style.display = index >= start && index < end ? "grid" : "none";
    });

    promoDotsContainer.innerHTML = "";

    for (let i = 0; i < totalPages; i++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "promo-dot";

      if (i === currentPromoPage) {
        dot.classList.add("active");
      }

      dot.addEventListener("click", () => {
        currentPromoPage = i;
        renderPromoProducts();
      });

      promoDotsContainer.appendChild(dot);
    }

    updatePromoArrows(totalPages);
  }

  if (promoNextBtn) {
    promoNextBtn.addEventListener("click", () => {
      const perPage = getPromoProductsPerPage();
      const totalPages = Math.ceil(promoCards.length / perPage);

      if (currentPromoPage < totalPages - 1) {
        currentPromoPage++;
        renderPromoProducts();
      }
    });
  }

  if (promoPrevBtn) {
    promoPrevBtn.addEventListener("click", () => {
      if (currentPromoPage > 0) {
        currentPromoPage--;
        renderPromoProducts();
      }
    });
  }

  promoGrid.addEventListener("touchstart", (event) => {
    promoTouchStartX = event.touches[0].clientX;
  });

  promoGrid.addEventListener("touchend", (event) => {
    promoTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = promoTouchStartX - promoTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    const perPage = getPromoProductsPerPage();
    const totalPages = Math.ceil(promoCards.length / perPage);

    if (swipeDistance > 0 && currentPromoPage < totalPages - 1) {
      currentPromoPage++;
    } else if (swipeDistance < 0 && currentPromoPage > 0) {
      currentPromoPage--;
    }

    renderPromoProducts();
  });

  renderPromoProducts();

  let lastPromoPerPage = getPromoProductsPerPage();

  window.addEventListener("resize", () => {
    const currentPerPage = getPromoProductsPerPage();

    if (currentPerPage !== lastPromoPerPage) {
      lastPromoPerPage = currentPerPage;
      currentPromoPage = 0;
      renderPromoProducts();
    }
  });
}

/* =========================
   PROMOTIONS HERO MOBILE SLIDER
========================= */

const promoHeroGrid = document.querySelector(".promotions-hero-grid");

if (promoHeroGrid) {
  const promoHeroSlides = Array.from(
    promoHeroGrid.querySelectorAll(".promotions-hero-banner")
  );

  let promoHeroIndex = 0;

  function renderPromoHeroSlide() {
    promoHeroSlides.forEach((slide) => {
      slide.style.transform = `translateX(-${promoHeroIndex * 100}%)`;
    });
  }

  if (promoHeroSlides.length > 1) {
    setInterval(() => {
      const isMobilePortrait = window.matchMedia(
        "(max-width: 767px) and (orientation: portrait)"
      ).matches;

      if (!isMobilePortrait) return;

      promoHeroIndex = (promoHeroIndex + 1) % promoHeroSlides.length;
      renderPromoHeroSlide();
    }, 3000);
  }
}

/* =========================
   HOME PACKAGE MOBILE SLIDER
   Dots + left/right arrows
========================= */

const homePackageSlider = document.getElementById("homePackageSlider");
const homePackageDots = document.getElementById("homePackageDots");
const homePackagePrevBtn = document.querySelector(".home-package-arrow-prev");
const homePackageNextBtn = document.querySelector(".home-package-arrow-next");

if (homePackageSlider && homePackageDots) {
  const packageSlides = Array.from(
    homePackageSlider.querySelectorAll(".package-banner-card")
  );

  let currentPackageSlide = 0;
  let packageTouchStartX = 0;
  let packageTouchEndX = 0;

  function isMobilePackageView() {
    return window.matchMedia(
      "(max-width: 799px) and (orientation: portrait), (max-height: 430px) and (orientation: landscape)"
    ).matches;
  }

  function updateHomePackageArrows() {
    if (!homePackagePrevBtn || !homePackageNextBtn) return;

    if (!isMobilePackageView()) {
      homePackagePrevBtn.classList.add("is-hidden");
      homePackageNextBtn.classList.add("is-hidden");
      return;
    }

    if (currentPackageSlide <= 0) {
      homePackagePrevBtn.classList.add("is-hidden");
    } else {
      homePackagePrevBtn.classList.remove("is-hidden");
    }

    if (currentPackageSlide >= packageSlides.length - 1) {
      homePackageNextBtn.classList.add("is-hidden");
    } else {
      homePackageNextBtn.classList.remove("is-hidden");
    }
  }

  function renderHomePackageSlider() {
    packageSlides.forEach((slide) => {
      slide.style.transform = isMobilePackageView()
        ? `translateX(-${currentPackageSlide * 100}%)`
        : "translateX(0)";
    });

    homePackageDots.innerHTML = "";

    packageSlides.forEach((_, index) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "home-package-dot";

      if (index === currentPackageSlide) {
        dot.classList.add("active");
      }

      dot.addEventListener("click", () => {
        currentPackageSlide = index;
        renderHomePackageSlider();
      });

      homePackageDots.appendChild(dot);
    });

    updateHomePackageArrows();
  }

  if (homePackageNextBtn) {
    homePackageNextBtn.addEventListener("click", () => {
      if (!isMobilePackageView()) return;

      if (currentPackageSlide < packageSlides.length - 1) {
        currentPackageSlide++;
        renderHomePackageSlider();
      }
    });
  }

  if (homePackagePrevBtn) {
    homePackagePrevBtn.addEventListener("click", () => {
      if (!isMobilePackageView()) return;

      if (currentPackageSlide > 0) {
        currentPackageSlide--;
        renderHomePackageSlider();
      }
    });
  }

  homePackageSlider.addEventListener("touchstart", (event) => {
    if (!isMobilePackageView()) return;
    packageTouchStartX = event.touches[0].clientX;
  });

  homePackageSlider.addEventListener("touchend", (event) => {
    if (!isMobilePackageView()) return;

    packageTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = packageTouchStartX - packageTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    if (swipeDistance > 0 && currentPackageSlide < packageSlides.length - 1) {
      currentPackageSlide++;
    } else if (swipeDistance < 0 && currentPackageSlide > 0) {
      currentPackageSlide--;
    }

    renderHomePackageSlider();
  });

  renderHomePackageSlider();

  window.addEventListener("resize", () => {
    if (!isMobilePackageView()) {
      currentPackageSlide = 0;
    }

    renderHomePackageSlider();
  });
}

/* =========================
   HOME TOP BRANDS PAGING
   Dots + left/right arrows
========================= */

const homeBrandsGrid = document.getElementById("homeBrandsGrid");
const homeBrandsDots = document.getElementById("homeBrandsDots");
const homeBrandsPrevBtn = document.querySelector(".home-brands-arrow-prev");
const homeBrandsNextBtn = document.querySelector(".home-brands-arrow-next");

if (homeBrandsGrid && homeBrandsDots) {
  const brandItems = Array.from(
    homeBrandsGrid.querySelectorAll(".home-brand-item")
  );

  let currentBrandPage = 0;
  let brandTouchStartX = 0;
  let brandTouchEndX = 0;

  function getHomeBrandsPerPage() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches
      ? 6   // mobile: 2 columns x 3 rows
      : 9;  // desktop: 3 columns x 3 rows
  }

  function isHomeBrandsMobileView() {
    return window.matchMedia("(max-width: 767px) and (orientation: portrait)").matches;
  }

  function updateHomeBrandsArrows(totalPages) {
    if (!homeBrandsPrevBtn || !homeBrandsNextBtn) return;

    if (!isHomeBrandsMobileView() || totalPages <= 1) {
      homeBrandsPrevBtn.classList.add("is-hidden");
      homeBrandsNextBtn.classList.add("is-hidden");
      return;
    }

    if (currentBrandPage <= 0) {
      homeBrandsPrevBtn.classList.add("is-hidden");
    } else {
      homeBrandsPrevBtn.classList.remove("is-hidden");
    }

    if (currentBrandPage >= totalPages - 1) {
      homeBrandsNextBtn.classList.add("is-hidden");
    } else {
      homeBrandsNextBtn.classList.remove("is-hidden");
    }
  }

  function renderHomeBrands() {
    const brandsPerPage = getHomeBrandsPerPage();
    const totalPages = Math.ceil(brandItems.length / brandsPerPage);

    if (currentBrandPage >= totalPages) {
      currentBrandPage = totalPages - 1;
    }

    if (currentBrandPage < 0) {
      currentBrandPage = 0;
    }

    brandItems.forEach((item, index) => {
      const start = currentBrandPage * brandsPerPage;
      const end = start + brandsPerPage;

      item.style.display = index >= start && index < end ? "flex" : "none";
    });

    homeBrandsDots.innerHTML = "";

    for (let i = 0; i < totalPages; i++) {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "home-brand-dot";

      if (i === currentBrandPage) {
        dot.classList.add("active");
      }

      dot.addEventListener("click", () => {
        currentBrandPage = i;
        renderHomeBrands();
      });

      homeBrandsDots.appendChild(dot);
    }

    updateHomeBrandsArrows(totalPages);
  }

  if (homeBrandsNextBtn) {
    homeBrandsNextBtn.addEventListener("click", () => {
      const brandsPerPage = getHomeBrandsPerPage();
      const totalPages = Math.ceil(brandItems.length / brandsPerPage);

      if (currentBrandPage < totalPages - 1) {
        currentBrandPage++;
        renderHomeBrands();
      }
    });
  }

  if (homeBrandsPrevBtn) {
    homeBrandsPrevBtn.addEventListener("click", () => {
      if (currentBrandPage > 0) {
        currentBrandPage--;
        renderHomeBrands();
      }
    });
  }

  homeBrandsGrid.addEventListener("touchstart", (event) => {
    brandTouchStartX = event.touches[0].clientX;
  });

  homeBrandsGrid.addEventListener("touchend", (event) => {
    brandTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = brandTouchStartX - brandTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    const brandsPerPage = getHomeBrandsPerPage();
    const totalPages = Math.ceil(brandItems.length / brandsPerPage);

    if (swipeDistance > 0 && currentBrandPage < totalPages - 1) {
      currentBrandPage++;
    } else if (swipeDistance < 0 && currentBrandPage > 0) {
      currentBrandPage--;
    }

    renderHomeBrands();
  });

  renderHomeBrands();

  window.addEventListener("resize", () => {
    currentBrandPage = 0;
    renderHomeBrands();
  });
}

/* =========================
   PRODUCTS / PROMOTIONS / BRANDS DYNAMIC API CATALOG
   Renders public catalog pages from backend APIs instead of static HTML cards.
========================= */

const productsGrid = document.querySelector(".products-catalog-grid");
const productsCount = document.getElementById("productsCount");
const productsPageNumbers = document.getElementById("productsPageNumbers");
const productsPrevBtn = document.getElementById("productsPrevBtn");
const productsNextBtn = document.getElementById("productsNextBtn");
const productFilterButtons = document.querySelectorAll(".product-filter-btn");
const productsSectionTitle = document.getElementById("productsSectionTitle");
const productsSearchInput = document.getElementById("productsSearchInput");
const productsEmptyState = document.getElementById("productsEmptyState");
const productsSortDropdown = document.getElementById("productsSortDropdown");
const isPromotionsPage = document.body.classList.contains("promotions-page");
const isBrandsPage = document.body.classList.contains("brands-page");

if (productsGrid && productsPageNumbers && productsPrevBtn && productsNextBtn) {
  let allProductCards = [];
  let publicProducts = [];
  let publicBrands = [];
  let currentProductsPage = 0;
  let currentFilter = "all";
  let currentSearch = "";
  let currentSort = "default";
  let currentBrand = "all";
  let currentBrandLabel = "";

  const filterTitles = {
    all: "All Products",
    sale: "Sale Products",
    cctv: "CCTV Cameras",
    recorders: "Recorders",
    networking: "Networking",
    accessories: "Accessories",
    power: "Power Supply",
    storage: "Storage",
    packages: "Packages/Kits"
  };

  function getPublicApiBaseUrl() {
    if (window.RSA_API_BASE_URL) return String(window.RSA_API_BASE_URL).replace(/\/$/, "");
    if (window.RSA_API_CONFIG && window.RSA_API_CONFIG.baseUrl) {
      return String(window.RSA_API_CONFIG.baseUrl).replace(/\/$/, "");
    }
    if (window.location.protocol === "file:") return "http://127.0.0.1:8000";
    return "";
  }

  function apiUrl(path) {
    const baseUrl = getPublicApiBaseUrl();
    return `${baseUrl}${path}`;
  }

  async function fetchJson(path) {
    const response = await fetch(apiUrl(path), {
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`${path} returned HTTP ${response.status}`);
    }

    return response.json();
  }

  function extractItems(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return [];

    const candidates = [
      payload.items,
      payload.data,
      payload.products,
      payload.brands,
      payload.categories,
      payload.results,
      payload.records,
      payload.rows
    ];

    for (const candidate of candidates) {
      if (Array.isArray(candidate)) return candidate;
    }

    if (payload.body) return extractItems(payload.body);
    return [];
  }

  async function fetchPagedApiItems(path, perPage = 50) {
    const safePerPage = Math.min(Math.max(Number(perPage) || 50, 1), 50);
    const separator = path.includes("?") ? "&" : "?";
    const firstPayload = await fetchJson(`${path}${separator}page=1&per_page=${safePerPage}`);
    const firstItems = extractItems(firstPayload);
    const totalPages = Number(firstPayload?.total_pages || 1);

    if (!Number.isFinite(totalPages) || totalPages <= 1) {
      return firstItems;
    }

    const remainingRequests = [];
    for (let page = 2; page <= totalPages; page++) {
      remainingRequests.push(fetchJson(`${path}${separator}page=${page}&per_page=${safePerPage}`));
    }

    const remainingPayloads = await Promise.all(remainingRequests);
    return firstItems.concat(...remainingPayloads.map(extractItems));
  }

  function slugify(value) {
    return String(value || "")
      .toLowerCase()
      .trim()
      .replace(/&/g, "and")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function normalizeAssetPath(pathValue, fallback) {
    const value = String(pathValue || "").trim();
    if (!value) return fallback;
    if (/^(https?:)?\/\//i.test(value) || value.startsWith("data:") || value.startsWith("/")) return value;
    if (value.startsWith("./")) return value;
    if (value.startsWith("assets/") || value.startsWith("uploads/")) return `./${value}`;
    if (value.includes("/")) return `./${value.replace(/^\/+/, "")}`;
    return fallback;
  }

  function firstNonEmpty(...values) {
    for (const value of values) {
      if (value !== undefined && value !== null && String(value).trim() !== "") return value;
    }
    return "";
  }

  function numericValue(value) {
    if (value === undefined || value === null || value === "") return null;
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    const cleaned = String(value).replace(/[^0-9.-]/g, "");
    if (!cleaned) return null;
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function formatPrice(value, fallback = "Get Quotation") {
    if (value === undefined || value === null || String(value).trim() === "") return fallback;
    const asString = String(value).trim();
    if (asString.toLowerCase().includes("quotation") || asString.includes("₱")) return asString;
    const parsed = numericValue(value);
    if (parsed === null) return asString;
    return `₱${parsed.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  function collectFeatures(product) {
    const features = [];

    const arrayFeatures = firstNonEmpty(product.features, product.key_features, product.product_features);
    if (Array.isArray(arrayFeatures)) {
      arrayFeatures.forEach((feature) => {
        if (feature !== undefined && feature !== null && String(feature).trim()) features.push(String(feature).trim());
      });
    } else if (typeof arrayFeatures === "string" && arrayFeatures.trim()) {
      arrayFeatures.split(/[|\n]/).forEach((feature) => {
        if (feature.trim()) features.push(feature.trim());
      });
    }

    for (let index = 1; index <= 10; index += 1) {
      const paddedKey = `feature_${String(index).padStart(2, "0")}`;
      const looseKey = `feature_${index}`;
      const feature = firstNonEmpty(product[paddedKey], product[looseKey]);
      if (feature && !features.includes(String(feature).trim())) features.push(String(feature).trim());
    }

    return features;
  }

  function normalizeProduct(product) {
    const brandName = firstNonEmpty(
      product.product_brand_name,
      product.brand_name,
      product.product_brand,
      product.brand,
      product.product_brand_key,
      product.brand_key
    );

    const categoryKey = firstNonEmpty(
      product.category_key,
      product.product_category_key,
      product.category,
      slugify(product.category_name)
    );

    const rawPrice = firstNonEmpty(product.price, product.product_price, product.base_price, product.regular_price);
    const rawSalePrice = firstNonEmpty(product.sale_price, product.promo_price, product.discount_price);
    const hasSalePrice = rawSalePrice !== "" && rawSalePrice !== null && rawSalePrice !== undefined;

    const displayPrice = hasSalePrice ? rawSalePrice : rawPrice;
    const features = collectFeatures(product);

    return {
      id: firstNonEmpty(product.product_id, product.id, product.pk, product.sk),
      name: firstNonEmpty(product.product_name, product.name, product.title, "Unnamed Product"),
      model: firstNonEmpty(product.product_model, product.model, product.model_number, product.sku, product.product_id),
      categoryKey: slugify(categoryKey),
      categoryName: firstNonEmpty(product.subcategory, product.sub_category, product.product_category, product.category_name, categoryKey),
      brandKey: slugify(firstNonEmpty(product.product_brand_key, product.brand_key, brandName)),
      brandName: firstNonEmpty(brandName, "Brand"),
      imagePath: normalizeAssetPath(
        firstNonEmpty(product.product_image_path, product.image_path, product.image_url, product.product_image, product.photo_path),
        "./assets/images/rsa-logo.png"
      ),
      brandLogoPath: normalizeAssetPath(
        firstNonEmpty(product.brand_logo_path, product.product_brand_logo_path, product.logo_path, product.brand_image_path),
        "./assets/images/rsa-logo.png"
      ),
      stock: numericValue(firstNonEmpty(product.stock_quantity, product.stock, product.quantity, product.inventory_quantity)) ?? 999,
      lowQuantity: numericValue(firstNonEmpty(product.low_quantity, product.low_stock_quantity, product.low_stock_threshold)) ?? 10,
      price: formatPrice(displayPrice),
      regularPrice: formatPrice(rawPrice, ""),
      salePrice: hasSalePrice ? formatPrice(rawSalePrice) : "",
      oldPrice: hasSalePrice ? formatPrice(rawPrice, "") : "",
      features
    };
  }

  function normalizeBrand(brand) {
    const name = firstNonEmpty(brand.brand_name, brand.product_brand_name, brand.name, brand.title, brand.brand_key, brand.product_brand_key);
    const key = slugify(firstNonEmpty(brand.brand_key, brand.product_brand_key, name));
    const logo = normalizeAssetPath(
      firstNonEmpty(brand.brand_logo_path, brand.logo_path, brand.image_path, brand.brand_image_path, brand.image_url),
      "./assets/images/rsa-logo.png"
    );

    return { key, name: firstNonEmpty(name, key), logo };
  }

  function renderProductCard(product) {
    const normalized = normalizeProduct(product);
    const hasSale = Boolean(normalized.salePrice && normalized.oldPrice);
    const stockClass = normalized.stock === 0 ? "sold-out" : normalized.stock <= normalized.lowQuantity ? "low-stock" : "in-stock";
    const stockLabel = normalized.stock === 0 ? "Sold Out" : normalized.stock <= normalized.lowQuantity ? "Low Stock" : "In Stock";
    const featureText = normalized.features.join("|");

    const card = document.createElement("div");
    card.className = "catalog-product-card";
    card.dataset.productId = normalized.id;
    card.dataset.category = normalized.categoryKey;
    card.dataset.productBrandName = normalized.brandKey;
    card.dataset.productName = normalized.name;
    card.dataset.productModel = normalized.model;
    card.dataset.productCategory = normalized.categoryName;
    card.dataset.productPrice = normalized.price;
    card.dataset.productImage = normalized.imagePath;
    card.dataset.productBrand = normalized.brandLogoPath;
    card.dataset.productStock = String(normalized.stock);
    card.dataset.productLowQuantity = String(normalized.lowQuantity);
    card.dataset.productFeatures = featureText;

    if (hasSale) {
      card.dataset.productOldPrice = normalized.oldPrice;
    }

    card.innerHTML = `
      ${hasSale ? '<span class="catalog-sale-badge">SALE</span>' : ''}
      <div class="catalog-product-image"><img src="${escapeHtml(normalized.imagePath)}" alt="${escapeHtml(normalized.name)}"></div>
      <span class="catalog-stock-badge ${stockClass}">${stockLabel}</span>
      <img class="catalog-brand-logo" src="${escapeHtml(normalized.brandLogoPath)}" alt="${escapeHtml(normalized.brandName)}">
      <p class="catalog-product-model">${escapeHtml(normalized.model)}</p>
      <h3 class="catalog-product-name">${escapeHtml(normalized.name)}</h3>
      <p class="catalog-product-subcategory">${escapeHtml(normalized.categoryName)}</p>
      ${hasSale
        ? `<div class="catalog-price-row"><span class="catalog-old-price">${escapeHtml(normalized.oldPrice)}</span><span class="catalog-sale-price">${escapeHtml(normalized.salePrice)}</span></div>`
        : `<p class="catalog-product-price">${escapeHtml(normalized.price)}</p>`}
    `;

    return card;
  }

  function renderBrandStrips() {
    if (!publicBrands.length) return;

    const rows = document.querySelectorAll(".product-brand-scroll-wrap .brand-strip-row, #brandsPageStrip");

    rows.forEach((row) => {
      row.innerHTML = "";

      publicBrands.forEach((brand) => {
        const item = document.createElement("div");
        item.className = "brand-strip-item";
        item.dataset.brandFilter = brand.key;
        item.innerHTML = `<img src="${escapeHtml(brand.logo)}" alt="${escapeHtml(brand.name)}">`;
        row.appendChild(item);
      });
    });

    const heroGrid = document.querySelector(".brands-hero-grid");
    if (isBrandsPage && heroGrid) {
      heroGrid.innerHTML = "";
      publicBrands.slice(0, 12).forEach((brand) => {
        const item = document.createElement("div");
        item.innerHTML = `<img src="${escapeHtml(brand.logo)}" alt="${escapeHtml(brand.name)}">`;
        heroGrid.appendChild(item);
      });
    }
  }

  async function renderPromotionHeroBanners() {
    if (!isPromotionsPage) return;

    const heroGrid = document.querySelector(".promotions-hero-grid");
    if (!heroGrid) return;

    try {
      const payload = await fetchJson("/api/package-banners?per_page=12&page_size=12&limit=12");
      const banners = extractItems(payload);
      if (!banners.length) return;

      heroGrid.innerHTML = "";
      banners.slice(0, 3).forEach((banner, index) => {
        const imagePath = normalizeAssetPath(
          firstNonEmpty(banner.image_path, banner.product_image_path, banner.banner_image_path, banner.image_url, banner.product_image),
          "./assets/images/rsa-logo.png"
        );
        const title = firstNonEmpty(banner.product_name, banner.title, banner.name, `Promo Package ${index + 1}`);
        const item = document.createElement("div");
        item.className = "promotions-hero-banner";
        item.innerHTML = `<img src="${escapeHtml(imagePath)}" alt="${escapeHtml(title)}">`;
        heroGrid.appendChild(item);
      });
    } catch (error) {
      console.warn("Package banner API unavailable; keeping existing promotion banners.", error);
    }
  }

  function getProductsPerPage() {
    const isMobilePortrait = window.matchMedia(
      "(max-width: 767px) and (orientation: portrait)"
    ).matches;

    const isSmallLandscape = window.matchMedia(
      "(max-width: 700px) and (orientation: landscape)"
    ).matches;

    const isMediumLandscape = window.matchMedia(
      "(min-width: 701px) and (max-width: 850px) and (orientation: landscape)"
    ).matches;

    const isLargeLandscape = window.matchMedia(
      "(min-width: 851px) and (max-width: 950px) and (orientation: landscape)"
    ).matches;

    const isIPadMiniPortrait = window.matchMedia(
      "(min-width: 768px) and (max-width: 799px) and (orientation: portrait)"
    ).matches;

    if (isMobilePortrait) return 6;
    if (isSmallLandscape) return 6;
    if (isMediumLandscape) return 6;
    if (isLargeLandscape) return 9;
    if (isIPadMiniPortrait) return 9;

    return 12;
  }

  function cardHasSale(card) {
    return Boolean(card.dataset.productOldPrice || card.querySelector(".catalog-sale-price"));
  }

  function getFilteredProducts() {
    let filtered = [...allProductCards];

    if (isBrandsPage && currentBrand === "all") {
      return [];
    }

    if (isPromotionsPage) {
      if (currentFilter === "packages") {
        filtered = filtered.filter((card) => card.dataset.category === "packages");
      } else {
        filtered = filtered.filter(cardHasSale);
        if (currentFilter !== "all" && currentFilter !== "sale") {
          filtered = filtered.filter((card) => card.dataset.category === currentFilter);
        }
      }
    } else if (currentFilter === "sale") {
      filtered = filtered.filter(cardHasSale);
    } else if (currentFilter !== "all") {
      filtered = filtered.filter((card) => card.dataset.category === currentFilter);
    }

    if (currentBrand !== "all") {
      filtered = filtered.filter((card) => card.dataset.productBrandName === currentBrand);
    }

    if (currentSearch.trim() !== "") {
      const searchText = currentSearch.toLowerCase().trim();

      filtered = filtered.filter((card) => {
        const searchableText = `
          ${card.dataset.productName || ""}
          ${card.dataset.productModel || ""}
          ${card.dataset.category || ""}
          ${card.dataset.productCategory || ""}
          ${card.dataset.productFeatures || ""}
        `.toLowerCase();

        return searchableText.includes(searchText);
      });
    }

    if (currentSort === "price-low") {
      filtered.sort((a, b) => parsePublicPrice(a.dataset.productPrice) - parsePublicPrice(b.dataset.productPrice));
    } else if (currentSort === "price-high") {
      filtered.sort((a, b) => parsePublicPrice(b.dataset.productPrice) - parsePublicPrice(a.dataset.productPrice));
    } else if (currentSort === "newest") {
      filtered.reverse();
    } else if (currentSort === "sale") {
      filtered = filtered.filter(cardHasSale);
    }

    return filtered;
  }

  function parsePublicPrice(priceText) {
    const parsed = numericValue(priceText);
    return parsed === null ? Number.MAX_SAFE_INTEGER : parsed;
  }

  function renderProductsPage() {
    const productsPerPage = getProductsPerPage();
    const filteredProducts = getFilteredProducts();
    const totalProducts = filteredProducts.length;
    const brandPromptActive = isBrandsPage && currentBrand === "all";

    document.body.classList.toggle("brands-no-brand", brandPromptActive);

    if (productsSortDropdown) {
      productsSortDropdown.disabled = brandPromptActive;
    }

    if (productsEmptyState) {
      const emptyIcon = productsEmptyState.querySelector("i");
      const emptyTitle = productsEmptyState.querySelector("h3");
      const emptyText = productsEmptyState.querySelector("p");

      if (brandPromptActive) {
        if (emptyIcon) emptyIcon.className = "fa-solid fa-tags";
        if (emptyTitle) emptyTitle.textContent = "Select a brand to view products.";
        if (emptyText) {
          emptyText.textContent = "Choose a brand above, then use All Products or the category buttons to narrow the results.";
        }
      } else {
        if (emptyIcon) emptyIcon.className = "fa-solid fa-magnifying-glass";
        if (emptyTitle) emptyTitle.textContent = "No products found.";
        if (emptyText) emptyText.textContent = "Try another keyword or select a different category.";
      }

      productsEmptyState.classList.toggle("hidden", totalProducts > 0 && !brandPromptActive);
    }

    const totalPages = Math.ceil(totalProducts / productsPerPage);

    if (currentProductsPage >= totalPages) currentProductsPage = 0;
    if (currentProductsPage < 0) currentProductsPage = 0;

    const start = currentProductsPage * productsPerPage;
    const end = start + productsPerPage;

    allProductCards.forEach((card) => {
      card.style.display = "none";
    });

    productsGrid.innerHTML = "";

    filteredProducts.slice(start, end).forEach((card) => {
      card.style.display = "flex";
      productsGrid.appendChild(card);
    });

    if (productsCount) {
      if (brandPromptActive) {
        productsCount.textContent = "Select a brand to view products";
      } else if (totalProducts > 0) {
        productsCount.textContent = `Showing ${start + 1}–${Math.min(end, totalProducts)} of ${totalProducts} products`;
      } else {
        productsCount.textContent = "Showing 0 products";
      }
    }

    productsPageNumbers.innerHTML = "";

    for (let index = 0; index < totalPages; index += 1) {
      const pageBtn = document.createElement("button");
      pageBtn.type = "button";
      pageBtn.className = "product-page-btn";
      pageBtn.textContent = index + 1;

      if (index === currentProductsPage) pageBtn.classList.add("active");

      pageBtn.addEventListener("click", () => {
        currentProductsPage = index;
        renderProductsPage();
        scrollToProductsTop();
      });

      productsPageNumbers.appendChild(pageBtn);
    }

    productsPrevBtn.disabled = currentProductsPage === 0;
    productsNextBtn.disabled = currentProductsPage >= totalPages - 1;
    productsPrevBtn.style.display = totalPages <= 1 ? "none" : "flex";
    productsNextBtn.style.display = totalPages <= 1 ? "none" : "flex";
  }

  function scrollToProductsTop() {
    const productsToolbar = document.querySelector(".products-toolbar");

    if (productsToolbar) {
      productsToolbar.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function setSectionTitle() {
    if (!productsSectionTitle) return;

    if (isBrandsPage && currentBrandLabel) {
      productsSectionTitle.textContent =
        currentFilter === "all"
          ? `${currentBrandLabel} Products`
          : `${currentBrandLabel} ${filterTitles[currentFilter] || "Products"}`;
      return;
    }

    if (isBrandsPage && currentBrand === "all") {
      productsSectionTitle.textContent = "Products per Brand";
      return;
    }

    if (isPromotionsPage && (currentFilter === "all" || currentFilter === "sale")) {
      productsSectionTitle.textContent = "Sale Items";
      return;
    }

    productsSectionTitle.textContent = filterTitles[currentFilter] || "Products";
  }

  function openProductModal(card) {
    const productModalOverlay = document.getElementById("productModalOverlay");
    const modalProductImage = document.getElementById("modalProductImage");
    const modalBrandLogo = document.getElementById("modalBrandLogo");
    const modalProductModel = document.getElementById("modalProductModel");
    const modalProductName = document.getElementById("modalProductName");
    const modalProductCategory = document.getElementById("modalProductCategory");
    const modalStockBadge = document.getElementById("modalStockBadge");
    const modalProductPrice = document.getElementById("modalProductPrice");
    const modalKeyFeatures = document.getElementById("modalKeyFeatures");
    const modalSaleBadge = document.getElementById("modalSaleBadge");

    if (!productModalOverlay || !modalProductImage || !modalBrandLogo || !modalProductModel || !modalProductName || !modalProductCategory || !modalStockBadge || !modalProductPrice || !modalKeyFeatures) return;

    modalProductImage.src = card.dataset.productImage || "";
    modalBrandLogo.src = card.dataset.productBrand || "";
    modalProductModel.textContent = card.dataset.productModel || "";
    modalProductName.textContent = card.dataset.productName || "";
    modalProductCategory.textContent = card.dataset.productCategory || "";

    const currentPrice = card.dataset.productPrice || "";
    const oldPrice = card.dataset.productOldPrice || "";

    if (oldPrice) {
      if (modalSaleBadge) modalSaleBadge.classList.remove("hidden");
      const currentPriceNumber = parsePublicPrice(currentPrice);
      const oldPriceNumber = parsePublicPrice(oldPrice);
      const discountPercent = oldPriceNumber && currentPriceNumber !== Number.MAX_SAFE_INTEGER
        ? Math.max(0, Math.round(((oldPriceNumber - currentPriceNumber) / oldPriceNumber) * 100))
        : 0;

      modalProductPrice.innerHTML = `
        <span class="modal-old-price">${escapeHtml(oldPrice)}</span>
        <span class="modal-sale-price">${escapeHtml(currentPrice)}</span>
        ${discountPercent ? `<span class="modal-discount-badge">${discountPercent}% OFF</span>` : ""}
      `;
    } else {
      if (modalSaleBadge) modalSaleBadge.classList.add("hidden");
      modalProductPrice.innerHTML = `<span class="modal-regular-price">${escapeHtml(currentPrice)}</span>`;
    }

    const stock = Number(card.dataset.productStock || 0);
    const lowQuantity = Number(card.dataset.productLowQuantity || 10);

    modalStockBadge.className = "product-modal-stock";

    if (stock === 0) {
      modalStockBadge.textContent = "Sold Out";
      modalStockBadge.classList.add("sold-out");
    } else if (stock <= lowQuantity) {
      modalStockBadge.textContent = "Low Stock";
      modalStockBadge.classList.add("low-stock");
    } else {
      modalStockBadge.textContent = "In Stock";
      modalStockBadge.classList.add("in-stock");
    }

    modalKeyFeatures.innerHTML = "";
    const features = card.dataset.productFeatures ? card.dataset.productFeatures.split("|") : [];

    features.forEach((feature) => {
      if (!feature.trim()) return;
      const li = document.createElement("li");
      li.innerHTML = `<i class="fa-solid fa-circle-check"></i><span>${escapeHtml(feature.trim())}</span>`;
      modalKeyFeatures.appendChild(li);
    });

    productModalOverlay.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  productsGrid.addEventListener("click", (event) => {
    const clickableArea = event.target.closest(".catalog-product-image, .catalog-product-model, .catalog-product-name");
    if (!clickableArea) return;

    const card = event.target.closest(".catalog-product-card");
    if (!card) return;

    openProductModal(card);
  });

  productsPrevBtn.addEventListener("click", () => {
    if (currentProductsPage > 0) {
      currentProductsPage -= 1;
      renderProductsPage();
      scrollToProductsTop();
    }
  });

  productsNextBtn.addEventListener("click", () => {
    const productsPerPage = getProductsPerPage();
    const totalPages = Math.ceil(getFilteredProducts().length / productsPerPage);

    if (currentProductsPage < totalPages - 1) {
      currentProductsPage += 1;
      renderProductsPage();
      scrollToProductsTop();
    }
  });

  productFilterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (isPromotionsPage && button.dataset.filter === "sale") return;

      if (isBrandsPage && currentBrand === "all") {
        productFilterButtons.forEach((btn) => btn.classList.remove("active"));
        currentFilter = "all";
        currentProductsPage = 0;
        setSectionTitle();
        renderProductsPage();
        return;
      }

      productFilterButtons.forEach((btn) => {
        if (!(isPromotionsPage && btn.dataset.filter === "sale")) btn.classList.remove("active");
      });

      button.classList.add("active");
      currentFilter = button.getAttribute("data-filter") || "all";
      currentProductsPage = 0;
      setSectionTitle();
      renderProductsPage();
    });
  });

  document.querySelectorAll(".brand-strip-row").forEach((row) => {
    row.addEventListener("click", (event) => {
      const item = event.target.closest(".brand-strip-item");
      if (!item) return;

      const selectedBrand = item.dataset.brandFilter || "all";
      const selectedBrandLabel = item.querySelector("img")?.getAttribute("alt") || selectedBrand;
      const isAlreadyActive = item.classList.contains("active");

      document.querySelectorAll(".brand-strip-item").forEach((brand) => brand.classList.remove("active"));

      if (isBrandsPage) {
        productFilterButtons.forEach((btn) => btn.classList.remove("active"));

        if (isAlreadyActive) {
          currentBrand = "all";
          currentBrandLabel = "";
          currentFilter = "all";
        } else {
          item.classList.add("active");
          currentBrand = selectedBrand;
          currentBrandLabel = selectedBrandLabel;
          currentFilter = "all";

          const allProductsButton = Array.from(productFilterButtons).find((btn) => btn.dataset.filter === "all");
          if (allProductsButton) allProductsButton.classList.add("active");
        }

        currentProductsPage = 0;
        setSectionTitle();
        renderProductsPage();
        return;
      }

      if (isAlreadyActive) {
        currentBrand = "all";
      } else {
        item.classList.add("active");
        currentBrand = selectedBrand;
      }

      currentProductsPage = 0;
      renderProductsPage();
    });
  });

  if (productsSearchInput) {
    productsSearchInput.addEventListener("input", () => {
      currentSearch = productsSearchInput.value;
      currentProductsPage = 0;
      renderProductsPage();
    });
  }

  if (productsSortDropdown) {
    productsSortDropdown.addEventListener("change", () => {
      currentSort = productsSortDropdown.value;
      currentProductsPage = 0;
      renderProductsPage();
    });
  }

  let lastProductsPerPage = getProductsPerPage();

  window.addEventListener("resize", () => {
    const currentPerPage = getProductsPerPage();
    if (currentPerPage !== lastProductsPerPage) {
      lastProductsPerPage = currentPerPage;
      renderProductsPage();
    }
  });

  async function loadDynamicCatalogData() {
    productsGrid.innerHTML = `<div class="products-loading-state text-center text-gray-500 py-8">Loading products...</div>`;
    if (productsCount) productsCount.textContent = "Loading products...";

    try {
      const [productsPayload, brandsPayload] = await Promise.all([
        fetchPagedApiItems("/api/products", 50),
        fetchPagedApiItems("/api/brands", 50)
      ]);

      publicProducts = productsPayload;
      publicBrands = brandsPayload.map(normalizeBrand).filter((brand) => brand.key);

      renderBrandStrips();
      await renderPromotionHeroBanners();

      allProductCards = publicProducts.map(renderProductCard);
      productsGrid.innerHTML = "";

      if (isPromotionsPage) currentFilter = "all";
      setSectionTitle();
      renderProductsPage();
    } catch (error) {
      console.error("Unable to load public catalog data from API.", error);
      productsGrid.innerHTML = `
        <div class="products-empty-state">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <h3>Unable to load products.</h3>
          <p>Please refresh the page or try again later.</p>
        </div>
      `;
      if (productsCount) productsCount.textContent = "Unable to load products";
    }
  }

  loadDynamicCatalogData();
}


/* =========================
   DRAG SCROLL - CATEGORY STRIP
========================= */

const categoryStrip = document.querySelector(".products-category-filter");

if (categoryStrip) {
  let isDown = false;
  let startX;
  let scrollLeft;

  categoryStrip.addEventListener("mousedown", (e) => {
    isDown = true;
    categoryStrip.classList.add("dragging");
    startX = e.pageX - categoryStrip.offsetLeft;
    scrollLeft = categoryStrip.scrollLeft;
  });

  categoryStrip.addEventListener("mouseleave", () => {
    isDown = false;
    categoryStrip.classList.remove("dragging");
  });

  categoryStrip.addEventListener("mouseup", () => {
    isDown = false;
    categoryStrip.classList.remove("dragging");
  });

  categoryStrip.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    e.preventDefault();

    const x = e.pageX - categoryStrip.offsetLeft;
    const walk = (x - startX) * 1.5;

    categoryStrip.scrollLeft = scrollLeft - walk;
  });
}

/* =========================
   CATEGORY STRIP ROW BALANCER
========================= */

const categoryFilter = document.querySelector(".products-category-filter");

if (categoryFilter) {
  const categoryButtons = Array.from(
    categoryFilter.querySelectorAll(".product-filter-btn")
  );

  function balanceCategoryRows() {
    const totalCategories = categoryButtons.length;

    categoryFilter.innerHTML = "";

    if (totalCategories <= 15) {
      categoryFilter.classList.remove("two-row");

      categoryButtons.forEach((button) => {
        categoryFilter.appendChild(button);
      });

      return;
    }

    categoryFilter.classList.add("two-row");

    const firstRowCount = Math.ceil(totalCategories / 2);

    const firstRow = categoryButtons.slice(0, firstRowCount);
    const secondRow = categoryButtons.slice(firstRowCount);

    for (let i = 0; i < firstRowCount; i++) {
      if (firstRow[i]) categoryFilter.appendChild(firstRow[i]);
      if (secondRow[i]) categoryFilter.appendChild(secondRow[i]);
    }
  }

  balanceCategoryRows();
}

const categoryScrollWrap = document.querySelector(".products-category-scroll-wrap");
const categoryScrollStrip = document.querySelector(".products-category-filter");
const categoryScrollLeft = document.querySelector(".category-scroll-left");
const categoryScrollRight = document.querySelector(".category-scroll-right");

if (categoryScrollWrap && categoryScrollStrip && categoryScrollLeft && categoryScrollRight) {
  categoryScrollLeft.addEventListener("click", () => {
    categoryScrollStrip.scrollBy({
      left: -260,
      behavior: "smooth"
    });
  });

  categoryScrollRight.addEventListener("click", () => {
    categoryScrollStrip.scrollBy({
      left: 260,
      behavior: "smooth"
    });
  });
}

/* =========================================================
   PRODUCTS / PROMOTIONS BRAND STRIP ARROWS
========================================================= */

const productBrandScrollWraps = document.querySelectorAll(".product-brand-scroll-wrap");

productBrandScrollWraps.forEach((wrap) => {
  const brandStrip = wrap.querySelector(".brand-strip-row");
  const brandScrollLeft = wrap.querySelector(".product-brand-scroll-left");
  const brandScrollRight = wrap.querySelector(".product-brand-scroll-right");

  if (!brandStrip || !brandScrollLeft || !brandScrollRight) return;

  brandScrollLeft.addEventListener("click", () => {
    brandStrip.scrollBy({
      left: -260,
      behavior: "smooth"
    });
  });

  brandScrollRight.addEventListener("click", () => {
    brandStrip.scrollBy({
      left: 260,
      behavior: "smooth"
    });
  });
});

/* =========================
   PRODUCT QUICK VIEW MODAL
========================= */

const productModalOverlay = document.getElementById("productModalOverlay");
const productModalClose = document.getElementById("productModalClose");

const modalProductImage = document.getElementById("modalProductImage");
const modalBrandLogo = document.getElementById("modalBrandLogo");
const modalProductModel = document.getElementById("modalProductModel");
const modalProductName = document.getElementById("modalProductName");
const modalProductCategory = document.getElementById("modalProductCategory");
const modalStockBadge = document.getElementById("modalStockBadge");
const modalProductPrice = document.getElementById("modalProductPrice");
const modalKeyFeatures = document.getElementById("modalKeyFeatures");
const modalSaleBadge = document.getElementById("modalSaleBadge");

const productCards = document.querySelectorAll(".catalog-product-card");

function parsePrice(priceText) {
  return Number(String(priceText).replace(/[₱,\s]/g, ""));
}

if (
  productModalOverlay &&
  productModalClose &&
  modalProductImage &&
  modalBrandLogo &&
  modalProductModel &&
  modalProductName &&
  modalProductCategory &&
  modalStockBadge &&
  modalProductPrice &&
  modalKeyFeatures
) {
  productCards.forEach((card) => {
    const clickableAreas = [
      card.querySelector(".catalog-product-image"),
      card.querySelector(".catalog-product-model"),
      card.querySelector(".catalog-product-name")
    ];

    clickableAreas.forEach((area) => {
      if (!area) return;

      area.addEventListener("click", () => {
        modalProductImage.src = card.dataset.productImage || "";
        modalBrandLogo.src = card.dataset.productBrand || "";

        modalProductModel.textContent = card.dataset.productModel || "";
        modalProductName.textContent = card.dataset.productName || "";
        modalProductCategory.textContent = card.dataset.productCategory || "";

        const currentPrice = card.dataset.productPrice || "";
        const oldPrice = card.dataset.productOldPrice || "";

        if (oldPrice) {
          const currentPriceNumber = parsePrice(currentPrice);
          const oldPriceNumber = parsePrice(oldPrice);

          if (modalSaleBadge) {
            modalSaleBadge.classList.remove("hidden");
          }

          const discountPercent = Math.round(
            ((oldPriceNumber - currentPriceNumber) / oldPriceNumber) * 100
          );

          modalProductPrice.innerHTML = `
            <span class="modal-old-price">${oldPrice}</span>
            <span class="modal-sale-price">${currentPrice}</span>
            <span class="modal-discount-badge">${discountPercent}% OFF</span>
          `;
        } else {
          if (modalSaleBadge) {
            modalSaleBadge.classList.add("hidden");
          }

          modalProductPrice.innerHTML = `
            <span class="modal-regular-price">${currentPrice}</span>
          `;
        }

        const stock = Number(card.dataset.productStock || 0);
        const lowQuantity = Number(card.dataset.productLowQuantity || 10);

        modalStockBadge.className = "product-modal-stock";

        if (stock === 0) {
          modalStockBadge.textContent = "Sold Out";
          modalStockBadge.classList.add("sold-out");
        } else if (stock <= lowQuantity) {
          modalStockBadge.textContent = "Low Stock";
          modalStockBadge.classList.add("low-stock");
        } else {
          modalStockBadge.textContent = "In Stock";
          modalStockBadge.classList.add("in-stock");
        }

        modalKeyFeatures.innerHTML = "";

        const features = card.dataset.productFeatures
          ? card.dataset.productFeatures.split("|")
          : [];

        features.forEach((feature) => {
          const li = document.createElement("li");

          li.innerHTML = `
            <i class="fa-solid fa-circle-check"></i>
            <span>${feature.trim()}</span>
          `;

          modalKeyFeatures.appendChild(li);
        });

        productModalOverlay.classList.remove("hidden");
        document.body.style.overflow = "hidden";
      });
    });
  });

  function closeProductModal() {
    productModalOverlay.classList.add("hidden");
    document.body.style.overflow = "";
  }

  productModalClose.addEventListener("click", closeProductModal);

  productModalOverlay.addEventListener("click", (e) => {
    if (e.target === productModalOverlay) {
      closeProductModal();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (
      e.key === "Escape" &&
      !productModalOverlay.classList.contains("hidden")
    ) {
        closeProductModal();
    }
  });
}
/* =========================
   BRANDS PAGE BRAND STRIP
========================= */

const brandsPageStrip = document.getElementById("brandsPageStrip");
const brandScrollLeft = document.querySelector(".brand-scroll-left");
const brandScrollRight = document.querySelector(".brand-scroll-right");

if (brandsPageStrip) {
  const brandStripItems = Array.from(
    brandsPageStrip.querySelectorAll(".brand-strip-item")
  );

  function balanceBrandRows() {
    const totalBrands = brandStripItems.length;

    brandsPageStrip.innerHTML = "";

    if (totalBrands <= 15) {
      brandsPageStrip.classList.remove("two-row");

      brandStripItems.forEach((brand) => {
        brandsPageStrip.appendChild(brand);
      });

      return;
    }

    brandsPageStrip.classList.add("two-row");

    const firstRowCount = Math.ceil(totalBrands / 2);
    const firstRow = brandStripItems.slice(0, firstRowCount);
    const secondRow = brandStripItems.slice(firstRowCount);

    for (let i = 0; i < firstRowCount; i++) {
      if (firstRow[i]) brandsPageStrip.appendChild(firstRow[i]);
      if (secondRow[i]) brandsPageStrip.appendChild(secondRow[i]);
    }
  }

  balanceBrandRows();

  if (brandScrollLeft && brandScrollRight) {
    brandScrollLeft.addEventListener("click", () => {
      brandsPageStrip.scrollBy({
        left: -300,
        behavior: "smooth"
      });
    });

    brandScrollRight.addEventListener("click", () => {
      brandsPageStrip.scrollBy({
        left: 300,
        behavior: "smooth"
      });
    });
  }
}

/* =========================
   DRAG SCROLL - BRANDS STRIP
========================= */

const brandsStrip = document.getElementById("brandsPageStrip");

if (brandsStrip) {
  let isBrandDragging = false;
  let brandStartX = 0;
  let brandScrollStart = 0;
  let brandHasMoved = false;

  brandsStrip.addEventListener("mousedown", (event) => {
    isBrandDragging = true;
    brandHasMoved = false;
    brandStartX = event.pageX;
    brandScrollStart = brandsStrip.scrollLeft;
    brandsStrip.classList.add("dragging");
  });

  brandsStrip.addEventListener("mousemove", (event) => {
    if (!isBrandDragging) return;

    const moveX = event.pageX - brandStartX;

    if (Math.abs(moveX) > 5) {
      brandHasMoved = true;
      event.preventDefault();
      brandsStrip.scrollLeft = brandScrollStart - moveX;
    }
  });

  brandsStrip.addEventListener("mouseup", () => {
    isBrandDragging = false;
    brandsStrip.classList.remove("dragging");
  });

  brandsStrip.addEventListener("mouseleave", () => {
    isBrandDragging = false;
    brandsStrip.classList.remove("dragging");
  });

  brandsStrip.addEventListener("click", (event) => {
    if (brandHasMoved) {
      event.preventDefault();
      event.stopPropagation();
    }
  });
}
/* =========================================================
   About Page Why Choose Mobile Swipe Controls
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".about-why-mobile-carousel");
  const grid = document.querySelector(".about-mobile-swipe-grid");
  const prevBtn = document.querySelector(".about-mobile-carousel-prev");
  const nextBtn = document.querySelector(".about-mobile-carousel-next");

  if (!carousel || !grid || !prevBtn || !nextBtn) return;

  function isMobileView() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function updateButtons() {
    if (!isMobileView()) {
      prevBtn.classList.add("is-hidden");
      nextBtn.classList.add("is-hidden");
      return;
    }

    const maxScrollLeft = grid.scrollWidth - grid.clientWidth;
    const currentScrollLeft = grid.scrollLeft;

    if (currentScrollLeft <= 10) {
      prevBtn.classList.add("is-hidden");
    } else {
      prevBtn.classList.remove("is-hidden");
    }

    if (currentScrollLeft >= maxScrollLeft - 10) {
      nextBtn.classList.add("is-hidden");
    } else {
      nextBtn.classList.remove("is-hidden");
    }
  }

  nextBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: grid.clientWidth,
      behavior: "smooth"
    });
  });

  prevBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: -grid.clientWidth,
      behavior: "smooth"
    });
  });

  grid.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});
/* =========================================================
   About Page Project Gallery Mobile Swipe Controls
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".about-gallery-mobile-carousel");
  const grid = document.querySelector(".about-gallery-swipe-grid");
  const prevBtn = document.querySelector(".about-gallery-carousel-prev");
  const nextBtn = document.querySelector(".about-gallery-carousel-next");

  if (!carousel || !grid || !prevBtn || !nextBtn) return;

  function isMobileView() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function updateButtons() {
    if (!isMobileView()) {
      prevBtn.classList.add("is-hidden");
      nextBtn.classList.add("is-hidden");
      return;
    }

    const maxScrollLeft = grid.scrollWidth - grid.clientWidth;
    const currentScrollLeft = grid.scrollLeft;

    if (currentScrollLeft <= 10) {
      prevBtn.classList.add("is-hidden");
    } else {
      prevBtn.classList.remove("is-hidden");
    }

    if (currentScrollLeft >= maxScrollLeft - 10) {
      nextBtn.classList.add("is-hidden");
    } else {
      nextBtn.classList.remove("is-hidden");
    }
  }

  nextBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: grid.clientWidth,
      behavior: "smooth"
    });
  });

  prevBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: -grid.clientWidth,
      behavior: "smooth"
    });
  });

  grid.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});

/* =========================================================
   Services Page Mobile Swipe Controls
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".services-mobile-carousel");
  const grid = document.querySelector(".services-mobile-swipe-grid");
  const prevBtn = document.querySelector(".services-carousel-prev");
  const nextBtn = document.querySelector(".services-carousel-next");

  if (!carousel || !grid || !prevBtn || !nextBtn) return;

  function isMobileView() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function updateButtons() {
    if (!isMobileView()) {
      prevBtn.classList.add("is-hidden");
      nextBtn.classList.add("is-hidden");
      return;
    }

    const maxScrollLeft = grid.scrollWidth - grid.clientWidth;
    const currentScrollLeft = grid.scrollLeft;

    if (currentScrollLeft <= 10) {
      prevBtn.classList.add("is-hidden");
    } else {
      prevBtn.classList.remove("is-hidden");
    }

    if (currentScrollLeft >= maxScrollLeft - 10) {
      nextBtn.classList.add("is-hidden");
    } else {
      nextBtn.classList.remove("is-hidden");
    }
  }

  nextBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: grid.clientWidth,
      behavior: "smooth"
    });
  });

  prevBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: -grid.clientWidth,
      behavior: "smooth"
    });
  });

  grid.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});
/* =========================================================
   Homepage Services Preview Mobile Swipe Controls
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".home-services-mobile-carousel");
  const grid = document.querySelector(".home-services-preview-grid");
  const prevBtn = document.querySelector(".home-services-carousel-prev");
  const nextBtn = document.querySelector(".home-services-carousel-next");

  if (!carousel || !grid || !prevBtn || !nextBtn) return;

  function isMobileView() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function updateButtons() {
    if (!isMobileView()) {
      prevBtn.classList.add("is-hidden");
      nextBtn.classList.add("is-hidden");
      return;
    }

    const maxScrollLeft = grid.scrollWidth - grid.clientWidth;
    const currentScrollLeft = grid.scrollLeft;

    if (currentScrollLeft <= 10) {
      prevBtn.classList.add("is-hidden");
    } else {
      prevBtn.classList.remove("is-hidden");
    }

    if (currentScrollLeft >= maxScrollLeft - 10) {
      nextBtn.classList.add("is-hidden");
    } else {
      nextBtn.classList.remove("is-hidden");
    }
  }

  nextBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: grid.clientWidth,
      behavior: "smooth"
    });
  });

  prevBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: -grid.clientWidth,
      behavior: "smooth"
    });
  });

  grid.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});
/* =========================================================
   Contact Page Other Ways Mobile Swipe Controls
========================================================= */

document.addEventListener("DOMContentLoaded", function () {
  const carousel = document.querySelector(".contact-channel-mobile-carousel");
  const grid = document.querySelector(".contact-channel-swipe-grid");
  const prevBtn = document.querySelector(".contact-channel-carousel-prev");
  const nextBtn = document.querySelector(".contact-channel-carousel-next");

  if (!carousel || !grid || !prevBtn || !nextBtn) return;

  function isMobileView() {
    return window.matchMedia("(max-width: 767px)").matches;
  }

  function updateButtons() {
    if (!isMobileView()) {
      prevBtn.classList.add("is-hidden");
      nextBtn.classList.add("is-hidden");
      return;
    }

    const maxScrollLeft = grid.scrollWidth - grid.clientWidth;
    const currentScrollLeft = grid.scrollLeft;

    if (currentScrollLeft <= 10) {
      prevBtn.classList.add("is-hidden");
    } else {
      prevBtn.classList.remove("is-hidden");
    }

    if (currentScrollLeft >= maxScrollLeft - 10) {
      nextBtn.classList.add("is-hidden");
    } else {
      nextBtn.classList.remove("is-hidden");
    }
  }

  nextBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: grid.clientWidth,
      behavior: "smooth"
    });
  });

  prevBtn.addEventListener("click", function () {
    grid.scrollBy({
      left: -grid.clientWidth,
      behavior: "smooth"
    });
  });

  grid.addEventListener("scroll", updateButtons);
  window.addEventListener("resize", updateButtons);

  updateButtons();
});
