from pathlib import Path

MARKER = "batch60a-precheck-hotfix-v2-admin-role-label-selector-not-body"

files = [
    Path("frontend/admin/assets/js/admin-auth.js"),
    Path("frontend/admin/assets/js/admin-header-utilities-55d.js"),
]

old = "document.querySelectorAll('[data-admin-role], [data-settings-admin-role]')"
new = "document.querySelectorAll('[data-admin-role]:not(body), [data-settings-admin-role]')"

print("[start] Applying admin role-label body overwrite hotfix")

for path in files:
    if not path.exists():
        raise SystemExit(f"[fail] Missing {path}")

    text = path.read_text(encoding="utf-8")

    if MARKER in text:
        print(f"[skip] {path} already patched")
        continue

    count = text.count(old)
    if count == 0:
        raise SystemExit(f"[fail] Expected selector not found in {path}")

    text = text.replace(old, new)
    text += f"\n/* {MARKER}: role label updater no longer targets body[data-admin-role]. */\n"
    path.write_text(text, encoding="utf-8")

    print(f"[ok] Patched {count} selector(s) in {path}")

print("[done] admin role-label body overwrite hotfix applied locally.")
print("[done] Admin role label updates no longer replace the whole admin page body.")
print("[done] No backend/IAM/Cognito/DynamoDB/S3/EC2/Route 53/CloudFront or paid notification change.")
