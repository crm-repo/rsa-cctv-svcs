# Phase 8 Batch 54C — Package Quotation Hotfix

This revised hotfix covers the approved package pricing behavior.

## Approved behavior

- Package products may have no fixed full price.
- Backend Product.price must be optional so `/api/products` does not fail on package records without price.
- Public catalog grids show `Get Quotation` instead of a price for package products without price.
- The product modal uses a `Get Quotation` primary button linking to `contact-us.html` for those package products.

## Apply

From project root:

```powershell
python backend/scripts/patch_package_quotation_price.py
```

## Verify

```powershell
Select-String -Path .ackendpp\models\product.py -Pattern "price: Optional\[float\] = None"
Select-String -Path .rontendssets\js\main.js -Pattern "RSA_PACKAGE_QUOTATION_PATCH_VERSION|catalog-product-quote-link|modal-quotation-text"
```

Then commit, push, deploy, and test:

```powershell
git status
git add backend/app/models/product.py frontend/assets/js/main.js backend/scripts/patch_package_quotation_price.py docs/phase8_batch54c_package_quotation_hotfix.md README_PHASE8_BATCH54C_PACKAGE_QUOTATION_HOTFIX.txt
git commit -m "Support quotation-only package products"
git push
```

After EC2 deployment:

```powershell
$IP = "54.254.154.139"
curl.exe -i "http://$IP/api/products?page=1&per_page=50"
```

Expected: `HTTP/1.1 200 OK`.

Then open products, promotions, and brands pages and confirm package cards show `Get Quotation` where price is missing.
