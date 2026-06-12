# Batch 35 — Connect and Prepare EC2 Server

This folder contains safe helper scripts for the Batch 35 EC2 server-preparation step.

## Files

- `bootstrap_rsa_cms_server.sh` — run on EC2 to install basic packages and create `/opt/rsa-cms` folders.
- `check_server_environment.sh` — run on EC2 to verify the prepared server environment.
- `windows_prepare_ssh_key_acl.ps1` — run locally on Windows only if SSH rejects the `.pem` key permissions.

## Local SSH preflight

From the backend folder:

```powershell
python scripts\check_ec2_ssh_preflight.py --key-path "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem"
```

## Copy scripts to EC2

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" deploy\ec2\bootstrap_rsa_cms_server.sh ec2-user@<PUBLIC_IPV4>:/tmp/bootstrap_rsa_cms_server.sh
scp -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" deploy\ec2\check_server_environment.sh ec2-user@<PUBLIC_IPV4>:/tmp/check_server_environment.sh
```

## Run on EC2

```bash
chmod +x /tmp/bootstrap_rsa_cms_server.sh /tmp/check_server_environment.sh
/tmp/bootstrap_rsa_cms_server.sh
/tmp/check_server_environment.sh
```

## Stop reminder

After Batch 35 is done, stop the EC2 instance unless the next batch starts immediately.
