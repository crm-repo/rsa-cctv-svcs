# Phase 8 Batch 59A Hotfix v9 — Users Role Labels and Reset Drawer Spacing

Scope: local admin UI polish only.

Changes:
- Display `Admin` as `System Administrator`.
- Display `Standard` as `Standard User`.
- Tighten Reset Password drawer spacing so content starts higher and reads like the other admin drawers.
- Keep temporary reset password inside the drawer.
- Disable the login email field during Cognito first-login/new-password-required reset flow.

No backend, IAM, Cognito, DynamoDB, S3, EC2, Route 53, CloudFront, or notification changes.
