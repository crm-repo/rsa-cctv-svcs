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
| DynamoDB access pattern review pending | Medium | High | Open | Logical models must be adapted to DynamoDB query patterns and Free-Tier-first capacity limits |
| Free-Tier implementation drift | High | High | Open | Backend/deployment must avoid ALB, NAT Gateway, RDS, multiple EC2 instances, SMS and unnecessary paid services |
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
| Cost guardrails not yet enforced in infrastructure | Medium | High | Add deployment checklist and billing alerts before public testing |

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
| Paid AWS components accidentally added | High | High | Prohibit ALB, NAT Gateway, RDS, multiple EC2 instances and paid notifications unless explicitly approved |
| DynamoDB capacity mode exceeds Free Tier | High | Medium | Use low provisioned capacity and minimal GSIs for launch |
| Cognito SMS/email features create charges | Medium | Medium | Use admin-only Cognito and disable SMS MFA/phone verification where possible |
| CloudWatch log retention grows cost | Medium | Medium | Use basic logging and short retention |

## Blockers

| Blocker | Blocks | Notes |
|---|---|---|
| Backend not started | Admin, CRM, dynamic content | Static frontend can continue independently |
| Booking form not built | Booking lead workflow | Required before launch if Request Site Visit is live |
| Inquiry CTA not built | Product/package inquiry workflow | Required for lead generation from catalog |
| SEO/deployment not complete | Production launch | Must be completed before go-live |
| Free-Tier deployment review not completed | Backend/admin launch | Must confirm EC2, DynamoDB, S3, Cognito and logging settings before public testing |

## Outstanding Decisions

| Decision | Status | Options | Current Recommendation |
|---|---|---|---|
| Final Brands hero logo background shade | Open only if Brands reopened | `#d1d5db`, `#cbd5e1`, `#bfc7d1` | Use darker off-white/light gray, not transparent |
| Final Brands active brand style | Open only if Brands reopened | Solid outline, stronger border, subtle background | Use simple solid outline |
| Backend DynamoDB table/index design | Open | Single-table vs multi-table/access-pattern design | Review before backend build with Free-Tier-first capacity limits |
| Inquiry CTA layout | Open | Modal inline form, separate modal, contact redirect | Define before implementation |
| Booking page form layout | Open | Single-step form or multi-section form | Keep simple form first |
| Admin frontend approach | Open | Static HTML/Tailwind first, JS-driven, or future framework | Start simple unless requirements expand |

## Resolved Cost-Control Decisions

| Decision | Resolution | Notes |
|---|---|---|
| Booking request notifications | Disabled by default for launch | Requests only need to appear in the admin panel |
| Inquiry notifications | Disabled by default for launch | Inquiries only need to appear in the admin panel |
| Cognito SMS features | Disable where possible | Avoid SMS MFA and phone verification unless explicitly approved |
| Route 53/domain timing | Defer until after IP-based testing/demo | Route 53/domain is the expected paid exception |

## Unresolved Questions

1. Will product prices always be shown publicly, or should some products say “Contact for Price”?
2. Should contact persons shown in UI be selectable as assigned sales persons?
3. Will multiple branches/locations be supported later?
4. Should products have downloadable specification sheets?
5. Should package banners link directly to modal or only to Promotions?
6. Should product stock be visible to customers long-term?
7. Should admin support Draft/Published/Archived status in addition to `show_flag`?

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
| AWS billing alerts | Public testing and Free-Tier-first deployment |
| Free-Tier deployment review | Backend/admin launch |
