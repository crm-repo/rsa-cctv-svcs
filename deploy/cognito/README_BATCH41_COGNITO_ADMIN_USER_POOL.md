# Batch 41 Cognito Admin User Pool

This folder contains local templates for the Cognito admin auth setup.

Use:

- `admin-auth.values.local.template.env` as a local-only value template.
- Do not commit copied files containing real user pool/client IDs if you prefer keeping deployment IDs out of Git.
- Never commit admin passwords or temporary passwords.

The actual public admin exposure is intentionally deferred to a later batch.
