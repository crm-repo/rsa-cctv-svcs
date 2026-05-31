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
========================= */

const featuredGrid = document.getElementById("featuredProductsGrid");
const featuredDotsContainer = document.getElementById("featuredProductsDots");

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

  function renderFeaturedProducts() {
    const perPage = getProductsPerPage();
    const totalPages = Math.ceil(productCards.length / perPage);

    if (currentPage >= totalPages) {
      currentPage = totalPages - 1;
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

    if (swipeDistance > 0) {
      currentPage = (currentPage + 1) % totalPages;
    } else {
      currentPage = (currentPage - 1 + totalPages) % totalPages;
    }

    renderFeaturedProducts();
  });

  renderFeaturedProducts();

  let lastFeaturedPerPage = getProductsPerPage();

  window.addEventListener("resize", () => {
    const currentPerPage = getProductsPerPage();

    if (currentPerPage !== lastFeaturedPerPage) {
      lastFeaturedPerPage = currentPerPage;
      renderFeaturedProducts();
    }
  });
}

/* =========================
   PROMO PRODUCTS PAGING
========================= */

const promoGrid = document.getElementById("promoProductsGrid");
const promoDotsContainer = document.getElementById("promoProductsDots");

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

  function renderPromoProducts() {
    const perPage = getPromoProductsPerPage();
    const totalPages = Math.ceil(promoCards.length / perPage);

    if (currentPromoPage >= totalPages) {
      currentPromoPage = totalPages - 1;
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

    if (swipeDistance > 0) {
      currentPromoPage = (currentPromoPage + 1) % totalPages;
    } else {
      currentPromoPage =
        (currentPromoPage - 1 + totalPages) % totalPages;
    }

    renderPromoProducts();
  });

  renderPromoProducts();

  let lastPromoPerPage = getPromoProductsPerPage();

  window.addEventListener("resize", () => {
    const currentPerPage = getPromoProductsPerPage();

    if (currentPerPage !== lastPromoPerPage) {
      lastPromoPerPage = currentPerPage;
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
========================= */

const homePackageSlider = document.getElementById("homePackageSlider");
const homePackageDots = document.getElementById("homePackageDots");

if (homePackageSlider && homePackageDots) {
  const packageSlides = Array.from(
    homePackageSlider.querySelectorAll(".package-banner-card")
  );

  let currentPackageSlide = 0;
  let packageTouchStartX = 0;
  let packageTouchEndX = 0;

  function isMobilePortraitView() {
    return window.matchMedia(
      "(max-width: 799px) and (orientation: portrait), (max-height: 430px) and (orientation: landscape)"
    ).matches;
  }

  function renderHomePackageSlider() {
    packageSlides.forEach((slide) => {
      slide.style.transform = isMobilePortraitView()
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
  }

  homePackageSlider.addEventListener("touchstart", (event) => {
    if (!isMobilePortraitView()) return;
    packageTouchStartX = event.touches[0].clientX;
  });

  homePackageSlider.addEventListener("touchend", (event) => {
    if (!isMobilePortraitView()) return;

    packageTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = packageTouchStartX - packageTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    if (swipeDistance > 0) {
      currentPackageSlide =
        (currentPackageSlide + 1) % packageSlides.length;
    } else {
      currentPackageSlide =
        (currentPackageSlide - 1 + packageSlides.length) %
        packageSlides.length;
    }

    renderHomePackageSlider();
  });

  renderHomePackageSlider();

  window.addEventListener("resize", () => {
    if (!isMobilePortraitView()) {
      currentPackageSlide = 0;
    }

    renderHomePackageSlider();
  });
}

/* =========================
   HOME TOP BRANDS PAGING
========================= */

const homeBrandsGrid = document.getElementById("homeBrandsGrid");
const homeBrandsDots = document.getElementById("homeBrandsDots");

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

  function renderHomeBrands() {
    const brandsPerPage = getHomeBrandsPerPage();
    const totalPages = Math.ceil(brandItems.length / brandsPerPage);

    if (currentBrandPage >= totalPages) {
      currentBrandPage = totalPages - 1;
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

    if (swipeDistance > 0) {
      currentBrandPage = (currentBrandPage + 1) % totalPages;
    } else {
      currentBrandPage =
        (currentBrandPage - 1 + totalPages) % totalPages;
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
   HOME SERVICES MOBILE SLIDER
========================= */

const homeServicesSlider = document.getElementById("homeServicesSlider");
const homeServicesDots = document.getElementById("homeServicesDots");

if (homeServicesSlider && homeServicesDots) {
  const serviceSlides = Array.from(
    homeServicesSlider.querySelectorAll(".service-preview-card")
  );

  let currentServiceSlide = 0;
  let serviceTouchStartX = 0;
  let serviceTouchEndX = 0;

  function isServicesMobilePortrait() {
    return window.matchMedia(
      "(max-width: 799px) and (orientation: portrait), (max-height: 430px) and (orientation: landscape)"
    ).matches;
  }

  function renderHomeServicesSlider() {
    serviceSlides.forEach((slide) => {
      slide.style.transform = isServicesMobilePortrait()
        ? `translateX(-${currentServiceSlide * 100}%)`
        : "translateX(0)";
    });

    homeServicesDots.innerHTML = "";

    serviceSlides.forEach((_, index) => {
      const dot = document.createElement("button");
      dot.type = "button";
      dot.className = "home-services-dot";

      if (index === currentServiceSlide) {
        dot.classList.add("active");
      }

      dot.addEventListener("click", () => {
        currentServiceSlide = index;
        renderHomeServicesSlider();
      });

      homeServicesDots.appendChild(dot);
    });
  }

  homeServicesSlider.addEventListener("touchstart", (event) => {
    if (!isServicesMobilePortrait()) return;
    serviceTouchStartX = event.touches[0].clientX;
  });

  homeServicesSlider.addEventListener("touchend", (event) => {
    if (!isServicesMobilePortrait()) return;

    serviceTouchEndX = event.changedTouches[0].clientX;

    const swipeDistance = serviceTouchStartX - serviceTouchEndX;

    if (Math.abs(swipeDistance) < 40) return;

    if (swipeDistance > 0) {
      currentServiceSlide =
        (currentServiceSlide + 1) % serviceSlides.length;
    } else {
      currentServiceSlide =
        (currentServiceSlide - 1 + serviceSlides.length) %
        serviceSlides.length;
    }

    renderHomeServicesSlider();
  });

  renderHomeServicesSlider();

  window.addEventListener("resize", () => {
    if (!isServicesMobilePortrait()) {
      currentServiceSlide = 0;
    }

    renderHomeServicesSlider();
  });
}

/* =========================
   PRODUCTS PAGE PAGINATION + FILTER + SEARCH
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
const brandFilterItems = document.querySelectorAll(".brand-strip-item");
const isPromotionsPage = document.body.classList.contains("promotions-page");

if (productsGrid && productsPageNumbers && productsPrevBtn && productsNextBtn) {
  const allProductCards = Array.from(
    productsGrid.querySelectorAll(".catalog-product-card")
  );

  let currentProductsPage = 0;
  let currentFilter = "all";
  let currentSearch = "";
  let currentSort = "default";
  let currentBrand = "all";

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

  function getFilteredProducts() {
    let filtered = [...allProductCards];

  if (isPromotionsPage) {

    // Packages button
    if (currentFilter === "packages") {

      filtered = filtered.filter((card) =>
        card.dataset.category === "packages"
      );

    } else {

      // Default promotions = sale items only
      filtered = filtered.filter((card) =>
        card.querySelector(".catalog-sale-price")
      );

      // Additional category filters
      if (currentFilter !== "all" && currentFilter !== "sale") {
        filtered = filtered.filter((card) =>
          card.dataset.category === currentFilter
        );
      }

    }

  } else {
    if (currentFilter === "sale") {
      filtered = filtered.filter((card) =>
        card.querySelector(".catalog-sale-price")
      );
    } else if (currentFilter !== "all") {
      filtered = filtered.filter((card) =>
        card.dataset.category === currentFilter
      );
    }
  }

    /* BRAND FILTER */
    if (currentBrand !== "all") {
      filtered = filtered.filter((card) =>
        card.dataset.productBrandName === currentBrand
      );
    }

    if (currentSearch.trim() !== "") {
      const searchText = currentSearch.toLowerCase().trim();

      filtered = filtered.filter((card) => {
        const name = card.dataset.productName || "";
        const model = card.dataset.productModel || "";
        const category = card.dataset.category || "";
        const subcategory = card.dataset.productCategory || "";
        const features = card.dataset.productFeatures || "";

        const searchableText = `
          ${name}
          ${model}
          ${category}
          ${subcategory}
          ${features}
        `.toLowerCase();

        return searchableText.includes(searchText);
      });
    }
  /* SORTING */

  if (currentSort === "price-low") {

    filtered.sort((a, b) => {

      const aPrice = parsePrice(
        a.dataset.productPrice || "0"
      );

      const bPrice = parsePrice(
        b.dataset.productPrice || "0"
      );

      return aPrice - bPrice;

    });

  }

  else if (currentSort === "price-high") {

    filtered.sort((a, b) => {

      const aPrice = parsePrice(
        a.dataset.productPrice || "0"
      );

      const bPrice = parsePrice(
        b.dataset.productPrice || "0"
      );

      return bPrice - aPrice;

    });

  }

  else if (currentSort === "newest") {

    filtered.reverse();

  }

  else if (currentSort === "sale") {

    filtered = filtered.filter((card) =>
      card.querySelector(".catalog-sale-price")
    );

  }
    return filtered;
  }

  function renderProductsPage() {
    const productsPerPage = getProductsPerPage();
    const filteredProducts = getFilteredProducts();

    const totalProducts = filteredProducts.length;

    if (productsEmptyState) {
      productsEmptyState.classList.toggle(
        "hidden",
        totalProducts > 0
      );
    }

    const totalPages = Math.ceil(totalProducts / productsPerPage);

    if (currentProductsPage >= totalPages) {
      currentProductsPage = 0;
    }

    const start = currentProductsPage * productsPerPage;
    const end = start + productsPerPage;

    allProductCards.forEach((card) => {
      card.style.display = "none";
    });

    filteredProducts.slice(start, end).forEach((card) => {
      card.style.display = "flex";
      productsGrid.appendChild(card);
    });

    if (productsCount) {
      if (totalProducts > 0) {
        productsCount.textContent =
          `Showing ${start + 1}–${Math.min(end, totalProducts)} of ${totalProducts} products`;
      } else {
        productsCount.textContent = "Showing 0 products";
      }
    }

    productsPageNumbers.innerHTML = "";

    for (let i = 0; i < totalPages; i++) {
      const pageBtn = document.createElement("button");

      pageBtn.type = "button";
      pageBtn.className = "product-page-btn";
      pageBtn.textContent = i + 1;

      if (i === currentProductsPage) {
        pageBtn.classList.add("active");
      }

      pageBtn.addEventListener("click", () => {
        currentProductsPage = i;
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
      productsToolbar.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  }

  productsPrevBtn.addEventListener("click", () => {
    if (currentProductsPage > 0) {
      currentProductsPage--;
      renderProductsPage();
      scrollToProductsTop();
    }
  });

  productsNextBtn.addEventListener("click", () => {
    const productsPerPage = getProductsPerPage();

    const totalPages = Math.ceil(
      getFilteredProducts().length / productsPerPage
    );

    if (currentProductsPage < totalPages - 1) {
      currentProductsPage++;
      renderProductsPage();
      scrollToProductsTop();
    }
  });

  productFilterButtons.forEach((button) => {
    button.addEventListener("click", () => {

      if (isPromotionsPage && button.dataset.filter === "sale") {
        return;
      }

      productFilterButtons.forEach((btn) => {
        if (!(isPromotionsPage && btn.dataset.filter === "sale")) {
          btn.classList.remove("active");
        }
      });

      button.classList.add("active");

      currentFilter = button.getAttribute("data-filter") || "all";

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

      if (productsSectionTitle) {
        productsSectionTitle.textContent =
          filterTitles[currentFilter] || "Products";
      }

      currentProductsPage = 0;
      renderProductsPage();
    });
  });

  /* BRAND FILTER */
  brandFilterItems.forEach((item) => {

    item.addEventListener("click", () => {

      const selectedBrand = item.dataset.brandFilter || "all";
      const isAlreadyActive = item.classList.contains("active");

      brandFilterItems.forEach((brand) => {
        brand.classList.remove("active");
      });

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

  renderProductsPage();
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