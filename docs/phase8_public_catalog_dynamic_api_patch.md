# Phase 8 / Batch 49 - Public Catalog Dynamic API Patch

This patch moves the public Products, Promotions, and Brands catalog sections from static HTML cards to API-rendered cards.

## Data flow

```text
DynamoDB
  -> FastAPI public APIs
  -> frontend/assets/js/main.js
  -> Products / Promotions / Brands public pages
```

## Public APIs used

- `GET /api/products?per_page=500&page_size=500&limit=500`
- `GET /api/brands?per_page=500&page_size=500&limit=500`
- `GET /api/package-banners?per_page=12&page_size=12&limit=12` for the promotions hero, when available

## Pages updated

- `frontend/products.html`
- `frontend/promotions.html`
- `frontend/brands.html`
- `frontend/assets/js/main.js`

## Verification

1. Open the public products API and count/inspect products.
2. Open `products.html` and confirm the same shown products appear.
3. Edit or create a shown product in admin.
4. Refresh the public products page.
5. Confirm the change appears.
6. Repeat for sale products and brand filtering.

## Safety

This patch only changes static frontend files. It does not create, update, or delete AWS resources.
