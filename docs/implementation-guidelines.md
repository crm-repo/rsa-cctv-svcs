# RSA CMS / Mini-CRM Implementation Guidelines

## Purpose

This document guides frontend, backend, admin, and AI-assisted development work for RSA CMS / Mini-CRM.

Use this document to maintain consistency, avoid regressions, and preserve current project decisions. For status, use [feature-status.md](./feature-status.md). For technical design, use [architecture.md](./architecture.md). For business requirements, use [requirements.md](./requirements.md).

## General Development Principles

1. Treat the latest documented decisions as authoritative.
2. Do not reopen completed pages unless specifically requested.
3. Prefer page-specific overrides over global CSS changes.
4. Reuse existing catalog, modal, filter, and card patterns.
5. Avoid unnecessary refactoring during active page polishing.
6. Preserve database-ready data attributes and naming conventions.
7. Keep Products, Promotions, and Brands behavior consistent where shared.
8. Maintain lead-generation focus; do not introduce checkout behavior.
9. Document superseded decisions clearly.
10. Test responsive layouts after CSS changes.

## Repository Conventions

Recommended structure:

```text
frontend/
├── index.html
├── about.html
├── products.html
├── promotions.html
├── brands.html
├── services.html
├── contact-us.html
├── booking.html
├── admin/
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── icons/
└── components/

backend/
├── app/
├── requirements.txt
└── .env

docs/
├── project-overview.md
├── architecture.md
├── requirements.md
├── feature-status.md
├── open-issues.md
├── implementation-guidelines.md
└── decision-log.md
```

## HTML Guidelines

- Use semantic structure where practical.
- Preserve data attributes used by product catalog logic.
- Keep product cards consistent across Products and Promotions until moved to shared data source.
- Use descriptive `alt` text for images.
- Use page wrapper classes for page-specific CSS.

Example:

```html
<body class="brands-page">
```

## CSS Guidelines

### General CSS Rules

- Avoid global changes unless the effect on all pages is intended.
- Use page-specific wrappers for targeted overrides.
- Keep shared styles stable for Products and Promotions.
- Remove temporary debug borders and test CSS before committing.
- Use `!important` only when required to override Tailwind or established page rules.

### Brand Color

Primary red:

```css
#b91c1c
```

### Soft Card Pattern

```css
background: #ffffff;
border: 1px solid #e5e7eb;
border-radius: 16px;
box-shadow: 0 4px 14px rgba(0,0,0,0.04);
```

### Brands Page Active Brand Override

Products page uses a global pseudo-element:

```css
.brand-strip-item.active::after
```

Brands page must disable it before applying a custom active style:

```css
.brands-page .brand-strip-item.active::after {
  display: none !important;
}
```

### Brands Page Two-Row Strip

Use this established two-row pattern:

```css
.brands-page .brand-strip-row.two-row {
  display: grid !important;
  grid-auto-flow: column;
  grid-template-rows: repeat(2, 120px);
  grid-auto-columns: 190px;
  gap: 16px 16px;
}
```

Do not reduce the two-row gap without retesting active indicator clipping.

### Brand Logo Image Drag Prevention

```css
.brands-page .brand-strip-item img {
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
}
```

## JavaScript Guidelines

### General JS Rules

- Keep catalog filtering centralized where possible.
- Sorting must append sorted cards back to the grid to update visual order.
- Reset pagination to page 1 after filters/search change.
- Keep Promotions sale hard filter protected.
- Avoid duplicating filter logic unless unavoidable.

### Brand Strip Row Balancing

For Brands page, use the one-row/two-row rule:

```javascript
const firstRowCount = Math.ceil(totalBrands / 2);
```

One row:

```text
1–15 brands
```

Two rows:

```text
16+ brands
```

### Drag-to-Scroll

Drag-to-scroll should:

- Avoid shaky trackpad behavior.
- Not force image dragging.
- Use grab/grabbing cursor on the strip container.
- Preserve mobile swipe behavior.

## Component Patterns

## Product Card Pattern

Product cards should include:

- Product image
- Sale badge where applicable
- Stock badge
- Brand logo
- Product model
- Product name
- Category/subcategory
- Price or sale price

Clickable modal triggers:

- Product image
- Product model
- Product name

## Product Modal Pattern

The modal should:

- Read data from product card attributes.
- Clear old key features before rendering new features.
- Render stock state from stock quantity and threshold.
- Close with X, outside click, and ESC.
- Be reused for products and packages.

## Filter Strip Pattern

Category filters:

- Horizontal scroll when necessary.
- Active state red.
- Icons turn white when active.
- Two-row behavior follows established category threshold.

Brand filters:

- Logo-based.
- Active click clears brand filter.
- Brands page may use custom active styling.

## Reusable Architecture Patterns

### Catalog Pages

Products, Promotions, and Brands should share:

- Product card structure
- Modal logic
- Search
- Sort
- Pagination
- Empty state

Differences:

| Page | Difference |
|---|---|
| Products | Full catalog |
| Promotions | Sale hard filter always active |
| Brands | Brand-first filtering |

### Public Visibility

Every public CMS record should eventually use:

```text
show_flag = Y/N
```

### Display Ordering

Use:

```text
display_order
```

for manual admin-controlled ordering.

## Backend Guidelines

### FastAPI

- Organize route modules by domain.
- Validate input before database writes.
- Return safe error messages.
- Keep public and admin routes clearly separated.
- Protect admin routes with Cognito JWT validation.

### DynamoDB

- Confirm access patterns before final table/index design.
- Do not blindly copy relational schema without access pattern review.
- Use `show_flag` filtering for public endpoints.
- Use status fields for workflow state.

### S3

- Store images by content type/domain.
- Use predictable paths for products, brands, services, packages, and gallery.
- Serve public assets through CloudFront.

## Testing Expectations

## Manual QA

Test after relevant changes:

- Desktop
- Mobile portrait
- Mobile landscape
- iPhone SE/small landscape
- iPad Mini portrait
- iPad Air/Pro portrait
- Tablet landscape

## Functional QA

Test:

- Category filtering
- Brand filtering
- Active brand click-to-clear
- Search
- Sorting
- Pagination
- Empty state
- Modal open/close
- Stock badge logic
- Promotions sale hard filter
- Promotions All Products behavior
- Brands strip one-row/two-row behavior
- Drag-to-scroll
- Mobile menu

## Pre-Launch QA

Before launch:

- Link check
- SEO metadata
- Sitemap
- robots.txt
- Image compression
- SSL
- Browser QA
- Mobile QA
- Remove console logs
- Remove debug CSS
- Backup final frontend

## Documentation Standards

- Keep docs in `/docs`.
- Update `feature-status.md` after completed work.
- Update `decision-log.md` when a significant decision is made.
- Update `open-issues.md` when an issue is resolved or discovered.
- Avoid conversational filler.
- Record superseded decisions clearly.
- Keep AI-agent instructions explicit and implementation-ready.
