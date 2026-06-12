# Batch 46 EC2 Scripts

Copy to EC2:

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\configure_rsa_cms_nginx_protected_admin_api_access.sh ubuntu@<PUBLIC_IPV4>:/tmp/configure_rsa_cms_nginx_protected_admin_api_access.sh
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_nginx_protected_admin_api_access.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_nginx_protected_admin_api_access.sh
```

Run on EC2:

```bash
chmod +x /tmp/configure_rsa_cms_nginx_protected_admin_api_access.sh /tmp/check_rsa_cms_nginx_protected_admin_api_access.sh
sudo /tmp/configure_rsa_cms_nginx_protected_admin_api_access.sh
/tmp/check_rsa_cms_nginx_protected_admin_api_access.sh
```
