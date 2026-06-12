# Phase 8 Batch 36 — Deployment Checklist

## Before deployment

- [ ] EC2 instance `rsa-cms-demo-backend` is started only for this work session.
- [ ] Current public IPv4 is confirmed after start.
- [ ] SSH works using `ubuntu@<PUBLIC_IPV4>`.
- [ ] Security group allows TCP `22` only from your current IP `/32`.
- [ ] Security group allows TCP `8000` only from your current IP `/32`.
- [ ] Batch 35 server environment check previously passed.
- [ ] Latest local changes are committed before `git archive` deployment.

## During deployment

- [ ] Clean Git archive created from `HEAD`.
- [ ] Release zip uploaded to EC2.
- [ ] Release extracted under `/opt/rsa-cms/releases/<timestamp>`.
- [ ] `/opt/rsa-cms/current` points to the latest release.
- [ ] Backend requirements installed in `/opt/rsa-cms/venv`.
- [ ] Runtime env file exists at `/opt/rsa-cms/runtime/backend.env`.
- [ ] Runtime mode is `RSA_REPOSITORY_MODE=dynamodb`.
- [ ] No AWS access keys are stored on EC2.
- [ ] `rsa-cms-backend.service` is installed and enabled.
- [ ] `rsa-cms-backend.service` is active/running.

## Verification

- [ ] Local EC2 curl works: `curl http://127.0.0.1:8000/api/health`.
- [ ] Public local machine curl works: `curl http://<PUBLIC_IPV4>:8000/api/health`.
- [ ] Public read API smoke checks pass or show only understood data/config issues.
- [ ] Instance profile role is visible as `rsa-cms-ec2-backend-role`.
- [ ] Service logs show no repeated crash loop.

## Do not do in Batch 36

- [ ] Do not open `8000`, `80`, or `443` to `0.0.0.0/0`.
- [ ] Do not create Elastic IP.
- [ ] Do not create Route 53 records.
- [ ] Do not create ALB, NAT Gateway, RDS, SMS, or paid notifications.
- [ ] Do not enable public admin access until Cognito/JWT enforcement is ready.

## End of Batch 36

- [ ] Commit/push Batch 36 helper files.
- [ ] Stop EC2 if not immediately starting Batch 37.
