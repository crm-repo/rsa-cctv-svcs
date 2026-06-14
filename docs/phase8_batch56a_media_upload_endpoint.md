# Batch 56A - Media upload design/preflight + backend upload endpoint

Approved decisions:

- Use S3 for deployed media storage, with local folder fallback for local development/testing.
- S3 bucket naming target: `rsa-cms-media-537765358118-ap-southeast-1`.
- Keep S3 private. No public write access and no public bucket policy required.
- Store/return both `media_key` and `media_url`; treat `media_key` as authoritative.
- Upload endpoint: `POST /api/admin/media/upload`.
- Display endpoint: `GET /api/media/{media_key:path}`.
- Allowed upload groups: `products`, `brands`, `project-gallery`, `contact-persons`.
- Allowed file types: `.jpg`, `.jpeg`, `.png`, `.webp` only.
- Max image size: 5 MB by default (`RSA_MEDIA_MAX_UPLOAD_MB=5`).
- Filename rule: readable slug + short unique suffix + original validated extension.
- Product slug source: `product_name` first; fallback to `brand_name + shortened feature_01 + subcategory`.
- No image conversion or resizing in 56A.
- Admin upload route stays under existing protected `/api/admin/*` protection.
- 56A is backend/preflight only. Full admin form integration is for 56B.

Environment variables:

```text
RSA_MEDIA_STORAGE_MODE=local              # local or s3
RSA_MEDIA_LOCAL_ROOT=backend/data/media_uploads
RSA_MEDIA_MAX_UPLOAD_MB=5
RSA_MEDIA_S3_BUCKET=rsa-cms-media-537765358118-ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1
```

For EC2/local-folder fallback, use a folder outside release directories, for example:

```text
RSA_MEDIA_LOCAL_ROOT=/opt/rsa-cms/shared/uploads
```

For S3 mode, set:

```text
RSA_MEDIA_STORAGE_MODE=s3
RSA_MEDIA_S3_BUCKET=rsa-cms-media-537765358118-ap-southeast-1
AWS_DEFAULT_REGION=ap-southeast-1
```

No CloudFront, Route 53, S3 versioning, replication, advanced Storage Lens, or paid notification services are introduced by this batch.
