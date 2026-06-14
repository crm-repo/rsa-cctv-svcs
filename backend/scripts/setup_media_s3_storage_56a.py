from __future__ import annotations

import argparse
import json
from botocore.exceptions import ClientError

BATCH_VERSION = "batch56a-s3-media-storage-setup"
DEFAULT_BUCKET = "rsa-cms-media-537765358118-ap-southeast-1"
DEFAULT_REGION = "ap-southeast-1"
POLICY_NAME = "rsa-cms-media-s3-access"


def s3_client(region: str):
    import boto3
    return boto3.client("s3", region_name=region)


def iam_client(region: str):
    import boto3
    return boto3.client("iam", region_name=region)


def bucket_exists(client, bucket_name: str) -> tuple[bool, str]:
    try:
        client.head_bucket(Bucket=bucket_name)
        return True, "exists"
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in {"404", "NoSuchBucket", "NotFound"}:
            return False, "missing"
        if code in {"403", "AccessDenied"}:
            raise SystemExit(
                f"Bucket {bucket_name} exists or is not accessible with the current AWS identity. "
                "Choose a different bucket name or verify ownership/permissions."
            ) from exc
        raise


def create_bucket_if_missing(client, bucket_name: str, region: str, execute: bool) -> None:
    exists, _ = bucket_exists(client, bucket_name)
    if exists:
        print(f"[ok] bucket already exists: {bucket_name}")
        return

    if not execute:
        print(f"[dry-run] would create private S3 bucket: {bucket_name} in {region}")
        return

    print(f"[apply] creating private S3 bucket: {bucket_name} in {region}")
    if region == "us-east-1":
        client.create_bucket(Bucket=bucket_name)
    else:
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
    waiter = client.get_waiter("bucket_exists")
    waiter.wait(Bucket=bucket_name)
    print(f"[ok] bucket created: {bucket_name}")


def put_public_access_block(client, bucket_name: str, execute: bool) -> None:
    config = {
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True,
    }
    if not execute:
        print("[dry-run] would enable S3 Block Public Access on bucket")
        return
    client.put_public_access_block(Bucket=bucket_name, PublicAccessBlockConfiguration=config)
    print("[ok] S3 Block Public Access enabled")


def put_ownership_controls(client, bucket_name: str, execute: bool) -> None:
    controls = {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}
    if not execute:
        print("[dry-run] would set object ownership to BucketOwnerEnforced")
        return
    client.put_bucket_ownership_controls(Bucket=bucket_name, OwnershipControls=controls)
    print("[ok] object ownership set to BucketOwnerEnforced")


def put_encryption(client, bucket_name: str, execute: bool) -> None:
    encryption = {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
                "BucketKeyEnabled": False,
            }
        ]
    }
    if not execute:
        print("[dry-run] would enable default SSE-S3 encryption")
        return
    client.put_bucket_encryption(Bucket=bucket_name, ServerSideEncryptionConfiguration=encryption)
    print("[ok] default SSE-S3 encryption enabled")


def put_versioning_suspended(client, bucket_name: str, execute: bool) -> None:
    if not execute:
        print("[dry-run] would keep bucket versioning suspended/off")
        return
    client.put_bucket_versioning(Bucket=bucket_name, VersioningConfiguration={"Status": "Suspended"})
    print("[ok] bucket versioning suspended/off for Free-Tier-first launch")


def put_tags(client, bucket_name: str, execute: bool) -> None:
    tags = {
        "TagSet": [
            {"Key": "Project", "Value": "rsa-cms"},
            {"Key": "Batch", "Value": "56A"},
            {"Key": "Purpose", "Value": "admin-media-uploads"},
            {"Key": "ManagedBy", "Value": "rsa-cms-script"},
        ]
    }
    if not execute:
        print("[dry-run] would apply project/cost tags to bucket")
        return
    client.put_bucket_tagging(Bucket=bucket_name, Tagging=tags)
    print("[ok] project/cost tags applied")


def build_role_policy(bucket_name: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RsaCmsMediaBucketReadLocation",
                "Effect": "Allow",
                "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{bucket_name}",
            },
            {
                "Sid": "RsaCmsMediaObjectAccess",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }


def attach_role_policy(role_name: str, bucket_name: str, region: str, execute: bool) -> None:
    policy = build_role_policy(bucket_name)
    print("[info] IAM inline policy document:")
    print(json.dumps(policy, indent=2))
    if not role_name:
        print("[skip] no --role-name supplied; IAM role policy was not attached")
        return
    if not execute:
        print(f"[dry-run] would attach inline IAM policy {POLICY_NAME} to role {role_name}")
        return
    client = iam_client(region)
    client.put_role_policy(
        RoleName=role_name,
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy),
    )
    print(f"[ok] attached inline IAM policy {POLICY_NAME} to role {role_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch 56A S3 media bucket and IAM setup")
    parser.add_argument("--bucket-name", default=DEFAULT_BUCKET)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--role-name", default="", help="Optional EC2 instance role name to receive S3 access policy")
    parser.add_argument("--execute", action="store_true", help="Actually create/update AWS resources. Omit for dry-run.")
    parser.add_argument("--attach-role-policy", action="store_true", help="Attach inline IAM policy to --role-name. Requires --execute.")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 56A S3 media storage setup")
    print(f"version: {BATCH_VERSION}")
    print(f"bucket_name: {args.bucket_name}")
    print(f"region: {args.region}")
    print(f"mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print("No AWS access keys or secrets are printed by this script.")

    client = s3_client(args.region)
    create_bucket_if_missing(client, args.bucket_name, args.region, args.execute)
    put_public_access_block(client, args.bucket_name, args.execute)
    put_ownership_controls(client, args.bucket_name, args.execute)
    put_encryption(client, args.bucket_name, args.execute)
    put_versioning_suspended(client, args.bucket_name, args.execute)
    put_tags(client, args.bucket_name, args.execute)

    if args.attach_role_policy:
        if not args.role_name:
            raise SystemExit("--attach-role-policy requires --role-name")
        attach_role_policy(args.role_name, args.bucket_name, args.region, args.execute)
    else:
        attach_role_policy("", args.bucket_name, args.region, False)

    if not args.execute:
        print("[done] dry-run complete. Re-run with --execute to apply bucket settings.")
    else:
        print("[done] batch56a-s3-media-storage-setup applied.")
        print("[done] Private S3 bucket setup complete. No public bucket policy, CloudFront, Route 53, versioning, or paid notification service was added.")


if __name__ == "__main__":
    main()
