# Phase 8 Batch 59A Hotfix v6B — Admin API Auth Header Preservation

Status: targeted local auth-header hotfix

## Purpose

Fix Settings > Users create/update/reset/enable/disable requests returning `401 Unauthorized` while user listing works.

## Root cause

The shared admin API request helper built authenticated headers, then spread `...options` after the `headers` object. When POST/PUT code supplied `options.headers`, the final spread could replace the authenticated headers and drop the bearer token.

## Fix

`frontend/admin/assets/js/admin-api.js` now separates `options.headers` from the rest of `options`, spreads fetch options first, and then builds the final headers object last.

## Changed files

```text
frontend/admin/assets/js/admin-api.js
backend/scripts/apply_batch59a_hotfix_v6b_admin_api_auth_header.py
docs/phase8_batch59a_hotfix_v6b_admin_api_auth_header.md
```

## Not changed

```text
Cognito groups
IAM policies
FastAPI routes
DynamoDB
S3
EC2/Nginx
Users UI layout
```
