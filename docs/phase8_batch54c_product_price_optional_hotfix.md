# Phase 8 Batch 54C Hotfix — Product Price Optional for Static Import

## Purpose

After Batch 54B imported reviewed static HTML data into DynamoDB, `/api/products` returned HTTP 500 while `/api/brands` and `/api/categories` returned HTTP 200.

The EC2 backend log showed `Product.model_validate(item)` failing because one imported product record did not contain a required `price` field:

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for Product
price
Field required [type=missing]
```

This is expected for package/banner-style products where a fixed public price may not exist.

## Change

Make `Product.price` optional in `backend/app/models/product.py`:

```python
price: Optional[float] = None
```

The admin create request can continue defaulting price to `0` for manual admin-created products.

## Apply

From project root:

```powershell
python backend/scripts/patch_product_price_optional.py
```

Then verify:

```powershell
Select-String -Path .\backend\app\models\product.py -Pattern "price: Optional\[float\] = None"
```

## Commit

```powershell
git status
git add backend/app/models/product.py backend/scripts/patch_product_price_optional.py docs/phase8_batch54c_product_price_optional_hotfix.md README_PHASE8_BATCH54C_PRODUCT_PRICE_OPTIONAL_HOTFIX.txt
git commit -m "Allow imported package products without price"
git push
```

## Deploy and test

Deploy to EC2, then test:

```powershell
$IP = "YOUR_EC2_PUBLIC_IP"
curl.exe -i "http://$IP/api/products?page=1&per_page=50"
```

Expected:

```text
HTTP/1.1 200 OK
```

Then verify Products, Promotions, and Brands pages load product cards again.
