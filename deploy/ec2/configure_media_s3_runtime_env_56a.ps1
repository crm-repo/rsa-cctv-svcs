param(
    [Parameter(Mandatory = $true)]
    [string]$KeyPath,

    [Parameter(Mandatory = $true)]
    [string]$HostName,

    [string]$SshUser = "ubuntu",
    [string]$BucketName = "rsa-cms-media-537765358118-ap-southeast-1",
    [string]$Region = "ap-southeast-1",
    [string]$MaxUploadMb = "5"
)

$ErrorActionPreference = "Stop"

Write-Host "RSA CMS Batch 56A - Configure EC2 backend media S3 runtime env"
Write-Host "Target: $SshUser@$HostName"
Write-Host "Bucket: $BucketName"
Write-Host "Region: $Region"
Write-Host "No AWS keys are written. EC2 must use its instance profile role."

if (!(Test-Path $KeyPath)) {
    throw "Key file not found: $KeyPath"
}

$remoteScript = @'
set -euo pipefail
ENV_FILE=/opt/rsa-cms/runtime/backend.env
BACKUP=/opt/rsa-cms/runtime/backend.env.batch56a-s3.$(date -u +%Y%m%d%H%M%S).bak
sudo test -f "$ENV_FILE"
sudo cp "$ENV_FILE" "$BACKUP"
echo "backup_created: $BACKUP"

sudo python3 - <<'PYREMOTE'
from pathlib import Path

env_file = Path('/opt/rsa-cms/runtime/backend.env')
updates = {
    'RSA_MEDIA_STORAGE_MODE': '__BUCKET_MODE__',
    'RSA_MEDIA_S3_BUCKET': '__BUCKET_NAME__',
    'RSA_MEDIA_MAX_UPLOAD_MB': '__MAX_UPLOAD_MB__',
    'AWS_DEFAULT_REGION': '__REGION__',
    'AWS_REGION': '__REGION__',
}
lines = env_file.read_text(encoding='utf-8').splitlines()
seen = set()
out = []
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith('#') or '=' not in stripped:
        out.append(line)
        continue
    key = stripped.split('=', 1)[0]
    if key in updates:
        out.append(f'{key}={updates[key]}')
        seen.add(key)
    else:
        out.append(line)
for key, value in updates.items():
    if key not in seen:
        out.append(f'{key}={value}')
env_file.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')
PYREMOTE

sudo chmod 640 "$ENV_FILE"
sudo systemctl restart rsa-cms-backend.service
sleep 4
sudo systemctl --no-pager --full status rsa-cms-backend.service || true

echo "runtime_env_media_lines:"
sudo grep -E '^(RSA_MEDIA_STORAGE_MODE|RSA_MEDIA_S3_BUCKET|RSA_MEDIA_MAX_UPLOAD_MB|AWS_DEFAULT_REGION|AWS_REGION)=' "$ENV_FILE"
'@

$remoteScript = $remoteScript.Replace('__BUCKET_MODE__', 's3')
$remoteScript = $remoteScript.Replace('__BUCKET_NAME__', $BucketName)
$remoteScript = $remoteScript.Replace('__MAX_UPLOAD_MB__', $MaxUploadMb)
$remoteScript = $remoteScript.Replace('__REGION__', $Region)

$ssh = Get-Command ssh -ErrorAction Stop
& $ssh.Source -i $KeyPath "${SshUser}@${HostName}" $remoteScript
if ($LASTEXITCODE -ne 0) { throw "remote EC2 media S3 env configuration failed" }

Write-Host "Batch 56A EC2 media S3 runtime env configuration completed."
