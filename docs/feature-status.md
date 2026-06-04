# RSA CMS / Mini-CRM Feature Status

## Authority

This document is the authoritative implementation progress tracker. If status here conflicts with another document, this document controls implementation status.

## Status Legend

| Status | Meaning |
|---|---|
| Complete | Complete for the current project phase |
| Established | Working foundation exists and should be reused |
| Current Active | The active work area |
| Planned | Approved but not implemented |
| Deferred | Approved but intentionally postponed |
| Open if Reopened | Not active now; only revisit if explicitly requested |

## Current Implementation Status

| Feature | Status | Priority | Notes |
|---|---|---:|---|
| Homepage | Complete | High | Complete for current phase; do not reopen unless requested |
| Homepage Hero | Complete | High | Static frontend implemented |
| Homepage Feature Strip | Complete | High | Responsive polish complete |
| Recommended Packages | Complete | High | Three square package banners; mobile slider behavior completed |
| Featured Products Preview | Complete | High | Dot paging; one large preview card |
| Products on Sale Preview | Complete | High | Replaces older Promotions Preview label |
| Homepage Top Brands | Complete | Medium | Dot paging; six brands per page |
| Homepage Services Preview | Complete | High | Responsive image behavior finalized |
| Products Page | Established | High | Master reusable catalog architecture |
| Product Category Filters | Complete | High | Includes approved product categories |
| Products Brand Strip | Complete | High | Brand filter toggle supported |
| Product Search | Complete | High | Searches name, model, category, subcategory, features |
| Product Sorting | Complete | High | Must physically reorder DOM cards |
| Product Pagination | Complete | High | Count and page buttons update |
| Product Empty State | Complete | Medium | Magnifying-glass style no-results message |
| Product Quick View Modal | Complete | High | Reused for products and packages |
| Product Stock Badges | Complete | Medium | In Stock, Low Stock, Sold Out |
| Promotions Page | Complete | High | Complete for current phase |
| Promotions Hero | Complete | Medium | Three package banners |
| Promotions Sale Filter | Complete | High | Sale remains active and cannot be removed |
| Promotions All Products Behavior | Complete | High | Clears category while keeping Sale active |
| Brands Page | Complete | High | Complete for current phase; do not reopen unless requested |
| Brands Hero | Complete | High | Hero text, features, and logo grid direction established |
| Brands Hero Logo Background Shade | Open if Reopened | Low | Final shade can be adjusted only if Brands is reopened |
| Brands Brand Strip | Complete | High | One-row/two-row behavior resolved |
| Brands Brand Strip 16+ Two-Row Logic | Complete | High | 1–15 one row; 16+ two rows |
| Brands Drag-to-Scroll | Complete | Medium | Image drag disabled |
| Brands Active Indicator Technical Override | Complete | Medium | Products pseudo-element disabled on Brands page |
| Brands Active Indicator Final Visual | Open if Reopened | Low | Solid outline preferred if adjusted |
| Brands Filtering UI | Complete for current phase | High | Brand-first behavior is the requirement; backend/dynamic wiring deferred |
| Brands Dynamic Data Integration | Planned | Medium | Future API/database integration |
| Why We Use These Brands Section | Planned | Medium | Should appear before CTA when Brands is reopened or content phase begins |
| About Us Page | Current Active | High | Current active public page |
| Services Page | Planned | Medium | Standalone public page not confirmed complete |
| Contact Us Page | Planned | High | Public contact workflow needed |
| Booking Page | Planned | High | Required for Request Site Visit workflow |
| Booking Form Validation | Planned | High | Required before production if booking is live |
| Inquiry CTA from Modal | Planned | High | Required for product/package lead capture |
| Admin Panel | Planned | High | Future CMS/CRM phase |
| Admin Dashboard | Planned | Medium | Counts, latest bookings, latest inquiries |
| Product Management Admin | Planned | High | CRUD, show_flag, display_order |
| Brand Management Admin | Planned | High | CRUD, logo, featured flag, display_order |
| Customer CRM | Planned | High | Auto-created from bookings/inquiries |
| Booking Management | Planned | High | Status workflow and assignment |
| Inquiry Management | Planned | High | Status workflow and assignment |
| User Roles / Permissions | Planned | Medium | Super Admin, Admin, Sales Staff, Marketing Staff |
| Audit Logs | Planned | Medium | Future admin audit trail |
| Backend FastAPI | Planned | High | Not yet implemented |
| DynamoDB Integration | Planned | High | Logical tables planned; access pattern review needed |
| Cognito Auth | Planned | High | Required for admin |
| S3 Image Storage | Planned | Medium | Required for production/admin uploads |
| CloudFront / SSL | Planned | High | Required for production |
| SEO Metadata | Planned | High | Required before launch |
| Sitemap / robots.txt | Planned | High | Required before launch |
| Image Optimization | Planned | High | Required before launch |
| Analytics | Planned | Low | Optional unless business requires |

## Completed Features

- Homepage polishing for current phase.
- Products page catalog foundation.
- Promotions page catalog reuse and sale behavior.
- Brands page hero/brand strip polishing for current phase.
- Category strip threshold rule confirmed.
- Brand strip threshold rule confirmed.
- Products page active brand pseudo-element identified.
- Brands page override for Products active brand border.
- iPhone SE / small landscape package and services slider behavior.
- iPad Air/Pro portrait services horizontal layout.

## Current Active Work

| Feature | Notes |
|---|---|
| About Us Page | Current active public page |
| Documentation quality | Documentation set v2 is the current source of truth |

## Planned Features

- Booking form
- Inquiry CTA from modal
- Contact Us page
- Services page
- Backend API
- Admin CMS
- Customer CRM
- Authentication
- File/image upload
- SEO/deployment readiness

## Deferred Features

| Feature | Reason |
|---|---|
| Online checkout | Business model is lead generation, not ecommerce |
| Product detail pages | Post-launch enhancement |
| Brand detail pages | Post-launch enhancement |
| Product image zoom | Deferred |
| Modal gallery | Deferred |
| Swipe-to-close modal gesture | Deferred |
| Quotation generator | Future CRM enhancement |
| Live backend integration | Future backend/admin phase |
| Advanced analytics dashboard | Future enhancement |

## Known Gaps

- Booking form not implemented.
- Inquiry CTA from modal not finalized.
- Backend/admin not implemented.
- Database schema must be reviewed for DynamoDB access patterns.
- Final Brands hero logo card shade is not locked, but Brands page is not active.
- SEO metadata and deployment assets are not complete.
- Product/promotions static markup duplication remains.

## Current Priorities

1. Continue About Us page implementation.
2. Keep Homepage, Promotions, and Brands closed unless reopened.
3. Avoid global CSS changes that affect Products/Promotions/Brands unintentionally.
4. Preserve database-ready patterns.
5. Before production, implement booking/inquiry flows, SEO, image optimization, and deployment checklist.
