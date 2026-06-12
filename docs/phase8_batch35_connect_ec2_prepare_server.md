# Phase 8 Batch 35 — Connect to EC2 and Prepare Server Environment

## Goal

Batch 35 connects to the Batch 34 EC2 demo instance and prepares a basic server environment for the RSA CMS backend deployment.

This batch does **not** deploy the app yet. It only prepares the EC2 instance.

## Safety rules

- Keep EC2 running only while working on this batch.
- Do not use the AWS root account for EC2 work.
- Do not store AWS access keys on EC2.
- Use the EC2 IAM instance profile `rsa-cms-ec2-backend-role`.
- Do not open `0.0.0.0/0` for SSH or backend port 8000.
- Do not create Elastic IP, Route 53, ALB, NAT Gateway, RDS, SMS, or paid notification resources.
- Do not commit `.pem`, `.env`, or server secrets.

## Expected EC2 details

| Item | Expected value |
|---|---|
| Region | `ap-southeast-1` |
| Instance name | `rsa-cms-demo-backend` |
| Instance type | `t3.micro` |
| Key pair | `rsa-cms-demo-key` |
| IAM instance profile | `rsa-cms-ec2-backend-role` |
| Security group | `rsa-cms-demo-backend-sg` |
| SSH source | Your public IP `/32` only |
| TCP 8000 source | Your public IP `/32` only |

## Step 1 — Run local SSH preflight

From Windows PowerShell:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_ssh_preflight.py --key-path "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem"
```

The script should show the running EC2 instance and print the SSH command to use.

## Step 2 — Prepare the `.pem` file permissions on Windows

If SSH complains about the private key permissions, run:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"

powershell -ExecutionPolicy Bypass -File deploy\ec2\windows_prepare_ssh_key_acl.ps1 -KeyPath "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem"
```

## Step 3 — SSH into EC2

Use the command printed by the preflight script. Usually:

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" ec2-user@<PUBLIC_IPV4>
```

If `ec2-user` fails with a user error, try:

```powershell
ssh -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" ubuntu@<PUBLIC_IPV4>
```

For the Batch 34 Amazon Linux-style launch, `ec2-user` is expected.

## Step 4 — Copy the server scripts to EC2

From local Windows PowerShell, replace `<PUBLIC_IPV4>` with the instance public IP:

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" `
  "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\deploy\ec2\bootstrap_rsa_cms_server.sh" `
  ec2-user@<PUBLIC_IPV4>:/tmp/bootstrap_rsa_cms_server.sh

scp -i "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem" `
  "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\deploy\ec2\check_server_environment.sh" `
  ec2-user@<PUBLIC_IPV4>:/tmp/check_server_environment.sh
```

If using Ubuntu, replace `ec2-user` with `ubuntu`.

## Step 5 — Run the server bootstrap on EC2

Inside the EC2 SSH session:

```bash
chmod +x /tmp/bootstrap_rsa_cms_server.sh /tmp/check_server_environment.sh
/tmp/bootstrap_rsa_cms_server.sh
/tmp/check_server_environment.sh
```

Expected results:

- `/opt/rsa-cms` exists.
- `/opt/rsa-cms/venv` exists.
- Python, pip, Git, curl, and unzip are available.
- The EC2 IAM role metadata is visible.
- No AWS access keys are stored on EC2.

## Step 6 — Final local verification

After the EC2 preparation finishes, run this locally again:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_ssh_preflight.py --key-path "C:\Users\johnb\Downloads\AWS Project\rsa-cms-demo-key.pem"
```

## End-of-batch stop reminder

At the end of Batch 35, the EC2 instance can normally be stopped until the next deployment batch.

Stop it from:

```text
EC2 → Instances → rsa-cms-demo-backend → Instance state → Stop instance
```

Do not terminate it unless the project explicitly decides to rebuild the demo server.
