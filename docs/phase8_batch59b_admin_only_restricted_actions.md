<!-- batch59b-full-admin-delete-actions -->
# Phase 8 Batch 59B â€” Admin-only Restricted/Delete Actions

Status: targeted full local patch package.

## Purpose

Batch 59B adds real Admin-only delete behavior for approved catalog records while preserving the non-delete rule for leads.

## Implemented in this package

- Adds backend `DELETE` routes protected by `require_admin_group` for:
  - Products
  - Brands
  - Categories
  - Key Features
- Adds repository delete helpers for mock and DynamoDB repositories.
- Adds dependency checks before delete:
  - Brand delete is blocked when any product uses the brand.
  - Category delete is blocked when any product uses the category.
  - Key Feature delete is blocked when any product uses that feature text.
- Adds Admin-only Delete buttons to catalog admin tables through `admin-catalog.js` only.
- Standard users do not receive Delete buttons.
- Customers, bookings, and inquiries remain non-delete for traceability.

## Not included

- No customer/booking/inquiry delete.
- No DynamoDB table changes.
- No Cognito schema/group changes.
- No S3/EC2/Route 53/CloudFront change.
- No global admin HTML rewrite.

## Browser verification

1. Login as System Administrator.
2. Open Brands.
3. Verify unused brand shows Delete.
4. Delete an unused brand and confirm it disappears after refresh.
5. Try deleting a brand used by products; backend should block it.
6. Login as Standard User and verify Delete is hidden.

