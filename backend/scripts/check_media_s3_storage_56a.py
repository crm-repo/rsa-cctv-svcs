from __future__ import annotations

import argparse
import json
import secrets
from botocore.exceptions import ClientError

BATCH_VERSION = "batch56a-s3-media-storage-setup"
DEFAULT_BUCKET = "rsa-cms-media-537765358118-ap-southeast-1"
DEFAULT_REGION = "ap-southeast-1"


def s3_client(region: str):
    import boto3
    return boto3.client("s3", region_name=region)


def check_bucket(client, bucket_name: str) -> int:
    issues = 0
    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"bucket_exists: True ({bucket_name})")
    except ClientError as exc:
        print(f"bucket_exists: False ({exc.response.get('Error', {}).get('Code')})")
        return issues + 1

    try:
        public_access = client.get_public_access_block(Bucket=bucket_name)["PublicAccessBlockConfiguration"]
        print("public_access_block:", json.dumps(public_access, sort_keys=True))
        expected = ["BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"]
        if not all(public_access.get(key) is True for key in expected):
            print("FAIL: all S3 Block Public Access settings must be true")
            issues += 1
    except ClientError as exc:
        print(f"FAIL: could not read public access block: {exc.response.get('Error', {}).get('Code')}")
        issues += 1

    try:
        encryption = client.get_bucket_encryption(Bucket=bucket_name)["ServerSideEncryptionConfiguration"]
        print("encryption:", json.dumps(encryption, sort_keys=True))
        rules = encryption.get("Rules", [])
        if not any(rule.get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm") == "AES256" for rule in rules):
            print("FAIL: bucket should use default SSE-S3 AES256 encryption")
            issues += 1
    except ClientError as exc:
        print(f"FAIL: could not read bucket encryption: {exc.response.get('Error', {}).get('Code')}")
        issues += 1

    try:
        ownership = client.get_bucket_ownership_controls(Bucket=bucket_name)["OwnershipControls"]
        print("ownership_controls:", json.dumps(ownership, sort_keys=True))
    except ClientError as exc:
        print(f"WARN: could not read ownership controls: {exc.response.get('Error', {}).get('Code')}")

    try:
        versioning = client.get_bucket_versioning(Bucket=bucket_name)
        print("versioning_status:", versioning.get("Status", "Off/Suspended"))
        if versioning.get("Status") == "Enabled":
            print("WARN: versioning is enabled; Free-Tier-first launch recommended off/suspended")
    except ClientError as exc:
        print(f"WARN: could not read versioning: {exc.response.get('Error', {}).get('Code')}")

    return issues


def write_test(client, bucket_name: str) -> int:
    key = f"_rsa56a-write-test/{secrets.token_hex(8)}.txt"
    body = b"rsa cms batch56a s3 write/read/delete test\n"
    try:
        client.put_object(Bucket=bucket_name, Key=key, Body=body, ContentType="text/plain")
        response = client.get_object(Bucket=bucket_name, Key=key)
        read_back = response["Body"].read()
        client.delete_object(Bucket=bucket_name, Key=key)
        print("write_read_delete_test: PASSED")
        if read_back != body:
            print("FAIL: read content did not match written content")
            return 1
        return 0
    except ClientError as exc:
        print(f"write_read_delete_test: FAILED ({exc.response.get('Error', {}).get('Code')})")
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch 56A S3 media bucket preflight/check")
    parser.add_argument("--bucket-name", default=DEFAULT_BUCKET)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--write-test", action="store_true", help="Put/get/delete a temporary object to verify permissions")
    args = parser.parse_args()

    print("RSA CMS / Mini-CRM Batch 56A S3 media storage check")
    print(f"version: {BATCH_VERSION}")
    print(f"bucket_name: {args.bucket_name}")
    print(f"region: {args.region}")
    print("No AWS access keys or secrets are printed by this script.")

    client = s3_client(args.region)
    issues = check_bucket(client, args.bucket_name)
    if args.write_test:
        issues += write_test(client, args.bucket_name)

    if issues:
        raise SystemExit(f"Batch 56A S3 media storage check FAILED with {issues} issue(s).")
    print("Batch 56A S3 media storage check PASSED.")


if __name__ == "__main__":
    main()
