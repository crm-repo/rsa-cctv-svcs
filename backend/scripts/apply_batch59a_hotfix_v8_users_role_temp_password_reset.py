from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PAYLOAD = SCRIPT_DIR / "batch59a_v8"
ADMIN_USERS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-users-59a.js"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
ADMIN_AUTH_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-auth.js"
HEADER_UTILS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-header-utilities-55d.js"
DOC_SRC = ROOT / "docs" / "phase8_batch59a_hotfix_v8_users_role_temp_password_reset.md"
MARKER = "batch59a-hotfix-v8-users-role-temp-password-reset"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


def copy_payload(filename: str, target: Path) -> None:
    source = PAYLOAD / filename
    if not source.exists():
        raise SystemExit(f"[fail] Missing payload file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"[ok] Copied {filename} -> {rel(target)}")


def append_once(path: Path, snippet: str, label: str) -> None:
    if not path.exists():
        print(f"[skip] Missing {rel(path)}; {label} not patched.")
        return
    text = read(path)
    if MARKER in text:
        print(f"[skip] {label} marker already present in {rel(path)}")
        return
    write(path, text.rstrip() + "\n\n// " + MARKER + "\n" + snippet.strip() + "\n")


def main() -> None:
    print(f"[start] Applying {MARKER}")
    if not ADMIN_USERS_JS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_USERS_JS)}")
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")

    copy_payload("admin-users-59a.js", ADMIN_USERS_JS)

    css = read(ADMIN_CSS)
    css_append = read(PAYLOAD / "admin-v8.css")
    if MARKER not in css:
        write(ADMIN_CSS, css.rstrip() + css_append)
    else:
        print(f"[skip] CSS marker already present in {rel(ADMIN_CSS)}")

    role_sync = read(PAYLOAD / "role-sync-snippet.js")
    append_once(ADMIN_AUTH_JS, role_sync, "admin auth role sync")
    append_once(HEADER_UTILS_JS, role_sync, "header utility role sync")

    print(f"[done] {MARKER} applied.")
    print("[done] Topbar role now comes from Cognito Groups, and reset-password temporary password stays inside a drawer.")
    print("[done] No backend/IAM/Cognito/DynamoDB/S3/EC2 change.")


if __name__ == "__main__":
    main()
