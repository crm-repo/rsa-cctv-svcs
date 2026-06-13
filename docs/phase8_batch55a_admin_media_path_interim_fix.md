# Phase 8 Batch 55A — Admin Media Path Interim Fix

## Purpose

Admin image Browse/Choose File was preparing `uploads/...` paths before binary storage was actually available. That could break public images because the uploaded file did not exist on EC2 or S3 yet.

## Approved interim behavior

- Existing deployed static assets continue to use `assets/images/...`.
- `uploads/...` remains reserved for the future S3/local upload batch.
- Admin file selection does not overwrite the saved image path unless the backend confirms a real upload/storage preparation with `upload_prepared = true`.
- Admin can clear an image path intentionally, but accidental path replacement is blocked.

## Files

- `frontend/admin/assets/js/admin-media.js`
- `backend/app/data/review_import/brands.json`
- `backend/scripts/patch_admin_media_path_interim_fix.py`
- `backend/scripts/fix_static_brand_logo_paths.py`

## Notes

This batch does not implement S3 and does not delete DynamoDB data. It keeps the future path convention intact while preventing broken image paths during admin/public page testing.
