from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import (  # noqa: E402
    get_aws_region,
    get_dynamodb_table,
    get_table_name,
)

CANONICAL_LOGOS_BY_KEY = {
    "tplink": "assets/images/brands/tplink.png",
    "tp-link": "assets/images/brands/tplink.png",
    "d-link": "assets/images/brands/dlink.png",
    "dlink": "assets/images/brands/dlink.png",
    "seagate": "assets/images/brands/seagate.png",
    "western-digital": "assets/images/brands/wd.png",
    "wd": "assets/images/brands/wd.png",
    "hanhwa": "assets/images/brands/hanwha.png",
    "hanwha": "assets/images/brands/hanwha.png",
}


def iter_scan(table):
    kwargs = {}
    while True:
        result = table.scan(**kwargs)
        for item in result.get("Items", []):
            yield item

        last_key = result.get("LastEvaluatedKey")
        if not last_key:
            break

        kwargs["ExclusiveStartKey"] = last_key


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix known static-import brand logo path mismatches in DynamoDB."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply updates. Without this, runs dry-run only.",
    )
    args = parser.parse_args()

    region = get_aws_region()
    table = get_dynamodb_table(get_table_name("brands"), region_name=region)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    candidates = []

    for item in iter_scan(table):
        brand_key = str(item.get("brand_key") or "").strip().lower()
        expected = CANONICAL_LOGOS_BY_KEY.get(brand_key)
        if not expected:
            continue

        current = str(item.get("brand_logo_path") or "")
        if current != expected:
            candidates.append((item, current, expected))

    if not candidates:
        print("[ok] No brand logo path mismatches found.")
        return

    print(f"Found {len(candidates)} brand logo path mismatches:")
    for item, current, expected in candidates:
        print(
            f"- {item.get('brand_id')} {item.get('brand_name')} "
            f"({item.get('brand_key')}): {current!r} -> {expected!r}"
        )

    if not args.execute:
        print("[dry-run] No changes applied. Re-run with --execute to update DynamoDB.")
        return

    for item, _current, expected in candidates:
        table.update_item(
            Key={"brand_id": item["brand_id"]},
            UpdateExpression="SET brand_logo_path = :p, updated_by = :u, updated_at = :t",
            ExpressionAttributeValues={
                ":p": expected,
                ":u": "batch55a-brand-logo-path-fix",
                ":t": now,
            },
        )

    print(f"[done] Updated {len(candidates)} brand logo path(s).")


if __name__ == "__main__":
    main()
