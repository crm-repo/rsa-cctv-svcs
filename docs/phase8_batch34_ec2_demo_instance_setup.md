# Phase 8 Batch 34 — EC2 Demo Instance and Security Group Setup

## Purpose

Create one temporary EC2 demo instance for the RSA CMS backend using the safest public-IP-first deployment path.

This batch creates only the minimum EC2 resources needed for the first server smoke test:

- one EC2 instance
- one security group
- one key pair
- no Elastic IP
- no load balancer
- no NAT Gateway
- no RDS
- no Route 53/domain
- no SMS/MFA/paid notification features

The public frontend can continue to be tested separately. This batch is for preparing the backend server environment first.

## Confirmed baseline before Batch 34

| Item | Expected |
|---|---|
| AWS account | `537765358118` |
| AWS region | `ap-southeast-1` |
| CLI user | `rsa-cms-cli-user` |
| Existing EC2 instances | `0` |
| Existing RSA security groups | `0` |
| EC2 backend role | `rsa-cms-ec2-backend-role` |
| EC2 role DynamoDB policy | `rsa-cms-ec2-instance-dynamodb-policy` |
| Deployment policy | `rsa-cms-ec2-deployment-minimum-policy` attached to CLI/deployment user |
| Billing alert | manually confirmed before launch |

## Cost-safety notes

1. Use only one small Free-Tier-labeled Linux EC2 instance.
2. Keep the instance stopped when not testing.
3. Do not allocate an Elastic IP.
4. The instance public IPv4 address is temporary and can change after stop/start.
5. Delete/terminate demo resources after the demo period if no longer needed.
6. Keep EBS storage minimal, normally `8 GiB`.

AWS currently charges for public IPv4 addresses in many cases, with Free Tier coverage depending on account eligibility and monthly usage. Keep the instance online only when needed for demo/testing.

## Resource names for Batch 34

Use these exact names so scripts and future steps can find the resources:

| Resource | Name |
|---|---|
| EC2 instance name tag | `rsa-cms-demo-backend` |
| Security group name | `rsa-cms-demo-backend-sg` |
| Key pair name | `rsa-cms-demo-key` |
| IAM role / instance profile | `rsa-cms-ec2-backend-role` |

## Step 1 — Get your current public IP

On your Windows machine, open PowerShell:

```powershell
(Invoke-RestMethod https://checkip.amazonaws.com).Trim()
```

Write it down as:

```text
YOUR_PUBLIC_IP/32
```

Example:

```text
203.0.113.10/32
```

Do not use `0.0.0.0/0` for SSH or port 8000.

## Step 2 — Create a key pair

AWS Console:

```text
EC2 → Key pairs → Create key pair
```

Recommended values:

| Field | Value |
|---|---|
| Name | `rsa-cms-demo-key` |
| Key pair type | `RSA` |
| Private key file format | `.pem` |

Download the `.pem` file and store it outside the Git project, for example:

```text
C:\Users\johnb\.ssh\rsa-cms-demo-key.pem
```

Do not commit the key file.

## Step 3 — Create the security group

AWS Console:

```text
EC2 → Security Groups → Create security group
```

Recommended values:

| Field | Value |
|---|---|
| Security group name | `rsa-cms-demo-backend-sg` |
| Description | `RSA CMS temporary EC2 backend demo security group` |
| VPC | Default VPC in `ap-southeast-1` |

Inbound rules:

| Type | Protocol | Port | Source | Purpose |
|---|---|---:|---|---|
| SSH | TCP | `22` | `YOUR_PUBLIC_IP/32` | temporary server access |
| Custom TCP | TCP | `8000` | `YOUR_PUBLIC_IP/32` | temporary FastAPI smoke test only |

Do **not** add these rules at this stage:

| Bad rule | Why |
|---|---|
| All traffic from `0.0.0.0/0` | unsafe |
| SSH from `0.0.0.0/0` | unsafe |
| Port `8000` from `0.0.0.0/0` | unsafe |
| RDP `3389` | not needed |
| HTTP `80` public | later only, after nginx/public frontend plan |
| HTTPS `443` public | later only, after domain/SSL plan |

Outbound rules can stay as the default AWS outbound rule.

Add tags if the console asks:

| Key | Value |
|---|---|
| `Project` | `rsa-cms` |
| `Phase` | `phase8-batch34` |
| `Environment` | `demo` |
| `Owner` | `rsa` |

## Step 4 — Launch the EC2 instance

AWS Console:

```text
EC2 → Instances → Launch instances
```

Use these values:

| Section | Value |
|---|---|
| Name | `rsa-cms-demo-backend` |
| Region | `ap-southeast-1` |
| AMI | Ubuntu Server LTS, x86_64, Free-Tier-labeled in the console |
| Instance type | Free-Tier-labeled micro type available in the console |
| Key pair | `rsa-cms-demo-key` |
| Network | Default VPC |
| Subnet | Any default public subnet in `ap-southeast-1` |
| Auto-assign public IP | Enabled |
| Firewall/security group | Existing security group: `rsa-cms-demo-backend-sg` |
| IAM instance profile | `rsa-cms-ec2-backend-role` |
| Storage | `8 GiB`, one root volume only |
| Shutdown behavior | Stop |
| Termination protection | Optional; off is okay for temporary demo |

Do not enable:

```text
Elastic IP
Load balancer
Auto Scaling group
Additional EBS volumes
Dedicated host/instance
RDS
NAT Gateway
```

## Step 5 — Verify the instance in AWS Console

After launch, open:

```text
EC2 → Instances → rsa-cms-demo-backend
```

Confirm:

| Check | Expected |
|---|---|
| Instance state | `Running` |
| Instance type | small Free-Tier-labeled micro instance |
| Public IPv4 address | present |
| Security group | `rsa-cms-demo-backend-sg` |
| IAM role | `rsa-cms-ec2-backend-role` |
| Storage | one small root volume |
| Elastic IP | none |

Copy the public IPv4 address. It will be used for SSH.

## Step 6 — Run local verification script

From your project backend folder:

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project\backend"
venv\Scripts\activate

python scripts\check_ec2_demo_instance_status.py
```

Expected:

```text
Found EC2 demo instance: rsa-cms-demo-backend
State: running
Security group: rsa-cms-demo-backend-sg
IAM role/profile includes: rsa-cms-ec2-backend-role
No public inbound rule for SSH/8000/80/443/RDP
```

If the script says no instance was found, wait one minute and re-run.

## Step 7 — SSH to the instance

Set private-key permissions on Windows PowerShell:

```powershell
icacls "$env:USERPROFILE\.ssh\rsa-cms-demo-key.pem" /inheritance:r
icacls "$env:USERPROFILE\.ssh\rsa-cms-demo-key.pem" /grant:r "$($env:USERNAME):(R)"
```

SSH:

```powershell
ssh -i "$env:USERPROFILE\.ssh\rsa-cms-demo-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

Replace:

```text
<EC2_PUBLIC_IP>
```

with the instance public IPv4 address.

## Step 8 — Basic server readiness check

Inside the EC2 SSH session:

```bash
hostname
whoami
python3 --version || true
curl --version || true
```

Then confirm the EC2 role is visible through instance metadata:

```bash
TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

Expected output includes:

```text
rsa-cms-ec2-backend-role
```

If it does not show the role, stop and check the instance IAM role/profile in the AWS Console.

## Step 9 — Stop the instance when not testing

AWS Console:

```text
EC2 → Instances → rsa-cms-demo-backend → Instance state → Stop instance
```

Do not leave the demo instance running when not testing.

## Batch 34 completion criteria

Batch 34 is complete when:

- `rsa-cms-demo-backend-sg` exists.
- `rsa-cms-demo-backend` exists and can run.
- Instance has temporary public IPv4.
- SSH works from your IP only.
- Instance role shows `rsa-cms-ec2-backend-role` in metadata.
- Local script `check_ec2_demo_instance_status.py` passes without risky inbound-rule warnings.
- No Elastic IP, ALB, NAT Gateway, RDS, Route 53, SMS, or paid notification drift was introduced.

## Next batch after this

The next controlled batch should deploy the backend app onto the EC2 server and run a temporary FastAPI health smoke test against the public IP.
