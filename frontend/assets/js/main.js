/* batch58-image-lazy-loading: non-critical rendered images use loading="lazy" and decoding="async". */
const RSA_PUBLIC_CATALOG_DYNAMIC_VERSION = "batch59c-hotfix-v2-public-category-strip-only";
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
let productFilterButtons = Array.from(document.querySelectorAll(".product-filter-btn"));
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
      <div class="catalog-product-image"><img loading="lazy" decoding="async" src="${escapeHtml(normalized.imagePath)}" alt="${escapeHtml(normalized.name)}"></div>
      <span class="catalog-stock-badge ${stockClass}">${stockLabel}</span>
      <img loading="lazy" decoding="async" class="catalog-brand-logo" src="${escapeHtml(normalized.brandLogoPath)}" alt="${escapeHtml(normalized.brandName)}">
      <p class="catalog-product-model">${escapeHtml(normalized.model)}</p>
      <h3 class="catalog-product-name">${escapeHtml(normalized.name)}</h3>
      <p class="catalog-product-subcategory">${escapeHtml(normalized.categoryName)}</p>
      ${hasSale
        ? `<div class="catalog-price-row"><span class="catalog-old-price">${escapeHtml(normalized.oldPrice)}</span><span class="catalog-sale-price">${escapeHtml(normalized.salePrice)}</span></div>`
        : `<p class="catalog-product-price">${escapeHtml(normalized.price)}</p>`}
    `;

    return card;
  }

  /* batch59c-hotfix-v2-public-category-strip-only:
     Only the public category button strip is hydrated from /api/categories.
     Existing product/brand loading, pagination, modal, and promotions hero logic stay unchanged. */
  function isPublicCategoryVisible(category) {
    const flag = String(category && category.show_flag !== undefined ? category.show_flag : "Y").trim().toUpperCase();
    return flag !== "N" && flag !== "FALSE" && flag !== "0";
  }

  function normalizePublicCategory(category) {
    const name = firstNonEmpty(category.category_name, category.name, category.title, category.category_key);
    const key = slugify(firstNonEmpty(category.category_key, category.key, name));
    const icon = firstNonEmpty(category.icon_code, "fa-solid fa-folder");
    const displaySeq = numericValue(firstNonEmpty(category.display_seq, category.display_order, category.sort_order)) ?? 9999;

    return {
      key,
      name: firstNonEmpty(name, key),
      icon,
      displaySeq
    };
  }

  function publicCategoryButtonHtml(filter, label, iconClass, extraClass = "") {
    const classes = ["product-filter-btn", extraClass].filter(Boolean).join(" ");
    return `<button class="${escapeHtml(classes)}" data-filter="${escapeHtml(filter)}"><i class="${escapeHtml(iconClass)}"></i>${escapeHtml(label)}</button>`;
  }

  function balancePublicCategoryStrip(categoryFilterElement) {
    if (!categoryFilterElement) return;

    const buttons = Array.from(categoryFilterElement.querySelectorAll(".product-filter-btn"));
    categoryFilterElement.innerHTML = "";

    if (buttons.length <= 15) {
      categoryFilterElement.classList.remove("two-row");
      buttons.forEach((button) => categoryFilterElement.appendChild(button));
      return;
    }

    categoryFilterElement.classList.add("two-row");
    const firstRowCount = Math.ceil(buttons.length / 2);
    const firstRow = buttons.slice(0, firstRowCount);
    const secondRow = buttons.slice(firstRowCount);

    for (let index = 0; index < firstRowCount; index += 1) {
      if (firstRow[index]) categoryFilterElement.appendChild(firstRow[index]);
      if (secondRow[index]) categoryFilterElement.appendChild(secondRow[index]);
    }
  }

  async function renderPublicCategoryStripFromApi() {
    const categoryFilterElement = document.querySelector(".products-category-filter");
    if (!categoryFilterElement) return;

    let categoryRecords = [];

    try {
      categoryRecords = await fetchPagedApiItems("/api/categories", 50);
    } catch (error) {
      console.warn("Unable to load public categories from API. Keeping static category buttons.", error);
      return;
    }

    const categories = categoryRecords
      .filter(isPublicCategoryVisible)
      .map(normalizePublicCategory)
      .filter((category) => category.key)
      .sort((a, b) => a.displaySeq - b.displaySeq || a.name.localeCompare(b.name));

    if (!categories.length) return;

    categories.forEach((category) => {
      filterTitles[category.key] = category.name;
    });

    const categoryButtonsHtml = categories
      .map((category) => publicCategoryButtonHtml(category.key, category.name, category.icon))
      .join("");

    if (isPromotionsPage) {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large"),
        publicCategoryButtonHtml("sale", "Sale", "fa-solid fa-tag", "active promo-sale-locked"),
        categoryButtonsHtml
      ].join("");
    } else if (isBrandsPage) {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large"),
        categoryButtonsHtml
      ].join("");
    } else {
      categoryFilterElement.innerHTML = [
        publicCategoryButtonHtml("all", "All Products", "fa-solid fa-table-cells-large", currentFilter === "all" ? "active" : ""),
        publicCategoryButtonHtml("sale", "Sale", "fa-solid fa-tag", currentFilter === "sale" ? "active" : ""),
        categoryButtonsHtml
      ].join("");
    }

    productFilterButtons = Array.from(categoryFilterElement.querySelectorAll(".product-filter-btn"));

    const allowedFilters = new Set(productFilterButtons.map((button) => button.dataset.filter || "all"));
    if (!allowedFilters.has(currentFilter)) {
      currentFilter = "all";
    }

    balancePublicCategoryStrip(categoryFilterElement);
    bindProductFilterButtons();
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

/* batch56d-promotions-hero-promoted-packages-only: Promotions hero uses package products with show_pack_flag=Y. */
  async function renderPromotionHeroBanners(products = []) {
    if (!isPromotionsPage) return;

    const heroGrid = document.querySelector(".promotions-hero-grid");
    if (!heroGrid) return;

    function isYesFlag(value) {
      return String(value || "").trim().toUpperCase() === "Y";
    }

    function isPromotedPackageProduct(product) {
      const normalized = normalizeProduct(product);
      const categoryText = String(firstNonEmpty(
        product.category_key,
        product.category_name,
        product.product_category_key,
        product.product_category,
        product.category,
        product.subcategory,
        product.subcategory_key,
        normalized.categoryKey
      )).toLowerCase();

      const isPackageCategory =
        normalized.categoryKey === "packages" ||
        normalized.categoryKey === "packages-kits" ||
        categoryText.includes("package") ||
        categoryText.includes("kit");

      return isPackageCategory && isYesFlag(product.show_pack_flag);
    }

    function renderHeroItems(records) {
      heroGrid.innerHTML = "";
      records.slice(0, 3).forEach((record, index) => {
        const normalized = normalizeProduct(record);
        const imagePath = normalizeAssetPath(
          firstNonEmpty(record.image_path, record.product_image_path, record.banner_image_path, record.image_url, record.product_image, normalized.imagePath),
          "./assets/images/rsa-logo.png"
        );
        const title = firstNonEmpty(record.product_name, record.title, record.name, normalized.name, `Promo Package ${index + 1}`);
        const item = document.createElement("div");
        item.className = "promotions-hero-banner";
        item.dataset.rsaBatch56d = "promoted-packages-only";
        item.innerHTML = `<img src="${escapeHtml(imagePath)}" alt="${escapeHtml(title)}">`;
        heroGrid.appendChild(item);
      });
    }

    const promotedPackages = products
      .filter(isPromotedPackageProduct)
      .sort((a, b) => Number(a.display_seq || 9999) - Number(b.display_seq || 9999));

    if (promotedPackages.length) {
      renderHeroItems(promotedPackages);
      return;
    }

    heroGrid.innerHTML = `<div class="rsa-cms-loading-state">No promoted package products available.</div>`;
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

  function bindProductFilterButtons() {
    productFilterButtons = Array.from(document.querySelectorAll(".product-filter-btn"));

    productFilterButtons.forEach((button) => {
      if (button.dataset.rsaBatch59cV2Bound === "true") return;
      button.dataset.rsaBatch59cV2Bound = "true";

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
  }

  bindProductFilterButtons();

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
      await renderPublicCategoryStripFromApi();
      await renderPromotionHeroBanners(publicProducts);

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

/* =========================================================
   BATCH 50 - PUBLIC CMS + LEAD PAGE API BINDING
   - Homepage dynamic products/brands/services
   - About page content/gallery
   - Services page cards
   - Contact page content/persons/socials + inquiry form
   - Booking page contact helpers + booking form
========================================================= */
(function rsaPublicCmsLeadBinding(global) {
  "use strict";

  if (global.RSA_PUBLIC_CMS_LEAD_VERSION === "batch50-public-cms-lead-api-binding") return;
  global.RSA_PUBLIC_CMS_LEAD_VERSION = "batch50-public-cms-lead-api-binding";

  const document = global.document;
  const PHP_LOCALE = "en-PH";
  const DEFAULT_LOGO = "./assets/images/rsa-logo.png";
  const DEFAULT_CONTACT_IMAGE = "./assets/images/contact/profile-placeholder.svg";

  function getApiBaseUrl() {
    if (global.RSA_API_BASE_URL) return String(global.RSA_API_BASE_URL).replace(/\/$/, "");
    if (global.RSA_API_CONFIG && global.RSA_API_CONFIG.baseUrl) {
      return String(global.RSA_API_CONFIG.baseUrl).replace(/\/$/, "");
    }
    if (global.location.protocol === "file:") return "http://127.0.0.1:8000";
    return "";
  }

  function apiUrl(path) {
    return `${getApiBaseUrl()}${path}`;
  }

  async function fetchJson(path) {
    const response = await fetch(apiUrl(path), {
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`);
    return response.json();
  }

  async function postJson(path, payload) {
    const response = await fetch(apiUrl(path), {
      method: "POST",
      headers: { "Accept": "application/json", "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    let body = null;
    try { body = await response.json(); } catch (_error) { body = null; }
    if (!response.ok) {
      const detail = body && body.detail ? JSON.stringify(body.detail) : `HTTP ${response.status}`;
      throw new Error(detail);
    }
    return body || {};
  }

  function extractItems(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return [];
    for (const key of ["items", "data", "products", "brands", "services", "project_gallery", "contact_persons", "social_media", "results", "records", "rows"]) {
      if (Array.isArray(payload[key])) return payload[key];
    }
    if (payload.body) return extractItems(payload.body);
    return [];
  }

  async function fetchPagedApiItems(path, perPage = 50) {
    const safePerPage = Math.min(Math.max(Number(perPage) || 50, 1), 50);
    const separator = path.includes("?") ? "&" : "?";
    const firstPayload = await fetchJson(`${path}${separator}page=1&per_page=${safePerPage}`);
    const firstItems = extractItems(firstPayload);
    const totalPages = Number(firstPayload && firstPayload.total_pages ? firstPayload.total_pages : 1);
    if (!Number.isFinite(totalPages) || totalPages <= 1) return firstItems;

    const remainingRequests = [];
    for (let page = 2; page <= totalPages; page += 1) {
      remainingRequests.push(fetchJson(`${path}${separator}page=${page}&per_page=${safePerPage}`));
    }
    const remainingPayloads = await Promise.all(remainingRequests);
    return firstItems.concat(...remainingPayloads.map(extractItems));
  }

  function firstNonEmpty(...values) {
    for (const value of values) {
      if (value !== undefined && value !== null && String(value).trim() !== "") return value;
    }
    return "";
  }

  function escapeHtml(value) {
    return String(value === undefined || value === null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function normalizeSpaces(value) {
    return String(value === undefined || value === null ? "" : value).replace(/\s+/g, " ").trim();
  }

  function slugify(value) {
    return String(value || "")
      .toLowerCase()
      .trim()
      .replace(/&/g, "and")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function normalizeAssetPath(pathValue, fallback = DEFAULT_LOGO) {
    const value = String(pathValue || "").trim();
    if (!value) return fallback;
    if (/^(https?:)?\/\//i.test(value) || value.startsWith("data:") || value.startsWith("/")) return value;
    if (value.startsWith("./")) return value;
    if (value.startsWith("assets/") || value.startsWith("uploads/")) return `./${value}`;
    if (value.includes("/")) return `./${value.replace(/^\/+/, "")}`;
    return fallback;
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
    return `₱${parsed.toLocaleString(PHP_LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  function looksShown(record) {
    const flag = String(record && record.show_flag !== undefined ? record.show_flag : "Y").toUpperCase();
    return flag !== "N" && flag !== "FALSE" && flag !== "0";
  }

  function sortByDisplaySeq(a, b) {
    return (Number(a.display_seq || 0) - Number(b.display_seq || 0));
  }

  function serviceIconClass(service) {
    const title = String(service.service_title || service.title || service.name || "").toLowerCase();
    if (service.icon_code) return service.icon_code;
    if (title.includes("maintenance") || title.includes("repair") || title.includes("troubleshoot")) return "fa-solid fa-screwdriver-wrench";
    if (title.includes("mobile") || title.includes("view")) return "fa-solid fa-mobile-screen-button";
    if (title.includes("network") || title.includes("cabling") || title.includes("data")) return "fa-solid fa-network-wired";
    if (title.includes("power")) return "fa-solid fa-bolt";
    if (title.includes("biometric") || title.includes("lock")) return "fa-solid fa-fingerprint";
    if (title.includes("alarm") || title.includes("door")) return "fa-solid fa-bell";
    if (title.includes("hidden")) return "fa-solid fa-eye";
    if (title.includes("fire") || title.includes("fdas")) return "fa-solid fa-fire-extinguisher";
    if (title.includes("computer")) return "fa-solid fa-computer";
    if (title.includes("storage") || title.includes("recorder")) return "fa-solid fa-hard-drive";
    return "fa-solid fa-video";
  }

  function socialIconClass(record) {
    const platform = String(record.platform_key || record.platform_name || "").toLowerCase();
    if (record.icon_code) return record.icon_code;
    if (platform.includes("facebook")) return "fa-brands fa-square-facebook";
    if (platform.includes("instagram")) return "fa-brands fa-instagram";
    if (platform.includes("youtube")) return "fa-brands fa-youtube";
    if (platform.includes("viber")) return "fa-brands fa-viber";
    if (platform.includes("whatsapp")) return "fa-brands fa-whatsapp";
    return "fa-solid fa-link";
  }

  function productFeatures(product) {
    const features = [];
    for (let index = 1; index <= 10; index += 1) {
      const value = firstNonEmpty(product[`feature_${String(index).padStart(2, "0")}`], product[`feature_${index}`]);
      if (value) features.push(String(value));
    }
    return features;
  }

  function normalizeProduct(product) {
    const sale = firstNonEmpty(product.sale_price, product.promo_price, product.discount_price);
    const hasSale = sale !== "" && sale !== null && sale !== undefined;
    const price = firstNonEmpty(product.price, product.regular_price, product.product_price);
    return {
      id: firstNonEmpty(product.product_id, product.id),
      name: firstNonEmpty(product.product_name, product.name, product.title, "Unnamed Product"),
      model: firstNonEmpty(product.product_model, product.model, product.sku),
      categoryKey: slugify(firstNonEmpty(product.category_key, product.product_category_key, product.category_name, product.category)),
      categoryName: firstNonEmpty(product.subcategory, product.category_name, product.product_category, product.category_key),
      brandKey: slugify(firstNonEmpty(product.product_brand_key, product.brand_key, product.product_brand_name, product.brand_name)),
      brandName: firstNonEmpty(product.product_brand_name, product.brand_name, product.product_brand_key, "RSA"),
      imagePath: normalizeAssetPath(firstNonEmpty(product.image_path, product.product_image_path, product.image_url, product.product_image), DEFAULT_LOGO),
      brandLogoPath: normalizeAssetPath(firstNonEmpty(product.brand_logo_path, product.logo_path, product.product_brand_logo_path), DEFAULT_LOGO),
      price: formatPrice(hasSale ? sale : price),
      oldPrice: hasSale ? formatPrice(price, "") : "",
      salePrice: hasSale ? formatPrice(sale, "") : "",
      hasSale,
      showPack: String(product.show_pack_flag || "N").toUpperCase() === "Y",
      features: productFeatures(product)
    };
  }

  function normalizeBrand(brand) {
    const name = firstNonEmpty(brand.brand_name, brand.name, brand.title, brand.brand_key);
    return {
      key: slugify(firstNonEmpty(brand.brand_key, name)),
      name: firstNonEmpty(name, "Brand"),
      logo: normalizeAssetPath(firstNonEmpty(brand.brand_logo_path, brand.logo_path, brand.image_path, brand.image_url), DEFAULT_LOGO)
    };
  }

  function normalizeService(service) {
    return {
      title: firstNonEmpty(service.service_title, service.title, service.name, "Service"),
      shortDescription: firstNonEmpty(service.short_description, service.description, service.service_description, "Professional CCTV and security support."),
      description: firstNonEmpty(service.service_description, service.short_description, service.description, "Professional CCTV and security support."),
      ctaLabel: firstNonEmpty(service.cta_label, "Learn More"),
      ctaUrl: firstNonEmpty(service.cta_url, "booking.html"),
      iconClass: serviceIconClass(service)
    };
  }

  function setText(selector, value) {
    const element = document.querySelector(selector);
    if (element && value) element.textContent = value;
  }

  function setHtml(selector, value) {
    const element = document.querySelector(selector);
    if (element && value) element.innerHTML = value;
  }

  function heroTitleHtml(title, fallback) {
    const text = normalizeSpaces(title || fallback);
    if (!text) return "";
    const parts = text.split(/\s+-\s+|:\s+|,\s+/);
    if (parts.length > 1) {
      return `${escapeHtml(parts[0])}<br><span>${escapeHtml(parts.slice(1).join(" "))}</span>`;
    }
    const words = text.split(" ");
    if (words.length > 4) {
      const first = words.slice(0, 4).join(" ");
      const rest = words.slice(4).join(" ");
      return `${escapeHtml(first)}<br><span>${escapeHtml(rest)}</span>`;
    }
    return `<span>${escapeHtml(text)}</span>`;
  }

  function renderFeaturedCard(product) {
    const p = normalizeProduct(product);
    return `
      <div class="featured-product-card">
        <div class="featured-product-image"><img loading="lazy" decoding="async" src="${escapeHtml(p.imagePath)}" alt="${escapeHtml(p.name)}"></div>
        <p class="featured-product-name text-sm font-black">${escapeHtml(p.name)}</p>
        <p class="text-gray-500 text-xs">${escapeHtml(p.categoryName)}</p>
        <p class="text-red-700 font-black text-base">${escapeHtml(p.price)}</p>
      </div>`;
  }

  function renderPromoCard(product) {
    const p = normalizeProduct(product);
    return `
      <div class="promo-product-card">
        <span class="promo-sale-badge">SALE</span>
        <div class="promo-product-image"><img loading="lazy" decoding="async" src="${escapeHtml(p.imagePath)}" alt="${escapeHtml(p.name)}"></div>
        <p class="promo-product-name text-sm font-black">${escapeHtml(p.name)}</p>
        <p class="text-gray-500 text-xs">${escapeHtml(p.categoryName)}</p>
        ${p.oldPrice ? `<p class="promo-old-price">${escapeHtml(p.oldPrice)}</p>` : ""}
        <p class="promo-sale-price">${escapeHtml(p.salePrice || p.price)}</p>
      </div>`;
  }

  function renderPackageCard(product) {
    const p = normalizeProduct(product);
    return `<a href="promotions.html" class="package-banner-card"><img src="${escapeHtml(p.imagePath)}" alt="${escapeHtml(p.name)}"></a>`;
  }

  function renderBrandCard(brand) {
    const b = normalizeBrand(brand);
    return `<div class="home-brand-item"><div class="home-brand-logo-box"><img loading="lazy" decoding="async" src="${escapeHtml(b.logo)}" alt="${escapeHtml(b.name)}"></div></div>`;
  }

  function renderHomeServiceCard(service) {
    const s = normalizeService(service);
    return `
      <a href="services.html" class="home-service-preview-card">
        <div class="home-service-preview-icon"><i class="${escapeHtml(s.iconClass)}"></i></div>
        <h3>${escapeHtml(s.title)}</h3>
      </a>`;
  }

  function renderServicesPageCard(service) {
    const s = normalizeService(service);
    return `
      <article class="services-page-card">
        <div class="services-page-card-icon"><i class="${escapeHtml(s.iconClass)}"></i></div>
        <div>
          <h3>${escapeHtml(s.title)}</h3>
          <p>${escapeHtml(s.description)}</p>
          ${s.ctaUrl ? `<a href="${escapeHtml(s.ctaUrl)}">${escapeHtml(s.ctaLabel)} <i class="fa-solid fa-arrow-right"></i></a>` : ""}
        </div>
      </article>`;
  }

  /* batch60c-1-public-polish: restore static-era swipe pagination for dynamic homepage sections. */
  function bindSwipePagination(element, callbacks) {
    if (!element || element.dataset.rsaBatch60cSwipeBound === "true") return;

    let startX = 0;
    let startY = 0;

    element.dataset.rsaBatch60cSwipeBound = "true";

    element.addEventListener("touchstart", (event) => {
      if (!event.touches || !event.touches.length) return;
      const touch = event.touches[0];
      startX = touch.clientX;
      startY = touch.clientY;
    }, { passive: true });

    element.addEventListener("touchend", (event) => {
      if (!event.changedTouches || !event.changedTouches.length) return;
      const touch = event.changedTouches[0];
      const distanceX = startX - touch.clientX;
      const distanceY = startY - touch.clientY;

      if (Math.abs(distanceX) < 40) return;
      if (Math.abs(distanceX) < Math.abs(distanceY) * 1.1) return;

      if (distanceX > 0 && callbacks && typeof callbacks.next === "function") {
        callbacks.next();
      } else if (distanceX < 0 && callbacks && typeof callbacks.prev === "function") {
        callbacks.prev();
      }
    }, { passive: true });
  }

  function setupPagedDisplay(config) {
    const container = typeof config.container === "string" ? document.querySelector(config.container) : config.container;
    const dots = typeof config.dots === "string" ? document.querySelector(config.dots) : config.dots;
    const prev = typeof config.prev === "string" ? document.querySelector(config.prev) : config.prev;
    const next = typeof config.next === "string" ? document.querySelector(config.next) : config.next;
    if (!container || !dots) return;

    let currentPage = 0;
    const display = config.display || "grid";

    function perPage() {
      if (config.perPage) return config.perPage();
      return global.matchMedia("(max-width: 767px) and (orientation: portrait)").matches ? (config.mobile || 6) : (config.desktop || 5);
    }

    function render() {
      const items = Array.from(container.querySelectorAll(config.itemSelector));
      const pageSize = perPage();
      const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
      currentPage = Math.min(Math.max(0, currentPage), totalPages - 1);
      const start = currentPage * pageSize;
      const end = start + pageSize;

      items.forEach((item, index) => {
        item.style.display = index >= start && index < end ? display : "none";
      });

      dots.innerHTML = "";
      if (items.length > pageSize) {
        for (let index = 0; index < totalPages; index += 1) {
          const dot = document.createElement("button");
          dot.type = "button";
          dot.className = config.dotClass || "featured-dot";
          if (index === currentPage) dot.classList.add("active");
          dot.addEventListener("click", () => { currentPage = index; render(); });
          dots.appendChild(dot);
        }
      }

      if (prev) prev.classList.toggle("is-hidden", currentPage <= 0 || totalPages <= 1);
      if (next) next.classList.toggle("is-hidden", currentPage >= totalPages - 1 || totalPages <= 1);
    }

    if (prev && prev.dataset.rsaBatch50Bound !== "true") {
      prev.dataset.rsaBatch50Bound = "true";
      prev.addEventListener("click", () => { currentPage -= 1; render(); });
    }
    if (next && next.dataset.rsaBatch50Bound !== "true") {
      next.dataset.rsaBatch50Bound = "true";
      next.addEventListener("click", () => { currentPage += 1; render(); });
    }
    bindSwipePagination(container, {
      prev: () => { currentPage -= 1; render(); },
      next: () => { currentPage += 1; render(); }
    });

    global.addEventListener("resize", render);
    render();
  }

  function setupPackageSlider() {
    const slider = document.getElementById("homePackageSlider");
    const dots = document.getElementById("homePackageDots");
    const prev = document.querySelector(".home-package-arrow-prev");
    const next = document.querySelector(".home-package-arrow-next");
    if (!slider || !dots) return;
    let current = 0;
    function isMobile() {
      return global.matchMedia("(max-width: 799px) and (orientation: portrait), (max-height: 430px) and (orientation: landscape)").matches;
    }
    function render() {
      const slides = Array.from(slider.querySelectorAll(".package-banner-card"));
      if (current >= slides.length) current = Math.max(0, slides.length - 1);
      slides.forEach((slide) => {
        slide.style.transform = isMobile() ? `translateX(-${current * 100}%)` : "translateX(0)";
      });
      dots.innerHTML = "";
      slides.forEach((_, index) => {
        const dot = document.createElement("button");
        dot.type = "button";
        dot.className = "home-package-dot";
        if (index === current) dot.classList.add("active");
        dot.addEventListener("click", () => { current = index; render(); });
        dots.appendChild(dot);
      });
      if (prev) prev.classList.toggle("is-hidden", !isMobile() || current <= 0);
      if (next) next.classList.toggle("is-hidden", !isMobile() || current >= slides.length - 1);
    }
    if (prev && prev.dataset.rsaBatch50Bound !== "true") {
      prev.dataset.rsaBatch50Bound = "true";
      prev.addEventListener("click", () => { if (isMobile()) { current -= 1; render(); } });
    }
    if (next && next.dataset.rsaBatch50Bound !== "true") {
      next.dataset.rsaBatch50Bound = "true";
      next.addEventListener("click", () => { if (isMobile()) { current += 1; render(); } });
    }
    bindSwipePagination(slider, {
      prev: () => { if (isMobile()) { current -= 1; render(); } },
      next: () => { if (isMobile()) { current += 1; render(); } }
    });

    global.addEventListener("resize", render);
    render();
  }

  async function loadProductsAndBrands() {
    const [products, brands] = await Promise.all([
      fetchPagedApiItems("/api/products", 50),
      fetchPagedApiItems("/api/brands", 50)
    ]);
    return {
      products: products.filter(looksShown).sort(sortByDisplaySeq),
      brands: brands.filter(looksShown).sort(sortByDisplaySeq)
    };
  }

  async function loadServices() {
    try {
      const page = await fetchJson("/api/pages/services");
      const pageItems = page && Array.isArray(page.services) ? page.services : extractItems(page);
      if (pageItems.length) return pageItems.filter(looksShown).sort(sortByDisplaySeq);
    } catch (_error) {}
    return (await fetchPagedApiItems("/api/services", 50)).filter(looksShown).sort(sortByDisplaySeq);
  }

  async function loadContactPage() {
    try {
      const page = await fetchJson("/api/pages/contact");
      if (page && (page.company_contact || page.contact_persons || page.social_media)) return page;
    } catch (_error) {}
    return fetchJson("/api/contact");
  }

  async function loadAboutPage() {
    try {
      const payload = await fetchJson("/api/pages/about");
      if (payload) return payload;
    } catch (_error) {}
    const about = await fetchJson("/api/about");
    return { about: Array.isArray(about.items) ? about.items[0] : about };
  }

  function renderHomePage(data, services) {
    const packageSlider = document.getElementById("homePackageSlider");
    const featuredGrid = document.getElementById("featuredProductsGrid");
    const promoGrid = document.getElementById("promoProductsGrid");
    const brandsGrid = document.getElementById("homeBrandsGrid");
    const servicesGrid = document.getElementById("homeServicesSlider");

    if (packageSlider) {
      const packages = data.products.filter((product) => {
        const p = normalizeProduct(product);
        const categoryText = String(firstNonEmpty(product.category_key, product.category_name, product.product_category_key, product.product_category, product.category, "")).toLowerCase();
        const isPackageCategory = p.categoryKey === "packages" || p.categoryKey === "packages-kits" || categoryText.includes("package") || categoryText.includes("kit");
        return looksShown(product) && p.showPack && isPackageCategory;
      }).slice(0, 3);
      packageSlider.innerHTML = packages.length ? packages.map(renderPackageCard).join("") : `<div class="rsa-cms-loading-state">No package products available.</div>`;
      setupPackageSlider();
    }

    if (featuredGrid) {
      featuredGrid.innerHTML = data.products.slice(0, 15).map(renderFeaturedCard).join("") || `<div class="rsa-cms-loading-state">No featured products available.</div>`;
      setupPagedDisplay({ container: featuredGrid, itemSelector: ".featured-product-card", dots: "#featuredProductsDots", prev: ".home-featured-arrow-prev", next: ".home-featured-arrow-next", desktop: 5, mobile: 6, display: "grid", dotClass: "featured-dot" });
    }

    if (promoGrid) {
      const promos = data.products.filter((product) => normalizeProduct(product).hasSale).slice(0, 15);
      promoGrid.innerHTML = promos.length ? promos.map(renderPromoCard).join("") : `<div class="rsa-cms-loading-state">No sale products available.</div>`;
      setupPagedDisplay({ container: promoGrid, itemSelector: ".promo-product-card", dots: "#promoProductsDots", prev: ".home-promo-arrow-prev", next: ".home-promo-arrow-next", desktop: 5, mobile: 6, display: "grid", dotClass: "promo-dot" });
    }

    if (brandsGrid) {
      brandsGrid.innerHTML = data.brands.slice(0, 24).map(renderBrandCard).join("") || `<div class="rsa-cms-loading-state">No brands available.</div>`;
      setupPagedDisplay({ container: brandsGrid, itemSelector: ".home-brand-item", dots: "#homeBrandsDots", prev: ".home-brands-arrow-prev", next: ".home-brands-arrow-next", desktop: 9, mobile: 6, display: "flex", dotClass: "home-brand-dot" });
    }

    if (servicesGrid) {
      servicesGrid.innerHTML = services.slice(0, 12).map(renderHomeServiceCard).join("") || `<div class="rsa-cms-loading-state">No services available.</div>`;
      global.dispatchEvent(new Event("resize"));
    }
  }

  function renderAboutPage(payload) {
    const about = payload && payload.about ? payload.about : payload;
    if (!about) return;

    setHtml(".about-page-hero-copy h1", heroTitleHtml(about.hero_title, "Trusted CCTV Installation, Security Products & Site Visit Support"));
    setText(".about-page-hero-desc", firstNonEmpty(about.hero_subtitle, about.meta_description));
    setText(".about-page-story-copy > p", firstNonEmpty(about.company_story_title, "Our Company Story"));
    setHtml(".about-page-story-copy h2", heroTitleHtml(about.company_story_title || about.hero_title, "Your Security, Our Priority"));

    const storyCopy = document.querySelector(".about-page-story-copy");
    if (storyCopy && about.company_story_body) {
      const link = storyCopy.querySelector("a.about-page-text-link")?.outerHTML || "";
      const label = storyCopy.querySelector("p.text-red-700")?.outerHTML || '<p class="text-red-700 text-sm font-bold uppercase mb-2">Our Company Story</p>';
      const title = storyCopy.querySelector("h2")?.outerHTML || "";
      storyCopy.innerHTML = `${label}${title}<p>${escapeHtml(about.company_story_body)}</p>${link}`;
    }

    const storyImage = document.querySelector(".about-page-story-image");
    if (storyImage && about.company_story_image_path) {
      storyImage.src = normalizeAssetPath(about.company_story_image_path, storyImage.src);
    }

    const missionGrid = document.querySelector(".about-page-mission-grid");
    if (missionGrid) {
      const cards = [];
      if (about.mission_title || about.mission_body) {
        cards.push({ icon: "fa-solid fa-bullseye", label: "Our Mission", title: about.mission_title, body: about.mission_body });
      }
      if (about.vision_title || about.vision_body) {
        cards.push({ icon: "fa-solid fa-handshake", label: "Our Vision", title: about.vision_title, body: about.vision_body });
      }
      missionGrid.innerHTML = cards.map((card) => `
        <div class="home-soft-card about-page-mission-card">
          <i class="${escapeHtml(card.icon)}"></i>
          <div><p class="text-red-700 text-sm font-bold uppercase mb-2">${escapeHtml(card.label)}</p><h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.body)}</p></div>
        </div>`).join("") || `<div class="rsa-cms-loading-state">No mission details available.</div>`;
    }

    const whyGrid = document.querySelector(".about-page-why-grid");
    if (whyGrid) {
      const bullets = [];
      for (let index = 1; index <= 6; index += 1) {
        const value = about[`why_choose_bullet_${String(index).padStart(2, "0")}`];
        if (value) bullets.push(value);
      }
      whyGrid.innerHTML = bullets.map((text, index) => `
        <div class="about-page-why-item">
          <i class="${index % 2 ? "fa-solid fa-shield-halved" : "fa-solid fa-circle-check"}"></i>
          <h3>${escapeHtml(text)}</h3>
          <p>${escapeHtml(about.why_choose_body || "Reliable CCTV and security support for your property.")}</p>
        </div>`).join("") || `<div class="rsa-cms-loading-state">No reasons available.</div>`;
    }

    const galleryGrid = document.querySelector(".about-page-gallery-grid");
    const gallery = payload && Array.isArray(payload.project_gallery) ? payload.project_gallery : [];
    if (galleryGrid && gallery.length) {
      galleryGrid.innerHTML = gallery.filter(looksShown).sort(sortByDisplaySeq).map((item) => `
        <div class="about-page-gallery-item">
          <img loading="lazy" decoding="async" src="${escapeHtml(normalizeAssetPath(item.image_path, DEFAULT_LOGO))}" alt="${escapeHtml(firstNonEmpty(item.alt_text, item.project_title))}">
          <h3>${escapeHtml(item.project_title)}</h3>
        </div>`).join("");
    } else if (galleryGrid) {
      galleryGrid.innerHTML = `<div class="rsa-cms-loading-state">No project gallery records available.</div>`;
    }
    global.dispatchEvent(new Event("resize"));
  }

  function renderServicesPage(services) {
    const grid = document.querySelector(".services-page-cards-grid");
    if (!grid) return;
    grid.innerHTML = services.map(renderServicesPageCard).join("") || `<div class="rsa-cms-loading-state">No services available.</div>`;
    global.dispatchEvent(new Event("resize"));
  }

  function contactCompany(payload) {
    return payload && (payload.company_contact || (Array.isArray(payload.items) ? payload.items.find((item) => item.contact_type === "Company Contact") : null));
  }

  function contactPersons(payload) {
    if (!payload) return [];
    if (Array.isArray(payload.contact_persons)) return payload.contact_persons;
    if (Array.isArray(payload.items)) return payload.items.filter((item) => item.contact_type === "Contact Person");
    return [];
  }

  function contactSocials(payload) {
    if (!payload) return [];
    if (Array.isArray(payload.social_media)) return payload.social_media;
    if (Array.isArray(payload.items)) return payload.items.filter((item) => item.contact_type === "Social Media");
    return [];
  }

  function telHref(number) {
    const digits = String(number || "").replace(/\D+/g, "");
    return digits ? `tel:+${digits.startsWith("63") ? digits : digits}` : "#";
  }

  function mailHref(email) {
    return email ? `mailto:${email}` : "#";
  }

  function updateGlobalHeaderContact(company, socials) {
    if (!company) return;
    const phone = firstNonEmpty(company.primary_contact_number, company.secondary_contact_number);
    const email = firstNonEmpty(company.company_email, company.email_address);
    document.querySelectorAll(".mobile-contact-row span, .hidden.md\\:flex span").forEach((span) => {
      const text = span.textContent || "";
      if (text.includes("@") && email) span.textContent = email;
      if ((text.includes("+63") || text.includes("091")) && phone) span.textContent = phone;
    });
    document.querySelectorAll('a[href^="tel:"]').forEach((a) => {
      if (phone && (a.textContent.includes("+63") || a.textContent.includes("091") || a.classList.contains("about-page-secondary-btn"))) a.href = telHref(phone);
    });
    document.querySelectorAll('a[href^="mailto:"]').forEach((a) => {
      if (email) a.href = mailHref(email);
    });

    const socialLinks = Array.from(document.querySelectorAll(".header-social-link, .mobile-social-row a"));
    socialLinks.forEach((link, index) => {
      const record = socials[index];
      if (record && record.profile_url) link.href = record.profile_url;
    });
  }

  function socialContactValue(record) {
    return firstNonEmpty(
      record && record.profile_url,
      record && record.phone_number_url,
      record && record.phone_number,
      record && record.url,
      record && record.contact_value
    );
  }

  function socialChannelUrl(record, value) {
    const raw = String(value || "").trim();
    if (!raw) return "#";
    if (/^(https?:|mailto:|tel:|sms:|viber:)/i.test(raw)) return raw;

    const platform = String(firstNonEmpty(record && record.platform_name, record && record.platform_key, "")).toLowerCase();
    const digits = raw.replace(/\D+/g, "");

    if (platform.includes("whatsapp") && digits) return `https://wa.me/${digits.startsWith("63") ? digits : digits}`;
    if (raw.includes("@") && !raw.includes(" ")) return mailHref(raw);
    if (/^\+?\d[\d\s().-]+$/.test(raw) || digits.length >= 7) return telHref(raw);

    return raw;
  }

  function renderContactInfo(payload) {
    const company = contactCompany(payload);
    const persons = contactPersons(payload).filter(looksShown).sort(sortByDisplaySeq);
    const socials = contactSocials(payload).filter(looksShown).sort(sortByDisplaySeq);
    updateGlobalHeaderContact(company, socials);
    if (!company) return;

    const infoList = document.querySelector(".contact-info-list");
    if (infoList) {
      const items = [];
      const numbers = [company.primary_contact_number, company.secondary_contact_number].filter(Boolean).map((number) => `<strong>${escapeHtml(number)}</strong>`).join("<br>");
      if (numbers) items.push(["fa-solid fa-phone", "Contact Numbers", numbers]);
      if (company.company_email) items.push(["fa-solid fa-envelope", "Email", `<strong>${escapeHtml(company.company_email)}</strong>`]);
      if (company.company_address) items.push(["fa-solid fa-location-dot", "Office Address", escapeHtml(company.company_address)]);
      if (company.showroom_address) items.push(["fa-solid fa-store", "Showroom", escapeHtml(company.showroom_address)]);
      if (company.business_hours) items.push(["fa-solid fa-clock", "Office Hours", escapeHtml(company.business_hours)]);
      infoList.innerHTML = items.map(([icon, title, body]) => `
        <div class="contact-info-item"><span class="contact-info-icon"><i class="${icon}"></i></span><div><h3>${title}</h3><p>${body}</p></div></div>`).join("");
    }

    const personGrid = document.querySelector(".contact-person-grid");
    if (personGrid) {
      personGrid.innerHTML = persons.map((person) => `
        <article class="home-soft-card contact-person-card">
          <img loading="lazy" decoding="async" src="${escapeHtml(normalizeAssetPath(person.person_image_path, DEFAULT_CONTACT_IMAGE))}" alt="${escapeHtml(person.person_name || "Contact person")}" class="contact-person-avatar">
          <div class="contact-person-copy">
            <p>${escapeHtml(person.department || "Contact Person")}</p>
            <h3>${escapeHtml(person.person_name || "RSA Team")}</h3>
            <span>${escapeHtml(person.position_title || "Team Contact")}</span>
            <div class="contact-person-divider"></div>
            ${person.phone_number ? `<a href="${escapeHtml(telHref(person.phone_number))}"><i class="fa-solid fa-phone"></i>${escapeHtml(person.phone_number)}</a>` : ""}
            ${person.email_address ? `<a href="${escapeHtml(mailHref(person.email_address))}"><i class="fa-solid fa-envelope"></i>${escapeHtml(person.email_address)}</a>` : ""}
          </div>
        </article>`).join("") || `<div class="rsa-cms-loading-state">No contact persons available.</div>`;
    }
    const channelGrid = document.querySelector(".contact-channel-grid");
    if (channelGrid) {
      const channels = socials.map((social) => {
        const detail = socialContactValue(social);
        return {
          icon: socialIconClass(social),
          title: firstNonEmpty(social.platform_name, social.platform_key, "Social Media"),
          detail,
          url: socialChannelUrl(social, detail)
        };
      }).filter((channel) => channel.detail);

      channelGrid.innerHTML = channels.map((channel) => `
        <a href="${escapeHtml(channel.url)}" class="home-soft-card contact-channel-card">
          <i class="${escapeHtml(channel.icon)}"></i><h3>${escapeHtml(channel.title)}</h3><p>${escapeHtml(channel.detail)}</p>
        </a>`).join("") || `<div class="rsa-cms-loading-state">No social media contacts available.</div>`;
    }

    const locationAddress = document.querySelector(".contact-location-address p");
    if (locationAddress && company.company_address) locationAddress.innerHTML = escapeHtml(company.company_address);
    const mapPin = document.querySelector(".contact-map-pin-card span");
    if (mapPin && company.company_address) mapPin.textContent = company.company_address;

    document.querySelectorAll(".booking-contact-links a").forEach((link) => {
      if (link.href.startsWith("tel") && company.primary_contact_number) {
        link.href = telHref(company.primary_contact_number);
        link.innerHTML = `<i class="fa-solid fa-phone"></i>${escapeHtml(company.primary_contact_number)}`;
      }
      if (link.href.startsWith("mailto") && company.company_email) {
        link.href = mailHref(company.company_email);
        link.innerHTML = `<i class="fa-solid fa-envelope"></i>${escapeHtml(company.company_email)}`;
      }
    });
    global.dispatchEvent(new Event("resize"));
  }

  function ensureStatusElement(form) {
    let status = form.querySelector("[data-rsa-form-status]");
    if (!status) {
      status = document.createElement("div");
      status.className = "rsa-api-form-status";
      status.setAttribute("data-rsa-form-status", "");
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      form.appendChild(status);
    }
    status.style.marginTop = "14px";
    status.style.fontWeight = "700";
    return status;
  }

  function setFormStatus(form, message, type) {
    const status = ensureStatusElement(form);
    status.textContent = message || "";
    status.hidden = !message;
    status.dataset.status = type || "info";
    status.style.color = type === "error" ? "#b91c1c" : type === "success" ? "#166534" : "#374151";
  }

  function ensureLeadSuccessModalStyle() {
    if (document.getElementById("rsaLeadSuccessModalStyle")) return;
    const style = document.createElement("style");
    style.id = "rsaLeadSuccessModalStyle";
    style.textContent = `
      .rsa-lead-success-overlay {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: grid;
        place-items: center;
        padding: 22px;
        background: rgba(15, 23, 42, 0.62);
        backdrop-filter: blur(4px);
      }
      .rsa-lead-success-modal {
        width: min(460px, 100%);
        border-radius: 24px;
        background: #fff;
        box-shadow: 0 28px 70px rgba(15, 23, 42, 0.26);
        padding: 30px 28px 26px;
        text-align: center;
        border: 1px solid rgba(185, 28, 28, 0.12);
      }
      .rsa-lead-success-icon {
        width: 62px;
        height: 62px;
        display: grid;
        place-items: center;
        margin: 0 auto 18px;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-size: 28px;
      }
      .rsa-lead-success-modal h2 {
        margin: 0 0 10px;
        color: #111827;
        font-size: 1.35rem;
        font-weight: 900;
      }
      .rsa-lead-success-modal p {
        margin: 0;
        color: #4b5563;
        line-height: 1.6;
      }
      .rsa-lead-success-ok {
        margin-top: 22px;
        border: 0;
        border-radius: 999px;
        background: #b91c1c;
        color: #fff;
        font-weight: 900;
        padding: 12px 28px;
        cursor: pointer;
        box-shadow: 0 16px 28px rgba(185, 28, 28, 0.22);
      }
      .rsa-lead-success-ok:hover { background: #991b1b; }
    `;
    document.head.appendChild(style);
  }

  function showLeadSuccessModal(title, message) {
    ensureLeadSuccessModalStyle();
    const existing = document.querySelector(".rsa-lead-success-overlay");
    if (existing) existing.remove();

    const overlay = document.createElement("div");
    overlay.className = "rsa-lead-success-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.innerHTML = `
      <div class="rsa-lead-success-modal">
        <div class="rsa-lead-success-icon"><i class="fa-solid fa-check"></i></div>
        <h2>${escapeHtml(title)}</h2>
        <p>${escapeHtml(message)}</p>
        <button class="rsa-lead-success-ok" type="button" data-rsa-lead-success-ok>OK</button>
      </div>
    `;
    document.body.appendChild(overlay);

    const ok = overlay.querySelector("[data-rsa-lead-success-ok]");
    if (ok) {
      ok.focus();
      ok.addEventListener("click", () => {
        window.location.href = "index.html";
      });
    }
  }

  function getField(form, name) {
    return form.elements[name] || form.querySelector(`[name="${name}"]`) || form.querySelector(`#${name}`);
  }

  function fieldValue(form, ...names) {
    for (const name of names) {
      const field = getField(form, name);
      if (field && field.value !== undefined && normalizeSpaces(field.value)) return normalizeSpaces(field.value);
    }
    return "";
  }

  function bookingPayload(form) {
    const propertyType = fieldValue(form, "property_type");
    const message = fieldValue(form, "message", "notes");
    return {
      customer_name: fieldValue(form, "customer_name", "full_name", "customerName"),
      contact_number: fieldValue(form, "contact_number", "phone_number", "contactNumber"),
      email: fieldValue(form, "email", "email_address", "emailAddress"),
      address: fieldValue(form, "location_address", "address", "site_address"),
      preferred_date: fieldValue(form, "preferred_date", "preferredDate"),
      preferred_time: fieldValue(form, "preferred_time", "preferredTime"),
      service_interest: fieldValue(form, "booking_type", "service_interest", "service_type"),
      notes: [message, propertyType ? `Property type: ${propertyType}` : ""].filter(Boolean).join("\n")
    };
  }

  function inquiryPayload(form) {
    return {
      customer_name: fieldValue(form, "customer_name", "full_name", "fullName"),
      contact_number: fieldValue(form, "contact_number", "phone_number", "contactNumber"),
      email: fieldValue(form, "email", "email_address", "emailAddress"),
      subject: fieldValue(form, "subject", "inquiry_subject"),
      message: fieldValue(form, "message", "notes"),
      source_page: form.dataset.rsaSourcePage || "contact-us"
    };
  }

  function removeEmpty(payload) {
    Object.keys(payload).forEach((key) => {
      if (payload[key] === undefined || payload[key] === null || payload[key] === "") delete payload[key];
    });
    return payload;
  }

  function setSubmitting(form, submitting) {
    form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((button) => {
      button.disabled = submitting;
      if (button.tagName === "BUTTON") {
        if (submitting) {
          button.dataset.rsaOriginalHtml = button.innerHTML;
          button.textContent = "Sending...";
        } else if (button.dataset.rsaOriginalHtml) {
          button.innerHTML = button.dataset.rsaOriginalHtml;
          delete button.dataset.rsaOriginalHtml;
        }
      }
    });
  }

  function bindLeadForms() {
    const bookingForm = document.querySelector('form[data-rsa-booking-form], #bookingForm');
    if (bookingForm && bookingForm.dataset.rsaBatch50Bound !== "true") {
      bookingForm.dataset.rsaBatch50Bound = "true";
      bookingForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = removeEmpty(bookingPayload(bookingForm));
        try {
          setSubmitting(bookingForm, true);
          setFormStatus(bookingForm, "Sending booking request...", "loading");
          await postJson("/api/bookings", payload);
          setFormStatus(bookingForm, "", "success");
          bookingForm.reset();
          showLeadSuccessModal(
            "Booking Request Received",
            "Thank you. Your booking request has been sent successfully. Our team will contact you soon to confirm the details."
          );
        } catch (error) {
          console.error("Booking submit failed", error);
          setFormStatus(bookingForm, `Could not send booking request: ${error.message}`, "error");
        } finally {
          setSubmitting(bookingForm, false);
        }
      });
    }

    const inquiryForm = document.querySelector('form[data-rsa-inquiry-form], form.contact-form-card');
    if (inquiryForm && inquiryForm.dataset.rsaBatch50Bound !== "true") {
      inquiryForm.dataset.rsaBatch50Bound = "true";
      inquiryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = removeEmpty(inquiryPayload(inquiryForm));
        try {
          setSubmitting(inquiryForm, true);
          setFormStatus(inquiryForm, "Sending inquiry...", "loading");
          await postJson("/api/inquiries", payload);
          setFormStatus(inquiryForm, "", "success");
          inquiryForm.reset();
          showLeadSuccessModal(
            "Inquiry Sent Successfully",
            "Thank you. Your inquiry has been sent successfully. Our team will review your message and contact you soon."
          );
        } catch (error) {
          console.error("Inquiry submit failed", error);
          setFormStatus(inquiryForm, `Could not send inquiry: ${error.message}`, "error");
        } finally {
          setSubmitting(inquiryForm, false);
        }
      });
    }
  }

  async function initializePublicCmsPages() {
    const isHome = document.body.classList.contains("home-page") || Boolean(document.getElementById("featuredProductsGrid"));
    const isAbout = document.body.classList.contains("about-page");
    const isServices = document.body.classList.contains("services-page");
    const isContact = document.body.classList.contains("contact-page");
    const isBooking = document.body.classList.contains("booking-page");

    bindLeadForms();

    if (isHome) {
      try {
        const [data, services] = await Promise.all([loadProductsAndBrands(), loadServices()]);
        renderHomePage(data, services);
      } catch (error) {
        console.error("Unable to load homepage API content.", error);
      }
    }

    if (isAbout) {
      try { renderAboutPage(await loadAboutPage()); }
      catch (error) { console.error("Unable to load about page API content.", error); }
    }

    if (isServices) {
      try { renderServicesPage(await loadServices()); }
      catch (error) { console.error("Unable to load services API content.", error); }
    }

    if (isContact || isBooking) {
      try { renderContactInfo(await loadContactPage()); }
      catch (error) { console.error("Unable to load contact API content.", error); }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePublicCmsPages);
  } else {
    initializePublicCmsPages();
  }
})(window);

