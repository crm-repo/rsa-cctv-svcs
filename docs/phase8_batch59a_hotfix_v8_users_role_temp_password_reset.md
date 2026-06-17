# Phase 8 Batch 59A Hotfix v8 — Users Role Display and Temporary Password Drawer

Status: targeted local hotfix

## Fixes

- Top-right admin user card role is derived from Cognito Groups instead of static `Admin` text.
- Standard users remain hidden from Settings navigation.
- Reset Password now opens a drawer and shows the one-time temporary password inside that drawer.
- Add User still shows the one-time temporary password inside the Add User drawer.
- Keeps Users table Full Name based and does not add a DynamoDB users table.

## Not changed

- No backend route change.
- No IAM/Cognito group setup change.
- No DynamoDB/S3/EC2/deployment change.
