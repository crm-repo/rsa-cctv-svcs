# Batch 56A - S3 media storage setup/preflight

This package completes the storage-infrastructure side of Batch 56A after the local upload endpoint has already passed.

Scope:

- Create or verify one private S3 bucket for RSA CMS admin media uploads.
- Enable S3 Block Public Access.
- Enable default SSE-S3 encryption.
- Keep bucket versioning off/suspended for Free-Tier-first launch.
- Optionally attach a narrow inline IAM policy to the EC2 instance role.
- Configure EC2 runtime environment to use S3 mode.
- Run an S3 write/read/delete smoke test.

Out of scope:

- No admin form integration. That is Batch 56B.
- No CloudFront.
- No Route 53/domain dependency.
- No public-read bucket policy.
- No S3 versioning, replication, advanced Storage Lens, lifecycle, or paid notification services.
- No DynamoDB schema changes.

Recommended bucket:

```text
rsa-cms-media-537765358118-ap-southeast-1
```

Recommended runtime env on EC2:

```text
RSA_MEDIA_STORAGE_MODE=s3
RSA_MEDIA_S3_BUCKET=rsa-cms-media-537765358118-ap-southeast-1
RSA_MEDIA_MAX_UPLOAD_MB=5
AWS_DEFAULT_REGION=ap-southeast-1
AWS_REGION=ap-southeast-1
```

IAM policy attached to the EC2 role is intentionally narrow:

- `s3:GetBucketLocation`
- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject`

Only on the approved bucket and its objects.
