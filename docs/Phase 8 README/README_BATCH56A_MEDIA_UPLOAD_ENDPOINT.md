Batch 56A - Media upload design/preflight + backend upload endpoint

Apply from project root:

  python backend/scripts/patch_media_upload_endpoint_56a.py

Then run:

  python backend/scripts/check_media_upload_preflight_56a.py

This batch adds:
- POST /api/admin/media/upload
- GET /api/media/{media_key:path}
- S3-ready/private storage service with local fallback
- readable slug filename generation with short unique suffix
- jpg/jpeg/png/webp validation and 5 MB default limit

This batch does not add admin form integration, S3 bucket creation, DynamoDB schema changes, CloudFront, Route 53, email/SMS, or paid notifications.
