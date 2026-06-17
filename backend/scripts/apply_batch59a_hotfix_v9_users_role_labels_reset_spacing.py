from __future__ import annotations

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PAYLOAD = SCRIPT_DIR / "batch59a_v9"
ADMIN_USERS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-users-59a.js"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
ADMIN_AUTH_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-auth.js"
HEADER_UTILS_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-header-utilities-55d.js"
LOGIN_HTML = ROOT / "frontend" / "admin" / "login.html"
MARKER = "batch59a-hotfix-v9-users-role-labels-reset-spacing"
LOGIN_MARKER = "data-batch59a-hotfix-v9-login-email-lock"


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


def append_once(path: Path, snippet: str, marker: str, label: str, comment_prefix: str = "//") -> None:
    if not path.exists():
        print(f"[skip] Missing {rel(path)}; {label} not patched.")
        return
    text = read(path)
    if marker in text:
        print(f"[skip] {label} marker already present in {rel(path)}")
        return
    write(path, text.rstrip() + f"\n\n{comment_prefix} {marker}\n" + snippet.strip() + "\n")


def patch_login_html() -> None:
    if not LOGIN_HTML.exists():
        print(f"[skip] Missing {rel(LOGIN_HTML)}; login email lock not patched.")
        return
    text = read(LOGIN_HTML)
    if LOGIN_MARKER in text:
        print(f"[skip] Login email lock already present in {rel(LOGIN_HTML)}")
        return
    snippet = read(PAYLOAD / "login-email-lock-snippet.html").strip()
    if "</body>" not in text:
        raise SystemExit(f"[fail] Could not find </body> in {rel(LOGIN_HTML)}")
    write(LOGIN_HTML, text.replace("</body>", snippet + "\n</body>", 1))


def main() -> None:
    print(f"[start] Applying {MARKER}")
    if not ADMIN_USERS_JS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_USERS_JS)}")
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")

    copy_payload("admin-users-59a.js", ADMIN_USERS_JS)

    css_append = read(PAYLOAD / "admin-v9.css")
    append_once(ADMIN_CSS, css_append, MARKER, "admin CSS", comment_prefix="/*")

    role_sync = read(PAYLOAD / "role-label-sync-snippet.js")
    append_once(ADMIN_AUTH_JS, role_sync, MARKER, "admin auth role label sync")
    append_once(HEADER_UTILS_JS, role_sync, MARKER, "header utility role label sync")
    patch_login_html()

    print(f"[done] {MARKER} applied.")
    print("[done] Role labels now display as System Administrator / Standard User, reset drawer spacing is tightened, and first-login email is locked during password reset.")
    print("[done] No backend/IAM/Cognito/DynamoDB/S3/EC2 change.")


if __name__ == "__main__":
    main()
