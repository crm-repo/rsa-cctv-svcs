# Batch 58 — Image Optimization / Lazy Loading

Scope:
- Adds `loading="lazy"` and `decoding="async"` to non-critical public frontend images.
- Patches selected existing image render functions in `frontend/assets/js/main.js`.
- Patches static fallback HTML image tags in the eight main public pages.
- Skips likely critical hero/header/logo images in static HTML.

Not included:
- No image compression/replacement.
- No backend changes.
- No admin media upload changes.
- No DynamoDB or S3 path changes.
- No Route 53, SEO metadata, sitemap, or robots changes.

Run from project root:

```powershell
python .\scriptspply_batch58_image_lazy_loading.py --dry-run
python .\scriptspply_batch58_image_lazy_loading.py --execute
node --check .rontendssets\js\main.js
```

After execute, review:

```powershell
git diff --stat
git diff -- .rontend .\docs
eviewatch58_image_lazy_loading_report.txt
```

## Local testing result

Status: Local testing passed.

The broken image issue seen during local verification was caused by starting the backend with local media mode while DynamoDB records already pointed to S3-backed `/api/media/...` paths. Local development should use:

```powershell
$env:RSA_MEDIA_STORAGE_MODE="s3"
$env:RSA_MEDIA_S3_BUCKET="rsa-cms-media-537765358118-ap-southeast-1"
$env:RSA_MEDIA_MAX_UPLOAD_MB="5"
```

Frontend testing should continue through the local proxy so `/api/*` and `/api/media/*` resolve correctly.
