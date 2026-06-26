# Phase 8 Batch 60B — Backup / Restore / Production Safety Notes

Date: 2026-06-26  
Status: Complete / documentation and procedure only  
Scope: RSA CMS / Mini-CRM demo and pre-launch safety runbooks

## 1. Purpose

Batch 60B documents the backup, restore, rollback, and production-safety procedures needed before the final EC2 public-IP demo readiness pass.

This batch is intentionally documentation/procedure only. It does not add paid backup services, does not enable DynamoDB PITR, does not create AWS Backup plans, and does not add new infrastructure unless separately approved after cost review.

## 2. Safety principles

Use these rules before any import, deployment, or recovery operation:

1. **Dry run first.** Any import, S3 sync, or destructive-looking operation must be run in preview/dry-run mode first.
2. **Do not delete DynamoDB tables during normal import/restore.** Restore should be record-level or table-data-level, not table recreation, unless a separate disaster-recovery action is explicitly approved.
3. **Do not reset `rsa_id_counters` downward.** Counters may only move forward or be preserved. Lowering a counter can cause ID collisions.
4. **Keep the S3 media bucket private.** Public display must continue through backend `/api/media/...` routes and Nginx, not public bucket ACLs.
5. **Preserve EC2 release rollback.** Do not overwrite `/opt/rsa-cms/releases/*`; deploy by creating new release folders and switching `/opt/rsa-cms/current`.
6. **Preserve Nginx safety rules.** Keep `/api/media/` before generic `/api/` blocks and keep `client_max_body_size 8m`.
7. **Do not store or paste secrets.** Never commit `.env`, Cognito tokens, bearer tokens, generated temporary passwords, AWS keys, or session output containing secrets.
8. **Keep Free-Tier-first.** Avoid ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, paid notification workflows, or paid backup services unless approved.
9. **Stop EC2 when not actively deploying/testing.**

## 3. Known project resources

Current documented values:

```text
AWS account: 537765358118
AWS region: ap-southeast-1
S3 media bucket: rsa-cms-media-537765358118-ap-southeast-1
EC2 app path: /opt/rsa-cms
Current symlink: /opt/rsa-cms/current
Release folders: /opt/rsa-cms/releases/*
Backend service: rsa-cms-backend
Nginx active site config: /etc/nginx/sites-enabled/rsa-cms.conf
```

Approved launch DynamoDB tables:

```text
rsa_products
rsa_brands
rsa_categories
rsa_key_features
rsa_customers
rsa_bookings
rsa_inquiries
rsa_about
rsa_project_gallery
rsa_services
rsa_contact_us
rsa_id_counters
```

## 4. Before any backup or restore

Capture the current state first.

```bash
export AWS_REGION="ap-southeast-1"
export RSA_BACKUP_ROOT="$HOME/rsa-cms-backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RSA_BACKUP_ROOT"/{dynamodb,s3,ec2,nginx,git}

echo "== AWS caller identity ==" | tee "$RSA_BACKUP_ROOT/00-context.txt"
aws sts get-caller-identity | tee -a "$RSA_BACKUP_ROOT/00-context.txt"

echo "== Git state ==" | tee "$RSA_BACKUP_ROOT/git/git-state.txt"
git status --short | tee -a "$RSA_BACKUP_ROOT/git/git-state.txt"
git branch --show-current | tee -a "$RSA_BACKUP_ROOT/git/git-state.txt"
git rev-parse HEAD | tee -a "$RSA_BACKUP_ROOT/git/git-state.txt"
git log --oneline -10 | tee -a "$RSA_BACKUP_ROOT/git/git-state.txt"
```

On EC2, also capture:

```bash
APP="/opt/rsa-cms"
BACKUP_ROOT="$HOME/rsa-cms-ec2-backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_ROOT"/{release,nginx,systemd}

readlink -f "$APP/current" | tee "$BACKUP_ROOT/release/current-release.txt"
ls -dt "$APP/releases"/* | head -n 20 | tee "$BACKUP_ROOT/release/recent-releases.txt"
systemctl is-active rsa-cms-backend | tee "$BACKUP_ROOT/systemd/backend-status.txt"
sudo nginx -T > "$BACKUP_ROOT/nginx/nginx-full-config.txt" 2>&1 || true
sudo cp /etc/nginx/sites-enabled/rsa-cms.conf "$BACKUP_ROOT/nginx/rsa-cms.conf.active" 2>/dev/null || true
```

## 5. DynamoDB backup procedure

### 5.1 Small demo-data JSON backup

For the current demo-sized dataset, a simple JSON scan export is acceptable.

```bash
export AWS_REGION="ap-southeast-1"
export BACKUP_DIR="$HOME/rsa-cms-backups/$(date -u +%Y%m%dT%H%M%SZ)/dynamodb"
mkdir -p "$BACKUP_DIR"

TABLES=(
  rsa_products
  rsa_brands
  rsa_categories
  rsa_key_features
  rsa_customers
  rsa_bookings
  rsa_inquiries
  rsa_about
  rsa_project_gallery
  rsa_services
  rsa_contact_us
  rsa_id_counters
)

for table in "${TABLES[@]}"; do
  echo "== Backup $table =="
  aws dynamodb scan \
    --region "$AWS_REGION" \
    --table-name "$table" \
    --output json \
    > "$BACKUP_DIR/${table}.scan.json"

  aws dynamodb scan \
    --region "$AWS_REGION" \
    --table-name "$table" \
    --select COUNT \
    --output json \
    > "$BACKUP_DIR/${table}.count.json"
done

ls -lh "$BACKUP_DIR"
```

Notes:

- This is suitable for the current small demo dataset.
- For larger production data, scan output may need pagination handling or a separately approved export process.
- Do not enable paid backup/PITR features unless explicitly approved after cost review.

### 5.2 Verify backup files

```bash
python3 - "$BACKUP_DIR" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
for path in sorted(root.glob("*.scan.json")):
    data = json.loads(path.read_text())
    print(path.name, "items=", data.get("Count"), "scanned=", data.get("ScannedCount"))
PY
```

## 6. DynamoDB restore approach

### 6.1 Preferred restore rule

Use the existing validated import/loaders and templates where possible. Restore should be:

1. Review backup file.
2. Dry-run target changes.
3. Execute only after confirmation.
4. Verify counts and sample records.

Do not truncate tables. Do not delete tables. Do not reset counters downward.

### 6.2 Record-level restore strategy

For a single broken record, prefer a targeted restore:

```bash
aws dynamodb put-item \
  --region ap-southeast-1 \
  --table-name rsa_products \
  --item file://single-product-item.json
```

Before using `put-item`, verify:

- The table name is correct.
- The item key matches the intended record.
- The item JSON is DynamoDB AttributeValue JSON, not plain application JSON.
- `rsa_id_counters` will not be moved backward.

### 6.3 Full table restore is not the normal path

Full table restore should only happen under a separate approved recovery plan. Normal launch/demo recovery should be targeted record updates or a controlled import run.

## 7. `rsa_id_counters` safety

Before any import or restore involving new IDs:

```bash
aws dynamodb scan \
  --region ap-southeast-1 \
  --table-name rsa_id_counters \
  --output json > rsa_id_counters.before.json
```

Rules:

- Never restore an older `rsa_id_counters` value if it is lower than the current value.
- If a counter must be repaired, set it to at least the maximum existing sequence for that prefix/category.
- Preserve category-based product ID prefixes such as `CCTV`, `RECO`, and `PACK`.

## 8. S3 media backup and preservation

### 8.1 List current media objects

```bash
export BUCKET="rsa-cms-media-537765358118-ap-southeast-1"
export AWS_REGION="ap-southeast-1"
export S3_BACKUP_DIR="$HOME/rsa-cms-backups/$(date -u +%Y%m%dT%H%M%SZ)/s3-media"
mkdir -p "$S3_BACKUP_DIR"

aws s3 ls "s3://$BUCKET" --recursive --summarize > "$S3_BACKUP_DIR/s3-object-list.txt"
cat "$S3_BACKUP_DIR/s3-object-list.txt" | tail -n 20
```

### 8.2 Dry-run S3 download backup

```bash
aws s3 sync "s3://$BUCKET" "$S3_BACKUP_DIR/files" --dryrun
```

### 8.3 Execute S3 download backup

Only after reviewing the dry run:

```bash
aws s3 sync "s3://$BUCKET" "$S3_BACKUP_DIR/files"
```

### 8.4 Restore S3 media objects

Dry run first:

```bash
aws s3 sync "$S3_BACKUP_DIR/files" "s3://$BUCKET" --dryrun
```

Execute only after review:

```bash
aws s3 sync "$S3_BACKUP_DIR/files" "s3://$BUCKET"
```

S3 restore rules:

- Do not use public ACLs.
- Do not make the bucket public.
- Do not overwrite current media unless the object keys are confirmed.
- Verify display through `/api/media/...`, not public S3 URLs.

## 9. Git backup and rollback

### 9.1 Before a risky code change

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -10
```

Keep the commit hash of the last known-good state.

### 9.2 Shared branch rollback rule

Prefer a revert commit over rewriting history:

```bash
git revert <bad_commit_sha>
git status --short
git push
```

Avoid `git reset --hard` on a shared branch unless explicitly approved.

### 9.3 Local cleanup before applying a new patch

```bash
git status --short
```

If unexpected changes appear, stop and inspect before applying another batch.

## 10. EC2 release rollback

The EC2 deployment model uses release folders and a current symlink.

### 10.1 Inspect active release

```bash
APP="/opt/rsa-cms"
readlink -f "$APP/current"
ls -dt "$APP/releases"/* | head -n 20
```

### 10.2 Roll back to a previous release

Replace `<previous-release-path>` with a known-good folder from `/opt/rsa-cms/releases`:

```bash
APP="/opt/rsa-cms"
PREVIOUS="<previous-release-path>"

sudo ln -sfn "$PREVIOUS" "$APP/current.new"
sudo mv -Tf "$APP/current.new" "$APP/current"
sudo nginx -t
sudo systemctl reload nginx
```

If backend Python/backend files changed in the release, also restart:

```bash
sudo systemctl restart rsa-cms-backend
systemctl is-active rsa-cms-backend
```

### 10.3 Smoke after rollback

```bash
curl -sS -i http://127.0.0.1/api/health | head -n 20
curl -sS -o /dev/null -w "home=%{http_code}\n" http://127.0.0.1/
curl -sS -o /dev/null -w "products=%{http_code}\n" http://127.0.0.1/products.html
curl -sS -o /dev/null -w "booking=%{http_code}\n" http://127.0.0.1/booking.html
curl -sS -o /dev/null -w "admin-login=%{http_code}\n" http://127.0.0.1/admin/login.html
curl -sS -o /dev/null -w "admin-products=%{http_code}\n" http://127.0.0.1/admin/products.html
```

Expected HTTP values are normally `200` for public/static pages and health checks.

## 11. Nginx backup and rollback

### 11.1 Back up active Nginx config

```bash
NGINX_BACKUP_DIR="$HOME/rsa-cms-nginx-backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$NGINX_BACKUP_DIR"

sudo cp /etc/nginx/sites-enabled/rsa-cms.conf "$NGINX_BACKUP_DIR/rsa-cms.conf.active"
sudo nginx -T > "$NGINX_BACKUP_DIR/nginx-full-config.txt" 2>&1 || true
```

### 11.2 Required Nginx rules to preserve

The active config must preserve:

```text
location ^~ /api/media/ ...
client_max_body_size 8m;
```

The `/api/media/` location must come before generic `/api/` deny/403 blocks.

### 11.3 Test and reload

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 11.4 Restore previous Nginx config

```bash
sudo cp "$NGINX_BACKUP_DIR/rsa-cms.conf.active" /etc/nginx/sites-enabled/rsa-cms.conf
sudo nginx -t
sudo systemctl reload nginx
```

## 12. Import rollback and launch data safety

Before any import:

```bash
aws dynamodb scan --region ap-southeast-1 --table-name rsa_id_counters --output json > rsa_id_counters.before-import.json
```

Required process:

1. Validate templates locally.
2. Run dry-run import.
3. Review warnings/errors and record counts.
4. Take DynamoDB scan backup if replacing real data.
5. Execute import only with explicit approval.
6. Verify public and admin pages after import.

Forbidden by default:

```text
Deleting DynamoDB tables
Dropping/recreating tables
Resetting rsa_id_counters downward
Using --execute without reviewing dry-run output
Overwriting production records without approved overwrite rules
```

## 13. Secrets and credentials handling

Never commit, attach, or paste:

```text
.env files
AWS access keys
Cognito client secrets
JWT / bearer tokens
Admin passwords
Generated temporary passwords
Full SSM session logs containing tokens
Private keys
```

For screenshots/logs:

- Redact Authorization headers.
- Redact tokens and temporary passwords.
- Redact any email/password combo used for admin login.
- Keep one-time temporary password behavior: show once only, then reset if lost.

## 14. Cost-safety checklist

Before extended demo or external testing, confirm:

```text
[ ] EC2 is the only always-on compute service.
[ ] No ALB is running.
[ ] No NAT Gateway is running.
[ ] No RDS database is running.
[ ] No SMS/MFA/paid notification workflow is enabled.
[ ] DynamoDB capacity remains low and intentional.
[ ] S3 media usage is reasonable.
[ ] CloudWatch logs are not configured for excessive retention.
[ ] Billing alerts / budgets have been checked.
[ ] EC2 is stopped when not actively testing/deploying.
```

## 15. Final Batch 60B acceptance checklist

Batch 60B is complete when:

```text
[ ] DynamoDB backup/export/restore approach is documented.
[ ] S3 media preservation/restore approach is documented.
[ ] Git rollback procedure is documented.
[ ] EC2 release rollback procedure is documented.
[ ] Nginx config backup/rollback procedure is documented.
[ ] Import rollback and dry-run-first rules are documented.
[ ] Secret/token/password handling rules are documented.
[ ] Cost-safety reminders are documented.
[ ] Batch 60A handoff notes are documented.
[ ] No new paid backup service or infrastructure was added.
```

## 16. Batch 60A handoff

After Batch 60B, proceed to Batch 60A only after confirming whether Batch 59B is complete or still needs to run.

Batch 60A must confirm:

```text
Active EC2 release
Public website smoke
Lead capture smoke
Admin login/dashboard/catalog/CMS/lead smoke
Admin vs Standard role behavior
Media upload/display behavior
Current demo data sanity
Accepted Batch 60C behavior
EC2 cost-safety state
```

Keep EC2 stopped unless actively deploying or testing.
