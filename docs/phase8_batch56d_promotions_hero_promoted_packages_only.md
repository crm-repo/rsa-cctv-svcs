# Batch 56D — Promotions Hero Promoted Packages Only

This patch changes only `frontend/assets/js/main.js`.

It does not touch Brands. The uploaded current `main.js` already rebuilds `.brands-hero-grid` dynamically from `/api/brands` via `renderBrandStrips()`.

Fix:
- Promotions hero now uses the already-loaded `/api/products` payload.
- It shows only package/kits products where `show_pack_flag = Y`.
- It no longer relies on the static Promotions hero HTML when products load successfully.

Apply by extracting/copying into the project root so `frontend/assets/js/main.js` is overwritten.
