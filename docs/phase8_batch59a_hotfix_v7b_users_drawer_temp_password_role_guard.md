# Phase 8 Batch 59A Hotfix v7B — Users Drawer, Temporary Password, and Standard Role Guard

Status: targeted local UI/auth-front-end hotfix

## Purpose

Corrects the v7 apply script syntax error and applies the intended Settings > Users cleanup.

## Fixes

- Add/Edit User uses the right-side drawer-style admin modal pattern.
- Create-user errors and generated temporary password remain inside the Add User drawer.
- The old page-level temporary-password panel above the users table remains hidden.
- Users status message stays compact in the toolbar-left area, opposite Refresh Users and Add User.
- Settings navigation is hidden for non-Admin users.
- Standard users are redirected away from Settings without showing the Settings content first.

## Not changed

- No backend route change.
- No Cognito group/IAM policy change.
- No DynamoDB users table.
- No S3 or EC2/deployment change.
