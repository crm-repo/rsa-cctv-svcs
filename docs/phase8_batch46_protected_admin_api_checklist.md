# Batch 46 Checklist

- [ ] Apply Batch 46 files locally.
- [ ] Deploy latest code to EC2 using `deploy_rsa_cms_release_to_ec2.ps1`.
- [ ] Copy Batch 46 Nginx scripts to EC2.
- [ ] Run `sudo /tmp/configure_rsa_cms_nginx_protected_admin_api_access.sh`.
- [ ] Run `/tmp/check_rsa_cms_nginx_protected_admin_api_access.sh`.
- [ ] Run local read-only smoke check.
- [ ] Optional: run local authenticated smoke check with Cognito password prompt.
- [ ] Confirm direct `:8000` public access remains blocked by the security group.
- [ ] Confirm `/docs`, `/redoc`, and `/openapi.json` remain blocked publicly.
- [ ] Commit and push Batch 46 files.
- [ ] Stop EC2 if pausing after the batch.
