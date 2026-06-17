from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS = [
    ("backend/app/models/admin_user.py", "class AdminUser"),
    ("backend/app/services/admin_user_service.py", "batch59a-cognito-groups-settings-users"),
    ("backend/app/routes/admin_users.py", "APIRouter(prefix=\"/admin/users\")"),
    ("backend/app/auth/admin_auth.py", "def require_admin_group"),
    ("backend/app/main.py", "admin_users"),
    ("frontend/admin/assets/js/admin-role-guard-59a.js", "RSA_BATCH59A_ROLE_GUARD_VERSION"),
    ("frontend/admin/assets/js/admin-users-59a.js", "RSA_BATCH59A_ADMIN_USERS_VERSION"),
    ("frontend/admin/settings.html", "data-settings-users"),
    ("frontend/admin/assets/css/admin.css", "batch59a-cognito-groups-settings-users"),
    ("docs/phase8_batch59a_cognito_groups_settings_users.md", "Batch 59A"),
]


def main() -> None:
    print("[start] verify-batch59a-cognito-groups-settings-users")
    failed = False
    for rel, marker in CHECKS:
        path = ROOT / rel
        if not path.exists():
            print(f"[fail] Missing {rel}")
            failed = True
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if marker not in text:
            print(f"[fail] Marker not found in {rel}: {marker}")
            failed = True
            continue
        print(f"[ok] {rel}")
    if failed:
        raise SystemExit("[fail] Batch 59A local file verification failed.")
    print("[done] Batch 59A local file verification passed.")
    print("[note] Runtime/API verification still requires backend running in Cognito mode and current admin user assigned to the Admin Cognito group.")


if __name__ == "__main__":
    main()
