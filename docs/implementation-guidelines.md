# RSA CMS / Mini-CRM Implementation Guidelines

## Phase 8 Continuation Guardrails — Batch 56D Onward

### Documentation/package folder standard

From Batch 59A cleanup onward, documentation packages should avoid creating nested Phase 8 README folders or root README text clutter. Use this structure:

```text
docs/
  project-overview.md
  architecture.md
  requirements.md
  feature-status.md
  implementation-guidelines.md
  decision-log.md
  open-issues.md
  UPDATE_SUMMARY.md
  phase8_batchXX_*.md

backend/scripts/
  apply/verify/cleanup scripts
```

Do not place patch scripts, README text files, or random Markdown files at the project root. Do not create `docs/Phase 8 README/` or `docs/phase8/` for new batch README files; use normal root-level `docs/phase8_batch*.md` files instead.

### Patch/package delivery style

Use project-structure patch zips only. Do not leave root-level batch folders inside the repository.

Preferred zip structure:

```text
frontend/...
backend/...
docs/...
deploy/...
scripts/...
```

Temporary patch/apply folders may be used outside the repository, but must not be committed.

### Runtime proof before patching

Before changing public/admin behavior:

1. Inspect the current file/function responsible for the behavior.
2. Confirm runtime behavior when possible from browser/admin output.
3. Patch only the affected function/section.
4. Do not add duplicate renderers over already-working dynamic sections.
5. State files changed and files intentionally not changed.

### Local development baseline

For current local testing, prefer:

- Backend in DynamoDB mode when validating real deployed data behavior.
- Media in S3 mode when validating `/api/media/...` paths that now point to S3-backed objects.
- Frontend through the local proxy on `http://127.0.0.1:5500` so `/api/*` and `/api/media/*` resolve correctly.

### Admin roles and restricted actions

- Use Cognito Groups for roles: `Admin` and `Standard`.
- Do not use the Cognito `profile` attribute for authorization.
- Do not expose AWS/Cognito admin credentials or direct Cognito admin calls in frontend JavaScript.
- Hide restricted UI for Standard users, but always enforce restrictions in backend routes.
- Do not add lead delete functionality. Booking, inquiry, and customer/lead records must remain for traceability.
- Batch 59A user onboarding uses suppressed Cognito invitation email and one-time visible temporary password after create/reset.
- Do not store, log, or re-display temporary passwords. If lost, reset/generate a new temporary password.
- Create/view/edit user forms use First Name and Last Name; main Users table displays generated Full Name.
- First-login password change must be handled through the browser UI, not command-line tools.

### Demo readiness and safety batches

- Batch 60A is the EC2 public-IP demo smoke checklist and demo data sanity pass. It supersedes the earlier Batch 62 regression idea for demo readiness.
- Batch 60B is the backup/restore/production safety notes batch. It supersedes the earlier Batch 64 backup/rollback idea.
- During Batch 60A, repeat the full demo checklist before declaring the app demo-ready.
- Batch 60B should document DynamoDB, S3, Git, EC2 deployment, Nginx rollback, import safety, and secret-handling procedures.

### Domain / HTTPS / CloudFront planning

- Batch 61 replaces the earlier Batch 65 CloudFront/SSL/domain planning idea.
- Keep the current EC2 public-IP HTTP demo until customer/domain approval.
- Later launch target: Route 53 + ACM + CloudFront + EC2 Nginx origin.
- Use `/admin/` under the main domain by default.
- Preserve Nginx `/api/media/` and `client_max_body_size 8m` rules during domain/CloudFront changes.
- Route 53/domain cost is approved as the paid exception: roughly USD 20-25/year planning number for normal `.com` domain + hosted zone, plus tiny DNS query charges.
- Avoid ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, and unnecessary paid services unless separately approved.

### EC2 cost safety

Keep the EC2 demo instance stopped unless actively deploying/testing. Continue avoiding ALB, NAT Gateway, RDS, unnecessary paid notifications, and always-on extra infrastructure unless explicitly approved after cost review.

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
9. Preserve the AWS Free-Tier-first cost rule during backend, admin and deployment work.
10. Document superseded decisions clearly.
11. Test responsive layouts after CSS changes.

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
display_seq
```

for new Phase 8 backend/admin manual ordering fields. Older frontend/static references to `display_order` should be migrated when the relevant module is updated.

## Backend Guidelines


### AWS Free-Tier-First Implementation Rules

All backend and deployment work must be reviewed against the original cost rule:

```text
First 12 months: AWS Free-Tier-first
Expected paid exception: Route 53/domain after IP-based testing/demo
After Free Tier: low-cost AWS operation
```

Implementation guardrails:

- Use one Free-Tier-eligible EC2 micro instance for FastAPI/admin APIs.
- Do not add Application Load Balancer for the initial deployment.
- Do not add NAT Gateway.
- Do not use RDS for the launch architecture.
- Do not keep multiple always-on EC2 instances running.
- Do not add SMS workflows or SMS MFA unless explicitly approved.
- Keep booking and inquiry notifications disabled by default; records must appear in admin panel.
- Use compressed images and upload limits before storing assets in S3.
- Keep CloudWatch logging useful but minimal, with short retention.
- Configure AWS Budgets/billing alerts before public testing.

### IP-Based Demo Before Route 53

Before Route 53/domain setup, test and demo the completed project using the EC2 public IP or free AWS-provided endpoint. Route 53/domain should be added only when domain-based launch is approved.

### FastAPI

- Organize route modules by domain.
- Validate input before database writes.
- Return safe error messages.
- Keep public and admin routes clearly separated.
- Protect admin routes with Cognito JWT validation.

### DynamoDB

- Confirm access patterns before final table/index design.
- Do not blindly copy relational schema without access pattern review.
- Use low provisioned capacity for the Free-Tier-first deployment.
- Start with minimal indexes and add GSIs only when a real page/API access pattern requires them.
- Avoid on-demand mode, streams, global tables and point-in-time recovery for launch unless explicitly approved after cost review.
- Use `show_flag` filtering for public endpoints.
- Use status fields for workflow state.
- Store images/files in S3, not DynamoDB.

### S3

- Store images by content type/domain.
- Use predictable paths for products, brands, services, packages, and gallery.
- Serve public assets through CloudFront where applicable.
- Compress images before upload.
- Set reasonable upload-size limits for admin images.
- Do not store video or large raw media for the first Free-Tier-first deployment.
- Avoid bucket versioning for launch unless explicitly approved after cost review.

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
- AWS billing alerts
- Free-Tier-first deployment review
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


## Phase 8 Final v5 Implementation Guidelines

The backend/admin implementation should follow [PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md](./PHASE8_FINAL_DYNAMODB_API_PLAN_v5.md).

Key implementation guardrails:

- Update local mock models/services/routes before creating AWS DynamoDB resources.
- Keep route code separate from storage implementation by introducing repositories before DynamoDB migration.
- Do not create `rsa_package_banners`; keep `GET /api/package-banners` sourced from `rsa_products`.
- Do not create split Contact Us tables; use `rsa_contact_us` with `contact_type`.
- Do not create `old_price`, sale boolean fields, customer email GSI, contact_type GSI, product show_pack GSI, or product sale GSI for launch.
- Use `display_seq` consistently in new code.
- Use `show_flag` and `show_pack_flag` according to the approved visibility rules.
- Use backend/server-side ID generation through `rsa_id_counters`.
- Keep admin-style routes unprotected only for local testing; add Cognito protection before external/public admin testing.


## Phase 8 Current Implementation Guardrails

Added in Batch 29 after full public/admin regression.

### Repository Mode

- Keep `RSA_REPOSITORY_MODE=mock` as the safe default for normal local development.
- Use `RSA_REPOSITORY_MODE=dynamodb` only when intentionally testing AWS-backed data.
- After DynamoDB tests in PowerShell, clear the environment variable with:

```powershell
Remove-Item Env:RSA_REPOSITORY_MODE
```

### Admin Auth

- Keep local admin auth disabled by default until the deployment/security step.
- Do not expose admin pages publicly without Cognito JWT enforcement.
- Avoid Cognito SMS/MFA/phone verification unless explicitly approved after cost review.

### Admin Media

- Admin image/photo/logo fields should use Browse/Choose File UI.
- Do not ask admins to type project-folder paths manually.
- Store/display resolved media paths or object keys.
- Real S3 binary upload/storage is enabled for the approved Batch 56A/56B media scope.
- Contact Person records may use the Contact Person photo/profile image field.
- Company Contact and Social Media records should not add extra photo upload fields unless reopened.

### Launch Data Import

- Company-facing launch data should use Excel/CSV templates.
- JSON seed data remains developer/test seed data.
- Import scripts must remain dry-run-first.
- DynamoDB writes must require explicit `--execute`.
- Import scripts should validate data before writing and should skip existing records by default unless an overwrite behavior is explicitly approved.

### Regression Testing

Before moving from Phase 8 into deployment/security work:

1. Run the full public/admin API regression in mock mode.
2. Run the full public/admin API regression in DynamoDB mode.
3. Complete the manual public/admin checklist.
4. Confirm mock mode is restored as the safe default.
5. Confirm no delete/destructive admin action is introduced unintentionally.
