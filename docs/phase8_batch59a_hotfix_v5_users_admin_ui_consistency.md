# Phase 8 Batch 59A Hotfix v5 — Users Admin UI Consistency

Status: targeted local UI hotfix

## Purpose

Normalize Settings > Users behavior with the rest of the admin UI after local Batch 59A testing.

## Fixes

- Moves the users return/status message into the toolbar row on the left.
- Keeps Refresh Users and Add User buttons on the right.
- Shortens success/error status messages.
- Keeps Add/Edit User modal error messages inside the modal.
- Normalizes the Add/Edit User modal overlay, spacing, and body scroll behavior.
- Keeps the Users table Full Name based.
- Keeps First Name and Last Name only inside the Add User form.
- Ensures sidebar Font Awesome icons are normalized on the Settings page.

## Not changed

- No Cognito backend route change.
- No IAM policy change.
- No DynamoDB users table.
- No EC2 or deployment change.

## Current known create-user test note

If Create User shows `401 Unauthorized`, log out and log back in before retrying. If the Admin group was added after the current login token was issued, the browser token must be refreshed by logging in again.
