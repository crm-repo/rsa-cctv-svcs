# RSA CMS / Mini-CRM Open Issues

## Authority

This document tracks risks, unresolved questions, blockers, technical debt, and dependencies. Implementation status is controlled by [feature-status.md](./feature-status.md).

## Known Issues

| Issue | Severity | Impact | Status | Notes |
|---|---|---|---|---|
| Product/promotions markup duplication | Medium | High | Open | Move to shared JSON/API/database source later |
| Backend not implemented | High | High | Planned | FastAPI/DynamoDB/Cognito phase pending |
| Admin panel not implemented | High | High | Planned | Required for long-term maintenance |
| Booking form not implemented | High | High | Open | Required if booking is included at launch |
| Inquiry CTA from modal not implemented | High | High | Open | Needed for product/package lead capture |
| SEO metadata missing/incomplete | High | Medium | Open | Required before production |
| sitemap.xml and robots.txt missing | High | Medium | Open | Required before production |
| Image optimization pending | Medium | High | Open | Needed for mobile performance |
| DynamoDB access pattern review pending | Medium | High | Open | Logical models must be adapted to DynamoDB query patterns |
| Final Brands hero logo card shade not locked | Low | Low | Open if Brands reopened | Candidate colors exist |
| Brands active indicator final visual not locked | Low | Low | Open if Brands reopened | Technical override is resolved |

## Technical Debt

| Technical Debt | Severity | Impact | Recommended Resolution |
|---|---|---|---|
| Static product cards duplicated between Products and Promotions | Medium | High | Move product data to shared JSON/API |
| Page-specific responsive CSS has grown large | Medium | Medium | Refactor after launch only if stable |
| Shared class names affect multiple pages | Medium | High | Prefer page-scoped CSS overrides |
| Package banners static | Low | Medium | Add Package Banner admin module |
| Brand list currently static | Medium | Medium | Add Brand admin + API |
| Product features stored in attributes | Medium | Medium | Normalize to Product Features table later |

## Risks

| Risk | Severity | Impact | Mitigation |
|---|---|---|---|
| Product and Promotions logic diverges | Medium | High | Use shared catalog module or API source |
| Global CSS changes break completed pages | High | High | Use page-specific wrappers such as `.brands-page` |
| Large images slow mobile load | Medium | High | Compress images and lazy load |
| Admin validation missing | Medium | High | Add validation rules in admin forms |
| `show_flag` confused with `status` | Medium | Medium | Enforce separate meanings in docs, UI labels, and backend validation |
| Promotions All Products contradiction reappears | Medium | Medium | Treat latest decision as authoritative: reset category while keeping Sale active |
| DynamoDB design copied too closely from relational schema | Medium | High | Review access patterns before backend build |
| Incomplete booking/inquiry flows reduce lead capture | High | High | Implement before production launch |

## Blockers

| Blocker | Blocks | Notes |
|---|---|---|
| Backend not started | Admin, CRM, dynamic content | Static frontend can continue independently |
| Booking form not built | Booking lead workflow | Required before launch if Request Site Visit is live |
| Inquiry CTA not built | Product/package inquiry workflow | Required for lead generation from catalog |
| SEO/deployment not complete | Production launch | Must be completed before go-live |

## Outstanding Decisions

| Decision | Status | Options | Current Recommendation |
|---|---|---|---|
| Final Brands hero logo background shade | Open only if Brands reopened | `#d1d5db`, `#cbd5e1`, `#bfc7d1` | Use darker off-white/light gray, not transparent |
| Final Brands active brand style | Open only if Brands reopened | Solid outline, stronger border, subtle background | Use simple solid outline |
| Backend DynamoDB table/index design | Open | Single-table vs multi-table/access-pattern design | Review before backend build |
| Inquiry CTA layout | Open | Modal inline form, separate modal, contact redirect | Define before implementation |
| Booking page form layout | Open | Single-step form or multi-section form | Keep simple form first |
| Admin frontend approach | Open | Static HTML/Tailwind first, JS-driven, or future framework | Start simple unless requirements expand |

## Unresolved Questions

1. Will product prices always be shown publicly, or should some products say “Contact for Price”?
2. Should booking requests send email notifications immediately?
3. Should inquiries send email notifications immediately?
4. Should contact persons shown in UI be selectable as assigned sales persons?
5. Will multiple branches/locations be supported later?
6. Should products have downloadable specification sheets?
7. Should package banners link directly to modal or only to Promotions?
8. Should product stock be visible to customers long-term?
9. Should admin support Draft/Published/Archived status in addition to `show_flag`?

## Dependencies

| Dependency | Required For |
|---|---|
| Final product content and images | Production launch |
| Optimized brand logos | Brands and homepage quality |
| Booking form details | Booking workflow |
| Inquiry CTA decision | Product/package lead capture |
| AWS setup | Backend/admin deployment |
| Cognito configuration | Admin authentication |
| S3 buckets | Image upload/storage |
| DynamoDB access pattern design | Backend implementation |
| SEO metadata | Production launch |
| SSL/domain setup | Production launch |
