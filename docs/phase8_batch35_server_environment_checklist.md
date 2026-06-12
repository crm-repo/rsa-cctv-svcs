# Phase 8 Batch 35 — Server Environment Checklist

## Before SSH

- [ ] EC2 instance `rsa-cms-demo-backend` is running only for this work session.
- [ ] Security group allows SSH `22` only from your current IP `/32`.
- [ ] Security group allows TCP `8000` only from your current IP `/32`.
- [ ] Key file `rsa-cms-demo-key.pem` is saved securely and not inside the Git repository.
- [ ] Local preflight script finds the instance and prints the SSH command.

## After SSH

- [ ] SSH works using `ec2-user@<PUBLIC_IPV4>` or the correct AMI user.
- [ ] No AWS access keys are copied to EC2.
- [ ] `/opt/rsa-cms` exists.
- [ ] `/opt/rsa-cms/backend` exists.
- [ ] `/opt/rsa-cms/frontend` exists.
- [ ] `/opt/rsa-cms/logs` exists.
- [ ] `/opt/rsa-cms/venv` exists.
- [ ] Python is installed.
- [ ] pip is installed.
- [ ] Git is installed.
- [ ] curl and unzip are installed.
- [ ] EC2 instance profile metadata is visible.
- [ ] AWS CLI is present or clearly marked optional/missing.

## Do not do in Batch 35

- [ ] Do not deploy backend code yet.
- [ ] Do not configure public admin access yet.
- [ ] Do not open port `80`, `443`, or `8000` to `0.0.0.0/0`.
- [ ] Do not create Elastic IP.
- [ ] Do not create Route 53 record.
- [ ] Do not create ALB, NAT Gateway, RDS, SMS, or paid notifications.

## End of Batch 35

- [ ] Capture the output of `/tmp/check_server_environment.sh`.
- [ ] Confirm next batch needed before keeping EC2 running.
- [ ] Stop EC2 if no longer actively testing.
