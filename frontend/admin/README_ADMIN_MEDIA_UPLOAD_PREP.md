# Phase 8 Batch 24 — Admin Image Upload Preparation

This batch changes the admin experience for image/path fields.

Instead of asking an admin user to manually type paths like:

```text
assets/images/products/camera.jpg
brands/images/hikvision.png
```

forms now show a Browse/Choose File control for image fields.

## Current Batch 24 behavior

- Admin selects an image from local PC.
- UI displays the selected filename.
- A hidden form field keeps the image key/path needed by backend/public pages.
- Backend `/api/admin/media/prepare-upload` prepares a future object key such as:

```text
uploads/products/hikvision-dome-camera.jpg
```

## Important

Batch 24 does **not** upload binary image files yet.

Actual image storage is deferred to the approved S3/local-upload batch. Until then, selected images prepare database keys only.

## Why this is done now

This avoids asking non-technical admin users to type project folder paths manually and prepares the UI/backend contract for S3 storage later.
