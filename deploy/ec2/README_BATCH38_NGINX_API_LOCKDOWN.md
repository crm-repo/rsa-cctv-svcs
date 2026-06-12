# Batch 38 EC2 scripts

Copy these scripts to the running EC2 instance:

```powershell
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\configure_rsa_cms_nginx_api_lockdown.sh ubuntu@<PUBLIC_IPV4>:/tmp/configure_rsa_cms_nginx_api_lockdown.sh
scp -i "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" deploy\ec2\check_rsa_cms_nginx_api_lockdown.sh ubuntu@<PUBLIC_IPV4>:/tmp/check_rsa_cms_nginx_api_lockdown.sh
```

Run on EC2:

```bash
chmod +x /tmp/configure_rsa_cms_nginx_api_lockdown.sh /tmp/check_rsa_cms_nginx_api_lockdown.sh
sudo /tmp/configure_rsa_cms_nginx_api_lockdown.sh
/tmp/check_rsa_cms_nginx_api_lockdown.sh
```

The config script backs up the previous Nginx site config before replacing it.
