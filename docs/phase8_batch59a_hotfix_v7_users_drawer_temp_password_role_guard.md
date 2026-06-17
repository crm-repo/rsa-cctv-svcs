# Phase 8 Batch 59A Hotfix v7 — Users Drawer, Temporary Password, and Standard Role Guard

Status: targeted local UI/auth-front-end hotfix

## Purpose

Clean up Batch 59A Settings > Users after local testing.

## Fixes

- Uses a right-side drawer style for Add/Edit User, aligned with the existing admin catalog/product drawer behavior.
- Keeps create-user errors and the temporary password inside the Add User drawer.
- Prevents the old page-level temporary password panel from showing above the users table.
- Keeps the users return/status message compact in the toolbar-left area, opposite Refresh Users and Add User.
- Hides Settings navigation for non-Admin/Standard users at the frontend shell level.
- Prevents the Settings page content flash for non-Admin users by gating it before redirect.

## Not changed

- No backend route change.
- No Cognito group/IAM policy change.
- No DynamoDB users table.
- No EC2/deployment change.
