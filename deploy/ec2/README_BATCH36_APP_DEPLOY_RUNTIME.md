# Batch 36 — EC2 App Deploy and Runtime

## Files

- `deploy_rsa_cms_release_to_ec2.ps1` — local Windows deployment helper.
- `install_rsa_cms_release.sh` — remote EC2 installer run with sudo.
- `check_rsa_cms_app_runtime.sh` — remote EC2 read-only runtime check.
- `rsa-cms-backend.service` — systemd service file for FastAPI backend.
- `backend/scripts/check_ec2_app_runtime_status.py` — local read-only EC2/app status check.

## Standard flow

1. Start EC2.
2. Get current public IPv4.
3. Deploy:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

powershell -ExecutionPolicy Bypass -File .\deploy\ec2\deploy_rsa_cms_release_to_ec2.ps1 `
  -KeyPath "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" `
  -HostName "<PUBLIC_IPV4>" `
  -SshUser "ubuntu"
```

4. SSH and check:

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
```

```bash
/tmp/check_rsa_cms_app_runtime.sh
```

## Stop reminder

At the end of Batch 36, stop EC2 unless Batch 37 starts immediately.
