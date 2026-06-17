# Phase 8 Batch 59C — Public Category Strip DynamoDB Binding

Status: Applied / pending local browser verification

Marker: batch59c-hotfix-v2-public-category-strip-only

## Scope

Hydrate the public category strips on Products, Promotions, and Brands from `/api/categories`.

## Behavior

- Products keeps virtual All Products and Sale buttons, then renders visible DynamoDB categories.
- Promotions keeps virtual All Products and locked Sale buttons, then renders visible DynamoDB categories.
- Brands keeps virtual All Products, then renders visible DynamoDB categories.
- Category button keys use `category_key`.
- Category button labels use `category_name`.
- Category icons use `icon_code`.
- Category order uses `display_seq`.
- Hidden categories are not shown publicly.

## Safety

- Frontend-only public catalog change.
- No backend route change.
- No DynamoDB table/data change.
- No Cognito change.
- No S3/media change.
- No EC2/Nginx/Route 53/CloudFront change.
- Static HTML category buttons remain as fallback if `/api/categories` cannot load.
