param(
    [Parameter(Mandatory = $true)]
    [string]$KeyPath,

    [Parameter(Mandatory = $true)]
    [string]$HostName,

    [string]$SshUser = "ubuntu",

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

Write-Host "RSA CMS Batch 36 - Deploy release package to EC2"
Write-Host "Project root: $ProjectRoot"
Write-Host "EC2 target: $SshUser@$HostName"
Write-Host "Key path: $KeyPath"
Write-Host ""

if (!(Test-Path $KeyPath)) {
    throw "Key file not found: $KeyPath"
}

if (!(Test-Path (Join-Path $ProjectRoot ".git"))) {
    throw "ProjectRoot does not look like the Git project root: $ProjectRoot"
}

$git = Get-Command git -ErrorAction Stop
$scp = Get-Command scp -ErrorAction Stop
$ssh = Get-Command ssh -ErrorAction Stop

$deployDir = Join-Path $ProjectRoot "deploy\ec2"
$installScript = Join-Path $deployDir "install_rsa_cms_release.sh"
$checkScript = Join-Path $deployDir "check_rsa_cms_app_runtime.sh"
$serviceTemplate = Join-Path $deployDir "rsa-cms-backend.service"

foreach ($file in @($installScript, $checkScript, $serviceTemplate)) {
    if (!(Test-Path $file)) {
        throw "Required deploy file missing: $file"
    }
}

$packagePath = Join-Path $env:TEMP ("rsa-cms-release-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".zip")

Write-Host "Creating clean Git archive package..."
& $git.Source -C $ProjectRoot archive --format=zip HEAD -o $packagePath
if ($LASTEXITCODE -ne 0) { throw "git archive failed" }
Write-Host "Created: $packagePath"

Write-Host "Uploading release package and deployment scripts..."
& $scp.Source -i $KeyPath $packagePath "${SshUser}@${HostName}:/tmp/rsa-cms-release.zip"
if ($LASTEXITCODE -ne 0) { throw "scp release package failed" }

& $scp.Source -i $KeyPath $installScript "${SshUser}@${HostName}:/tmp/install_rsa_cms_release.sh"
if ($LASTEXITCODE -ne 0) { throw "scp install script failed" }

& $scp.Source -i $KeyPath $checkScript "${SshUser}@${HostName}:/tmp/check_rsa_cms_app_runtime.sh"
if ($LASTEXITCODE -ne 0) { throw "scp runtime check script failed" }

& $scp.Source -i $KeyPath $serviceTemplate "${SshUser}@${HostName}:/tmp/rsa-cms-backend.service"
if ($LASTEXITCODE -ne 0) { throw "scp service file failed" }

Write-Host "Running remote installer..."
& $ssh.Source -i $KeyPath "${SshUser}@${HostName}" "chmod +x /tmp/install_rsa_cms_release.sh /tmp/check_rsa_cms_app_runtime.sh && sudo /tmp/install_rsa_cms_release.sh"
if ($LASTEXITCODE -ne 0) { throw "remote install failed" }

Write-Host ""
Write-Host "Batch 36 deployment command completed."
Write-Host "Next: SSH into the server and run:"
Write-Host "  /tmp/check_rsa_cms_app_runtime.sh"
Write-Host ""
Write-Host "You can also test from local PowerShell after service starts:"
Write-Host "  curl http://$HostName`:8000/api/health"
