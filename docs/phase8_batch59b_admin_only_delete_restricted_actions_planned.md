# Batch 59B — Admin-only Delete / Restricted Actions

Status: Planned

## Dependency

Batch 59B should be implemented only after Batch 59A role/group detection is working.

## Rule

Admin-only delete/restricted actions must be enforced in both places:

1. Frontend: hide controls from Standard users.
2. Backend: return 403 for Standard users even if they call the API manually.

## Delete behavior

Admin users may see delete controls only for approved record types.

Standard users:

- Do not see delete controls.
- Cannot call delete/restricted endpoints.

## Lead records are non-delete

Do not enable delete for lead records, even for Admin users.

Lead/non-delete records include:

```text
bookings
inquiries
customers / customer lead records
```

Use status workflows, archive-style handling, or closed/resolved statuses instead of hard delete for leads.

## Existing protections remain required

- Category hide/delete protection when active products use a category.
- Subcategory delete protection when products use a subcategory.
- Brand hide/delete protection when products depend on the brand.
- Existing product/category/brand dependency rules from Batch 55B must remain active.
