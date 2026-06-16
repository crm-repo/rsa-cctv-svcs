Batch 56B - Admin media upload integration

Apply:
  python backend/scripts/patch_admin_media_upload_integration_56b.py

Verify:
  node --check frontend/admin/assets/js/admin-media.js
  Select-String -Path .\frontend\admin\assets\js\admin-media.js,.\frontend\admin\assets\css\admin-media.css -Pattern "batch56b-admin-media-upload-integration"
  Select-String -Path .\frontend\admin\*.html,.\frontend\admin\assets\js\*.js,.\frontend\admin\assets\css\*.css -Pattern "â|�|admin-icon-consistency-55c|fa-boxes-stackedes-stacked"

Browser checks:
  Products image upload
  Brand logo upload
  Project Gallery image upload
  Contact Person photo upload
  Failed upload preserves existing path
  Restore Current works
