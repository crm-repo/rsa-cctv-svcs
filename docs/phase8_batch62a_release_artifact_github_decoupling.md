# Phase 8 Batch 62A — Release Artifact / GitHub Decoupling Safety

Date: 2026-06-26  
Status: Deferred / post-demo pre-launch safety batch  
Scope: RSA CMS / Mini-CRM release packaging, deployment independence, and runtime dependency hardening

## 1. Purpose

Batch 62A formally adds a pre-launch safety step to ensure the production runtime does not depend on GitHub downloads, moving Git branches, raw GitHub URLs, or GitHub credentials.

GitHub remains the source-control system and can still be used during development. However, after a release is approved for production/go-live, the live EC2 application should run from local EC2 release folders and a controlled release artifact, not from GitHub at runtime.

## 2. Why this batch is needed

During demo and development deployments, EC2 sometimes downloaded files or branch archives from GitHub using a commit hash or branch reference. This is useful for repeatable development deployment, but it should not become a production runtime dependency.

For go-live, the project should be able to keep serving the website/admin application even if:

- GitHub is unavailable.
- A branch changes after deployment.
- GitHub tokens rotate or are revoked.
- Internet access to GitHub is temporarily interrupted.
- A rollback is needed without re-downloading code from GitHub.

## 3. Scope

Batch 62A should cover:

1. Creating a tagged release, for example `v1.0.0`.
2. Creating a release artifact zip/tarball from the approved source tree.
3. Storing a copy of the artifact outside GitHub deployment downloads, such as private S3 or a controlled local/offline backup.
4. Deploying from the release artifact instead of `raw.githubusercontent.com` or branch archives.
5. Preserving `/opt/rsa-cms/releases/*` and `/opt/rsa-cms/current` rollback behavior.
6. Verifying no runtime file requires GitHub URLs or GitHub credentials.
7. Confirming no GitHub token is stored in frontend files, Nginx config, systemd unit files, backend `.env`, or public JavaScript.

## 4. Out of scope

Batch 62A does not require:

- Removing GitHub as source control.
- Changing the application code architecture.
- Adding paid deployment tooling.
- Adding CI/CD unless separately approved.
- Adding a second EC2 instance, ALB, NAT Gateway, RDS, paid WAF, or any other paid infrastructure.

## 5. Recommended release artifact process

### 5.1 Before packaging

Confirm the approved local source tree:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log --oneline -10
```

The working tree should be clean before packaging a launch artifact.

### 5.2 Create a tag

Example:

```bash
git tag -a v1.0.0 -m "RSA CMS production release v1.0.0"
git push origin v1.0.0
```

The tag is for traceability. The production EC2 runtime should still run from the deployed artifact and local release folder, not from GitHub directly.

### 5.3 Create the artifact

Example from the repository root:

```bash
RELEASE_NAME="rsa-cms-v1.0.0"
mkdir -p /tmp/$RELEASE_NAME

rsync -a   --exclude='.git'   --exclude='.env'   --exclude='__pycache__'   --exclude='.venv'   --exclude='node_modules'   ./ /tmp/$RELEASE_NAME/

cd /tmp
zip -r ${RELEASE_NAME}.zip $RELEASE_NAME
sha256sum ${RELEASE_NAME}.zip > ${RELEASE_NAME}.zip.sha256
```

Do not include local secrets, `.env`, AWS credentials, Cognito tokens, temporary passwords, or session logs.

## 6. Artifact storage options

Preferred low-cost options:

```text
Option A: Private S3 deploy/artifact prefix
Option B: Controlled local/offline backup copy
Option C: Both private S3 and local/offline backup
```

If using S3, keep the bucket private. Do not make release artifacts public.

Example:

```bash
aws s3 cp /tmp/rsa-cms-v1.0.0.zip   s3://rsa-cms-media-537765358118-ap-southeast-1/_releases/rsa-cms-v1.0.0.zip   --region ap-southeast-1

aws s3 cp /tmp/rsa-cms-v1.0.0.zip.sha256   s3://rsa-cms-media-537765358118-ap-southeast-1/_releases/rsa-cms-v1.0.0.zip.sha256   --region ap-southeast-1
```

## 7. Deployment model

Production deployment should continue using the existing release-folder model:

```text
/opt/rsa-cms/releases/<release-folder>
/opt/rsa-cms/current -> /opt/rsa-cms/releases/<release-folder>
```

Do not deploy by editing `/opt/rsa-cms/current` directly.

For frontend-only artifact changes, reload Nginx after switching the symlink:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

For backend changes, restart the backend service after switching the symlink:

```bash
sudo systemctl restart rsa-cms-backend
systemctl is-active rsa-cms-backend
curl -sS -i http://127.0.0.1/api/health | head -n 20
```

## 8. Runtime GitHub dependency check

Before production go-live, run this on EC2:

```bash
APP="/opt/rsa-cms"

echo "== Active release =="
readlink -f "$APP/current"

echo
 echo "== Check runtime files for GitHub references =="
sudo grep -R -nE "github.com|raw.githubusercontent.com|api.github.com"   "$APP/current"   /etc/nginx/sites-enabled   /etc/systemd/system/rsa-cms-backend.service*   2>/dev/null || true
```

Expected result: no GitHub references in active runtime files.

Deploy scripts, old logs, or local operator notes outside the active runtime can mention GitHub, but live application files, Nginx config, systemd service files, public JavaScript, and runtime environment should not require GitHub.

## 9. Token and secret checks

Before launch, verify:

- No GitHub token in frontend files.
- No GitHub token in Nginx config.
- No GitHub token in systemd service files.
- No GitHub token in backend runtime environment.
- No Cognito bearer token or temporary password committed to repository or artifact.
- No `.env` file included in release artifacts.

## 10. Rollback rule

Rollback should use the local EC2 release folder, not GitHub:

```bash
APP="/opt/rsa-cms"
PREVIOUS="/opt/rsa-cms/releases/<known-good-release>"

sudo ln -sfn "$PREVIOUS" "$APP/current.new"
sudo mv -Tf "$APP/current.new" "$APP/current"
sudo nginx -t
sudo systemctl reload nginx
```

If backend files changed:

```bash
sudo systemctl restart rsa-cms-backend
systemctl is-active rsa-cms-backend
```

## 11. Acceptance checklist

Batch 62A is complete when:

```text
[ ] Approved release tag exists.
[ ] Release artifact zip/tarball exists.
[ ] Artifact checksum exists.
[ ] Artifact copy is stored outside GitHub deployment downloads.
[ ] EC2 deploy from artifact is documented or scripted.
[ ] Runtime GitHub grep check is clean or only finds non-runtime notes/scripts.
[ ] No GitHub token is present in runtime files.
[ ] No secrets are included in the artifact.
[ ] /opt/rsa-cms/releases rollback remains available.
[ ] /opt/rsa-cms/current points to the approved release.
```

## 12. Placement in post-demo pipeline

Recommended post-demo/pre-launch order:

```text
1. Targeted demo feedback/hotfixes, if any
2. Batch 62A — Release Artifact / GitHub Decoupling Safety
3. Batch 57 — SEO metadata/page titles/canonical/Open Graph/sitemap/robots after final domain is known
4. Batch 61 — Route 53 + ACM + CloudFront + EC2 Nginx origin
5. Batch 62 — Final launch/cutover checklist
```

## 13. Cost-safety reminder

Batch 62A should preserve the AWS Free-Tier-first strategy. It should not add ALB, NAT Gateway, RDS, paid WAF, extra always-on EC2 instances, paid CI/CD, or paid backup/deployment tooling unless separately approved after cost review.
