# Batch 56A - S3 media storage setup

Apply patch from project root:

```powershell
python backend/scripts/patch_media_s3_storage_setup_56a.py
```

Run dry-run first:

```powershell
python backend/scripts/setup_media_s3_storage_56a.py --bucket-name rsa-cms-media-537765358118-ap-southeast-1 --region ap-southeast-1
```

Apply bucket setup:

```powershell
python backend/scripts/setup_media_s3_storage_56a.py --bucket-name rsa-cms-media-537765358118-ap-southeast-1 --region ap-southeast-1 --execute
```

If you know the EC2 instance role name, attach the S3 policy:

```powershell
python backend/scripts/setup_media_s3_storage_56a.py --bucket-name rsa-cms-media-537765358118-ap-southeast-1 --region ap-southeast-1 --role-name <EC2_ROLE_NAME> --attach-role-policy --execute
```

Check bucket:

```powershell
python backend/scripts/check_media_s3_storage_56a.py --bucket-name rsa-cms-media-537765358118-ap-southeast-1 --region ap-southeast-1 --write-test
```

Configure EC2 runtime env after deploy:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\ec2\configure_media_s3_runtime_env_56a.ps1 -KeyPath "C:\Users\johnb\Downloads\AWS Project\aws\rsa-cms-demo-key.pem" -HostName "<EC2_PUBLIC_IP>"
```
