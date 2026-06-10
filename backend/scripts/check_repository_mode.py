"""Check the RSA CMS repository mode safely.

Safe by default:
- Running this script never creates AWS resources.
- Running this script never reads/writes DynamoDB records.
- It only shows which repository classes would be selected by the current env.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:  # Optional local .env support.
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

from app.database import get_repository_mode, get_repository_mode_summary  # noqa: E402
from app.repositories.id_counter_repository import id_counter_repository  # noqa: E402
from app.repositories.repository_factory import get_crm_repository_summary  # noqa: E402


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(inner_value) for key, inner_value in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def main() -> int:
    crm_summary = get_crm_repository_summary()

    print("RSA CMS / Mini-CRM Repository Mode Check")
    print(f"Repository mode: {get_repository_mode()}")
    print("AWS calls made: False")
    print("")

    print(json.dumps(_json_safe(get_repository_mode_summary()), indent=2))
    print("")

    print("Selected CRM repositories:")
    for logical_name, summary in crm_summary["repositories"].items():
        print(
            f"- {logical_name}: {summary['class_name']} "
            f"mode={summary['repository_mode']} table={summary['table_name']}"
        )

    print(
        "- id_counters: "
        f"{id_counter_repository.__class__.__name__} "
        f"mode={getattr(id_counter_repository, 'repository_mode', '')} "
        f"table={getattr(id_counter_repository, 'table_name', '')}"
    )
    print("")

    if get_repository_mode() == "dynamodb":
        print("DynamoDB mode selected. Make sure tables exist and seed data is loaded before starting public API testing.")
    else:
        print("Mock mode selected. This is the safe default for local development/testing.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
