Batch 56B - Admin media upload integration

Apply:
  python backend/scripts/patch_admin_media_upload_integration_56b.py

Verify:
  node --check frontend/admin/assets/js/admin-media.js
  Select-String -Path .\frontend\admin\assets\js\admin-media.js,.\frontend\admin\assets\css\admin-media.css -Pattern "batch56b-admin-media-upload-integration"
  Select-String -Path .\frontend\admin\*.html,.\frontend\admin\assets\js\*.js,.\frontend\admin\assets\css\*.css -Pattern "â|�|admin-icon-consistency-55c|fa-boxes-stackedes-stacked"

Scope:
  Products image_path
  Brands brand_logo_path
  Project Gallery image_path
  Contact Us person_image_path for Contact Person records

No backend route, DynamoDB schema, S3 bucket/IAM, CloudFront, Route 53, email/SMS, or notification change.
