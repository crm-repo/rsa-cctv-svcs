# Batch 57 — SEO Metadata / Page Titles

Status: Deferred

## Decision

Batch 57 is deferred until Route 53/final domain is ready.

## Reason

The following SEO items depend on the final public domain:

- Canonical URLs.
- Open Graph page URLs.
- Twitter card URLs.
- sitemap.xml.
- robots.txt.
- Final public URL conventions with or without `www`.

Do not use the EC2 public IP as the canonical URL.

## Future scope when reopened

- Page-specific `<title>` and meta description review.
- Canonical URLs using the final domain.
- Open Graph and Twitter card title/description/image/url tags.
- sitemap.xml.
- robots.txt.
- Final favicon/logo/social-preview checks.
