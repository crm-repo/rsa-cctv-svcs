# Phase 8 Batch 59A Hotfix v6 — Admin API Auth Header Preservation

This package fixes the Settings > Users create-user `401 Unauthorized` failure caused by the shared admin API client dropping the Authorization header on POST/PUT requests.

## Apply

```powershell
cd "C:\Users\johnb\Downloads\AWS Project\cctv-crm-project"
python .\backend\scripts\apply_batch59a_hotfix_v6_admin_api_auth_header.py
```

Expected markers:

```text
[done] batch59a-hotfix-v6-admin-api-auth-header applied.
[done] POST/PUT admin API requests now preserve Authorization bearer headers.
[done] No Cognito/IAM/backend/DynamoDB/S3/EC2 change.
```

## Browser step

Hard refresh the admin page after apply:

```text
Ctrl + F5
```

Then log in again and retry Add User.
