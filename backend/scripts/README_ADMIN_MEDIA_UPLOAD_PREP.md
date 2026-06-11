# Phase 8 Batch 24 — Admin Media Upload Preparation

Batch 24 prepares the media upload contract without creating S3 resources yet.

## Endpoints

```text
GET  /api/admin/media/config
POST /api/admin/media/prepare-upload
```

`prepare-upload` accepts:

```json
{
  "media_type": "products",
  "file_name": "camera.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 123456
}
```

and returns:

```json
{
  "field_value": "uploads/products/camera.jpg",
  "upload_prepared": false
}
```

## Important

No file binary is uploaded in Batch 24. S3/local storage will be implemented later after bucket, access, cost, and deployment decisions are confirmed.

## Test

```powershell
python scripts\test_admin_media_prep.py
python scripts\test_admin_media_prep.py --execute
```
