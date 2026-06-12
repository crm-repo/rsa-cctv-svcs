param(
    [Parameter(Mandatory = $true)]
    [string]$KeyPath
)

Write-Host "RSA CMS Batch 35 - Windows SSH key ACL preparation"
Write-Host "Key path: $KeyPath"

if (!(Test-Path $KeyPath)) {
    Write-Error "Key file not found: $KeyPath"
    exit 1
}

$currentUser = "$env:USERDOMAIN\$env:USERNAME"

icacls $KeyPath /inheritance:r | Out-Host
icacls $KeyPath /grant:r "$currentUser:R" | Out-Host
icacls $KeyPath /remove "Users" "Authenticated Users" "Everyone" 2>$null | Out-Host

Write-Host "Done. Try SSH again."
