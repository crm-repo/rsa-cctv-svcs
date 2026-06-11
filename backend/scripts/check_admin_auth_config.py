from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.auth.admin_auth import get_admin_auth_config  # noqa: E402


def main() -> int:
    print("RSA CMS / Mini-CRM Admin Auth Config Check")
    config = get_admin_auth_config()
    print(json.dumps(config, indent=2))

    if config["mode"] == "disabled":
        print("\nSafe default confirmed: admin auth is disabled for local preview.")
    elif config["mode"] == "mock":
        print("\nMock mode enabled: use RSA_ADMIN_MOCK_TOKEN for local auth wiring tests.")
    elif config["mode"] == "cognito":
        print("\nCognito mode selected. Full JWT verification will be completed in a later batch.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
