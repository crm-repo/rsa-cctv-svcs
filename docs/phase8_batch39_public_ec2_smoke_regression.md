# Phase 8 Batch 39 — Public EC2 Smoke Regression

## Purpose

Batch 39 verifies the deployed EC2 public-IP demo after Nginx public/API lockdown.

It checks that:

- The public website is reachable through port 80.
- Approved public read APIs are reachable through Nginx.
- Admin UI, admin APIs, CRM listing APIs, `/docs`, and `/openapi.json` are blocked publicly.
- Direct backend port `8000` is not publicly reachable.
- Optional public booking/inquiry POST smoke tests still work through Nginx.

## Cost/Safety

- Keep the EC2 instance running only while testing.
- Stop the instance after the batch if not continuing immediately.
- Do not use Elastic IP, Route 53, ALB, NAT Gateway, RDS, or SMS/MFA for this batch.
- Do not expose `/admin/` or admin/CRM APIs publicly while admin auth remains disabled.

## Files

- `backend/scripts/check_ec2_public_site_smoke.py`
- `docs/phase8_batch39_public_ec2_smoke_checklist.md`
- `deploy/ec2/README_BATCH39_PUBLIC_EC2_SMOKE.md`

## Required current state

- Batch 34 EC2 demo instance exists.
- Batch 36 backend service is active on EC2.
- Batch 37 Nginx serves frontend and proxies approved public APIs.
- Batch 38 Nginx lockdown is applied.
- Security group inbound rules should be limited to:
  - SSH `22` from your IP `/32`
  - HTTP `80` from your IP `/32`
- Direct `8000` should not be open publicly.

## Run read-only smoke check

From local PowerShell, with the backend virtual environment activated:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_public_site_smoke.py --base-url http://<PUBLIC_IPV4>
```

Example:

```powershell
python scripts\check_ec2_public_site_smoke.py --base-url http://54.179.42.39
```

## Optional public write smoke check

This creates one public booking and one public inquiry record through the Nginx public endpoints.

```powershell
python scripts\check_ec2_public_site_smoke.py --base-url http://<PUBLIC_IPV4> --execute --confirm-write-test
```

Expected result:

- Static pages return `200`.
- Public read APIs return `200`.
- Admin/CRM management routes return `403`.
- Direct port `8000` is blocked or unreachable.
- Optional public booking/inquiry POST returns `200` or `201`.

## Pass criteria

Batch 39 passes when:

- Read-only smoke check passes.
- Optional write check passes if run.
- `/admin/`, `/api/admin/*`, `/api/customers`, GET `/api/bookings`, GET `/api/inquiries`, `/docs`, and `/openapi.json` are blocked.
- Direct public `:8000` does not return HTTP 200.
