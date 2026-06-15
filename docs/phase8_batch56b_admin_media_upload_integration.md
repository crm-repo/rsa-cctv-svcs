# Batch 56B - Admin media upload integration

Batch 56B connects the Batch 56A backend/S3 media upload endpoint to the existing admin media picker.

## Scope

Integrated real uploads for:

- Products: `image_path`
- Brands: `brand_logo_path`
- Project Gallery: `image_path`
- Contact Us: `person_image_path` for Contact Person records

Not included:

- No backend route changes
- No DynamoDB schema changes
- No S3 bucket/IAM changes
- No CloudFront or Route 53
- No email/SMS/notification changes
- No About/Services upload enablement in this batch

## Behavior

Choose File now uploads the selected image to `POST /api/admin/media/upload` before the record is saved.

Successful upload returns `upload_prepared=true` and a `/api/media/...` path. The hidden form field is updated only after the backend confirms upload success.

If upload fails, the existing image path is preserved.

Restore Current restores the image path that was loaded when the form opened.

## Safety

- JPG/JPEG/PNG/WEBP only
- Backend max upload limit from `/api/admin/media/config`
- Existing admin bearer token is used
- No unauthenticated upload
- Static legacy image paths remain supported
