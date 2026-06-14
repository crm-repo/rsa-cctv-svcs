# Phase 8 Batch 56A Filename Slug De-dup Hotfix

This small backend-only hotfix refines the Batch 56A media upload filename builder.

## Purpose

Product upload filenames still use readable slug filenames with a short unique suffix and the original validated extension. When product fallback naming is based on brand + shortened feature_01 + subcategory, repeated boundary phrases are removed.

Example: `dahua-full-color-4k-bullet-camera-bullet-camera-0f4f9f.png` becomes `dahua-full-color-4k-bullet-camera-0f4f9f.png`.

## Scope

- Backend filename builder only.
- No admin form integration.
- No frontend change.
- No DynamoDB schema change.
- No S3 bucket creation.
