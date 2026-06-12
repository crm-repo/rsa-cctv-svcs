# Batch 34 EC2 Demo Instance Quick Steps

Use this only after Batch 31, 32, and 33 checks have passed.

## Names

```text
Instance: rsa-cms-demo-backend
Security group: rsa-cms-demo-backend-sg
Key pair: rsa-cms-demo-key
IAM role/profile: rsa-cms-ec2-backend-role
Region: ap-southeast-1
```

## PowerShell — get your public IP

```powershell
(Invoke-RestMethod https://checkip.amazonaws.com).Trim()
```

Use the result as `/32` in security group inbound rules.

## Inbound rules

```text
SSH         TCP 22     YOUR_PUBLIC_IP/32
Custom TCP  TCP 8000   YOUR_PUBLIC_IP/32
```

No public `0.0.0.0/0` inbound rules in Batch 34.

## Launch instance

In EC2 Console, launch one Ubuntu Server LTS Free-Tier-labeled micro instance with:

```text
Security group: rsa-cms-demo-backend-sg
IAM role/profile: rsa-cms-ec2-backend-role
Storage: 8 GiB
Public IP: enabled
Elastic IP: none
```

## Check from local project

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate
python scripts\check_ec2_demo_instance_status.py
```

## SSH

```powershell
ssh -i "$env:USERPROFILE\.ssh\rsa-cms-demo-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

## Stop when done

Stop the instance when not testing.
