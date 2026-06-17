# Phase 8 Batch 61 — Domain / HTTPS / CloudFront / Route 53 Planning

Project: RSA CMS / Mini-CRM  
Status: Planned / Deferred until demo approval and final customer domain confirmation  
Current anchor: EC2 public-IP HTTP demo remains the active demo setup  
Prepared: 2026-06-16

## Purpose

Batch 61 moves RSA CMS / Mini-CRM from the current EC2 public-IP demo setup to a domain-based HTTPS launch setup.

The approved target architecture is:

```text
Visitor browser
  ↓ HTTPS
Route 53 DNS
  ↓ alias record
CloudFront distribution + ACM certificate
  ↓ origin request
EC2 Nginx origin / FastAPI backend
```

This batch is intentionally deferred until the customer/domain decision is final. The current EC2 public-IP HTTP setup remains the correct demo approach until then.

## Approved Direction

Use this launch path:

```text
Route 53 + ACM + CloudFront + EC2 Nginx origin
```

Do not use these by default:

```text
Application Load Balancer
NAT Gateway
RDS
Extra always-on EC2 instances
Paid WAF rules
Unnecessary paid notification services
```

The goal is to keep the domain launch aligned with the project’s AWS Free-Tier-first and post-free-tier low-cost rules.

## Current Demo Setup

Until Batch 61 is started:

```text
Public demo URL: http://EC2_PUBLIC_IP/
Admin demo URL: http://EC2_PUBLIC_IP/admin/
```

Current security group expectation for demo:

```text
HTTP 80  → 0.0.0.0/0
SSH 22   → current admin/developer IP only
```

Do not require HTTPS for the EC2 public-IP demo because trusted browser certificates are normally issued for domain names, not changing EC2 public IPs.

## Deferred Domain Decisions

These cannot be finalized until demo/customer launch approval:

```text
Final domain name
Root vs www behavior
Final ACM certificate names
Final DNS records
Final SEO canonical/Open Graph domain
```

Recommended default once a domain is approved:

```text
Main public/admin domain:
https://www.customer-domain.com

Admin path:
https://www.customer-domain.com/admin/
```

Do not create a separate `admin.customer-domain.com` subdomain for launch unless specifically approved later. Keeping admin under `/admin/` is simpler for CloudFront, Cognito callback/logout URLs, SSL behavior, and operational testing.

## Certificate Plan

Confirm only after the final domain is known.

Expected ACM certificate names:

```text
customer-domain.com
www.customer-domain.com
```

If a separate admin subdomain is later approved, add:

```text
admin.customer-domain.com
```

For CloudFront viewer HTTPS, the ACM certificate should be requested in `us-east-1`, while the EC2 origin can remain in `ap-southeast-1`.

Use DNS validation through Route 53 where possible.

## CloudFront Behavior Plan

CloudFront should be configured carefully so public static files can be cached while admin/auth/API traffic is not incorrectly cached.

Recommended initial behavior plan:

| Path pattern | Purpose | Cache recommendation |
|---|---|---|
| `/` | Homepage/public website | Normal/short public cache or no-cache during first smoke |
| `/*.html` | Static public/admin pages | Short cache or no-cache during first launch smoke |
| `/assets/*` | Public CSS/JS/images | Cacheable after smoke testing |
| `/api/media/*` | Public uploaded media display route | Cacheable or short-cache after validation |
| `/api/auth/*` | Auth/login/session routes | No-cache |
| `/api/admin/*` | Protected admin APIs | No-cache |
| `/api/*` | Public APIs and lead submit APIs | No-cache or very short-cache unless endpoint is proven safe |
| `/admin/*` | Admin static pages | No sensitive caching; no-cache or short-cache |

Important launch rule:

```text
Do not cache admin/API responses unless the endpoint is explicitly reviewed and safe.
```

## EC2 Origin Plan

Recommended origin:

```text
CloudFront origin → EC2 Nginx public DNS/public endpoint
```

CloudFront serves HTTPS to visitors. The EC2 Nginx origin continues to serve the public site, admin static files, protected admin APIs, public APIs, and `/api/media/...` routes.

For the first implementation, keep the EC2 public-IP rollback path available until CloudFront/domain smoke testing passes.

## Security Group Plan

### Current public-IP demo

```text
HTTP 80  → 0.0.0.0/0
SSH 22   → current admin/developer IP only
```

### Preferred after domain/CloudFront launch

```text
Origin HTTP/HTTPS port → CloudFront origin-facing prefix list only, if practical
SSH 22                 → current admin/developer IP only
```

This prevents users from bypassing CloudFront and browsing the EC2 public IP directly.

If origin lock-down causes unexpected behavior during first launch smoke, keep the rollback plan simple: temporarily allow HTTP 80 while diagnosing, then re-lock to CloudFront origin-facing access after validation.

## Nginx Preservation Rules

Batch 61 must preserve existing EC2 Nginx behavior needed by Batch 56B media/upload work:

```text
/api/media/ route must remain before any generic /api/ deny/403 rule
client_max_body_size 8m must remain
admin/CRM API protection must remain
direct :8000 access must remain blocked
```

Do not overwrite the active Nginx config with an older template that lacks the Batch 56B media route or upload-size fix.

## Cognito / Domain Update Plan

When the final domain is ready, review and update:

```text
Cognito app client callback URLs
Cognito app client logout URLs
FastAPI CORS allowed origins
Admin frontend base URL assumptions
Any hardcoded EC2 public IP references
Browser login redirects
Cookie/session assumptions if added later
```

Expected transition:

```text
Before:
http://EC2_PUBLIC_IP/admin/

After:
https://www.customer-domain.com/admin/
```

Settings > Users / Cognito group management remains Admin-only and continues to use protected FastAPI backend routes. The browser must not call Cognito admin APIs directly.

## SEO Dependency

SEO remains deferred until the final domain is confirmed.

Do not set EC2 public IP as canonical URL.

After Batch 61 confirms the launch domain, reopen the SEO work for:

```text
Page titles
Meta descriptions
Canonical URLs
Open Graph URLs
sitemap.xml
robots.txt
```

## Approved Cost Review

Route 53/domain is the approved paid exception for launch.

Expected domain/DNS cost model for a normal small-business `.com` style domain:

```text
Domain registration / renewal: roughly USD 15/year, varies by TLD
Route 53 hosted zone: roughly USD 0.50/month, about USD 6/year
Estimated domain + DNS planning number: roughly USD 20–25/year for a normal .com
DNS query charges: expected tiny for small traffic
```

Cost rules approved for Batch 61:

```text
Route 53 domain registration: paid annual cost
Route 53 hosted zone: paid monthly DNS management cost
ACM standard public certificate: expected no direct certificate charge for normal AWS-integrated use
CloudFront: expected free/low for small traffic within current free allowance
EC2: continue one-instance Free-Tier-first / low-cost origin plan
DynamoDB/S3/Cognito: continue Free-Tier-first / low-cost guardrails
```

Do not enable these without a separate approval:

```text
Application Load Balancer
NAT Gateway
RDS
Paid WAF rules
CloudFront real-time logs
Multiple always-on EC2 instances
SMS/email notification workflows
High-retention/expensive logging
Large unoptimized media storage
```

Before implementation, re-check AWS pricing pages because AWS pricing can change.

## Batch 61 Implementation Scope

When Batch 61 is reopened, planned implementation tasks are:

1. Confirm final domain name and customer approval.
2. Confirm root vs `www` behavior.
3. Confirm Route 53 domain purchase/transfer and hosted zone timing.
4. Request ACM certificate in `us-east-1`.
5. Validate ACM certificate through DNS.
6. Create CloudFront distribution with EC2 Nginx as origin.
7. Add CloudFront alternate domain names.
8. Add Route 53 alias records pointing domain/root/www to CloudFront.
9. Configure HTTP to HTTPS redirect at CloudFront.
10. Configure CloudFront behaviors for static, media, API, admin, and auth paths.
11. Preserve Nginx `/api/media/` and `client_max_body_size 8m` rules.
12. Update Cognito callback/logout URLs.
13. Update FastAPI CORS/domain configuration.
14. Confirm no EC2 public IP references remain where domain is required.
15. Optionally restrict EC2 origin access to CloudFront origin-facing prefix list.
16. Run full public/admin/media/API smoke tests.
17. Keep EC2 public-IP rollback path until domain smoke passes.
18. Stop EC2 when not actively testing to avoid unnecessary running cost.

## Smoke Test Checklist

After CloudFront/domain cutover, verify:

```text
https://www.customer-domain.com/
https://www.customer-domain.com/products.html
https://www.customer-domain.com/promotions.html
https://www.customer-domain.com/brands.html
https://www.customer-domain.com/about.html
https://www.customer-domain.com/services.html
https://www.customer-domain.com/contact-us.html
https://www.customer-domain.com/booking.html
https://www.customer-domain.com/admin/
```

API/media checks:

```text
GET /api/health
GET /api/products?per_page=1
GET /api/brands?per_page=1
GET /api/pages/contact
GET /api/media/<known-s3-backed-path>
POST /api/bookings using public form
POST /api/inquiries using public/contact form
Admin login through Cognito
Protected admin API returns 401/403 without token
Protected admin API works with valid Admin token
Standard user cannot access Settings > Users
```

## Rollback Plan

Keep the public-IP demo path available until the domain smoke test passes:

```text
http://EC2_PUBLIC_IP/
```

If CloudFront/domain launch fails:

1. Do not delete the CloudFront distribution immediately.
2. Verify Route 53 alias records.
3. Verify ACM certificate status.
4. Verify CloudFront origin health and behaviors.
5. Verify EC2 Nginx local HTTP works.
6. Temporarily use EC2 public IP for demo while fixing CloudFront/domain configuration.

## Not Included in Batch 61

```text
No SEO canonical/sitemap/robots work until domain is confirmed and live
No ALB
No NAT Gateway
No RDS
No new EC2 instance
No paid WAF by default
No email/SMS notifications
No admin user-management changes unless required for domain/Cognito callback updates
No unrelated frontend/admin polish
```

## Open Decisions for Batch Start

These must be confirmed before implementation:

```text
Final customer domain name
Whether root redirects to www or both serve the same site
Whether admin remains /admin/ under main domain
Whether EC2 origin should be locked to CloudFront immediately or after smoke testing
Whether Route 53 domain registration is done in the same AWS account or the domain is purchased elsewhere and delegated
```

## EC2 Cost Reminder

The EC2 demo instance should remain stopped when not actively deploying/testing. Start it only for demo, CloudFront/domain setup, smoke testing, or troubleshooting.
