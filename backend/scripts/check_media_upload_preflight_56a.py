from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.media_service import get_media_storage_config, get_local_media_root  # noqa: E402


def mask(value: str) -> str:
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def main() -> None:
    print("RSA CMS / Mini-CRM Batch 56A Media Upload Preflight")
    print("Mode: read-only configuration check")

    config = get_media_storage_config()
    for key in [
        "version",
        "storage_mode",
        "upload_binary_enabled",
        "s3_bucket_configured",
        "s3_bucket_name",
        "aws_region",
        "local_media_root",
        "max_upload_mb",
        "allowed_upload_media_types",
        "allowed_extensions",
        "media_url_format",
        "filename_rule",
    ]:
        print(f"{key}: {config.get(key)}")

    issues = 0

    multipart_available = importlib.util.find_spec("multipart") is not None
    print(f"python_multipart_available: {multipart_available}")
    if not multipart_available:
        print("FAIL: python-multipart is required by FastAPI UploadFile/Form routes.")
        print("Install locally with: pip install python-multipart")
        issues += 1

    storage_mode = str(config.get("storage_mode") or "local")
    if storage_mode == "s3":
        boto3_available = importlib.util.find_spec("boto3") is not None
        print(f"boto3_available: {boto3_available}")
        if not boto3_available:
            print("FAIL: boto3 is required when RSA_MEDIA_STORAGE_MODE=s3.")
            issues += 1
        if not config.get("s3_bucket_configured"):
            print("FAIL: RSA_MEDIA_S3_BUCKET is required when RSA_MEDIA_STORAGE_MODE=s3.")
            issues += 1
    else:
        local_root = get_local_media_root()
        try:
            local_root.mkdir(parents=True, exist_ok=True)
            print(f"local_media_root_writable: {os.access(local_root, os.W_OK)}")
            if not os.access(local_root, os.W_OK):
                issues += 1
        except Exception as exc:
            print(f"FAIL: could not prepare local media root: {exc}")
            issues += 1

    print(f"aws_access_key_id: {mask(os.getenv('AWS_ACCESS_KEY_ID', ''))}")
    print("No secrets are printed by this preflight.")

    if issues:
        raise SystemExit(f"Batch 56A media upload preflight FAILED with {issues} issue(s).")

    print("Batch 56A media upload preflight PASSED.")


if __name__ == "__main__":
    main()
