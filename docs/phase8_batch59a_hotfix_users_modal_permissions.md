# Phase 8 Batch 59A Hotfix — Users Modal and Cognito Permissions

Status: hotfix for Batch 59A local testing

## Purpose

Corrects two Batch 59A issues found during local browser testing:

1. The Settings > Users add form was incorrectly displayed inline. It is now opened through an Add User modal.
2. The Users table remains a Full Name table. First Name and Last Name are only used by the Add User modal to populate Cognito `given_name`, `family_name`, and `name` attributes.

The backend error shown in the browser is not a UI bug. It means the AWS identity used by local backend credentials is missing Cognito IDP permissions, especially `cognito-idp:ListGroups`. The IAM policy must be updated outside this script.

## Files affected

- `frontend/admin/settings.html`
- `frontend/admin/assets/js/admin-users-59a.js`
- `frontend/admin/assets/css/admin.css`

## Not changed

- No DynamoDB users table.
- No SMS/MFA.
- No email invitation workflow.
- No EC2, Route 53, CloudFront, or paid notification change.
