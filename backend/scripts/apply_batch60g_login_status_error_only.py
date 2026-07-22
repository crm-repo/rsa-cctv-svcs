#!/usr/bin/env python3
# Apply RSA CMS Batch 60G v3 — Login Status Error-Only Polish.
#
# Expected location:
#   backend/scripts/apply_batch60g_login_status_error_only.py
#
# Changes only:
#   frontend/admin/login.html
#   frontend/admin/assets/css/admin-auth.css
#
# The script does not commit, push, deploy, or start EC2.

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


BATCH_MARKER = "batch60g-login-status-error-only-v3"


@dataclass(frozen=True)
class TextFile:
    path: Path
    text: str
    newline: str
    had_bom: bool


def read_text_file(path: Path) -> TextFile:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    if had_bom:
        raw = raw[3:]

    decoded = raw.decode("utf-8")
    normalized = (
        decoded
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    return TextFile(
        path=path,
        text=normalized,
        newline="\r\n" if b"\r\n" in raw else "\n",
        had_bom=had_bom,
    )


def write_text_file(source: TextFile, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if source.newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")

    raw = normalized.encode("utf-8")
    if source.had_bom:
        raw = b"\xef\xbb\xbf" + raw

    source.path.write_bytes(raw)


def run_git(project_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\n{message}"
        )
    return result.stdout.strip()


def replace_once(
    content: str,
    old: str,
    new: str,
    description: str,
    *,
    allow_already_done: bool = False,
) -> str:
    count = content.count(old)

    if count == 1:
        return content.replace(old, new, 1)

    if allow_already_done and new in content:
        return content

    raise RuntimeError(
        f"{description} expected exactly 1 match, but found {count}."
    )


def remove_once(
    content: str,
    old: str,
    description: str,
) -> str:
    count = content.count(old)

    if count == 1:
        return content.replace(old, "", 1)

    if count == 0:
        return content

    raise RuntimeError(
        f"{description} expected at most 1 match, but found {count}."
    )


def create_backup(
    project_root: Path,
    source_paths: list[Path],
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(tempfile.gettempdir())
        / "rsa-cms-batch60g-v3-backup"
        / timestamp
    )

    for source in source_paths:
        relative = source.relative_to(project_root)
        destination = backup_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    return backup_root


def restore_backup(
    project_root: Path,
    backup_root: Path,
    target_paths: list[Path],
) -> None:
    for target in target_paths:
        relative = target.relative_to(project_root)
        source = backup_root / relative
        if source.exists():
            shutil.copy2(source, target)


def patch_login_html(content: str) -> str:
    if BATCH_MARKER in content:
        raise RuntimeError(
            "Batch 60G v3 marker already exists in login.html."
        )

    status_old = (
        '    <p class="admin-login-status" '
        'data-admin-login-status></p>'
    )
    status_new = "\n".join([
        f"    <!-- {BATCH_MARKER} -->",
        "    <p",
        '      class="admin-login-status"',
        "      data-admin-login-status",
        '      role="alert"',
        '      aria-live="polite"',
        "    ></p>",
    ])
    content = replace_once(
        content,
        status_old,
        status_new,
        "Login status element",
    )

    challenge_old = "\n".join([
        "        submitButton.textContent = "
        "'Set new password and continue';",
        "        status.textContent = "
        "'First login requires a new permanent password.';",
    ])
    challenge_new = "\n".join([
        "        submitButton.textContent = "
        "'Set new password and continue';",
        "        note.textContent = "
        "'First login requires a new permanent password.';",
        "        status.textContent = '';",
    ])
    content = replace_once(
        content,
        challenge_old,
        challenge_new,
        "New-password challenge message",
    )

    cognito_old = "\n".join([
        "          status.textContent = "
        "authConfig.is_cognito_configured",
        "            ? 'Enter your Cognito admin credentials.'",
        "            : 'Admin authentication is not ready. "
        "Please check the configuration.';",
    ])
    cognito_new = "\n".join([
        "          status.textContent = "
        "authConfig.is_cognito_configured",
        "            ? ''",
        "            : 'Admin authentication is not ready. "
        "Please contact the system administrator.';",
    ])
    content = replace_once(
        content,
        cognito_old,
        cognito_new,
        "Cognito initial status",
    )

    access_token_old = (
        "        status.textContent = "
        "'Enter your admin access token to continue.';"
    )
    access_token_new = "        status.textContent = '';"
    content = replace_once(
        content,
        access_token_old,
        access_token_new,
        "Access-token initial status",
    )

    submit_old = "\n".join([
        "        try {",
        "          submitButton.disabled = true;",
    ])
    submit_new = "\n".join([
        "        try {",
        "          submitButton.disabled = true;",
        "          status.textContent = '';",
    ])
    content = replace_once(
        content,
        submit_old,
        submit_new,
        "Submit-time error clearing",
    )

    for old, description in [
        (
            "            status.textContent = "
            "'Opening dashboard…';\n",
            "Opening-dashboard status",
        ),
        (
            "          status.textContent = 'Signing in…';\n",
            "Signing-in status",
        ),
        (
            "              status.textContent = "
            "'New password set. Redirecting…';\n",
            "New-password success status",
        ),
        (
            "            status.textContent = "
            "'Cognito login successful. Redirecting…';\n",
            "Cognito success status",
        ),
        (
            "          status.textContent = "
            "'Mock login saved. Redirecting…';\n",
            "Mock-login success status",
        ),
    ]:
        content = remove_once(content, old, description)

    # Keep the existing friendly login-error catch block unchanged.
    friendly_error_marker = (
        "Login failed. Please check your email and password"
    )
    legacy_error = (
        "          status.textContent = "
        "`Login failed: ${error.message}`;"
    )
    if friendly_error_marker not in content:
        content = replace_once(
            content,
            legacy_error,
            "\n".join([
                "          console.error("
                "'Admin login failed.', error);",
                "          status.textContent =",
                "            'Login failed. Please check your email "
                "and password '",
                "            + 'and try again.';",
            ]),
            "Friendly login error",
        )

    legacy_init_error = (
        "        status.textContent = "
        "`Unable to load auth config: ${error.message}`;"
    )
    friendly_init_error = "\n".join([
        "        console.error("
        "'Unable to load admin auth config.', error);",
        "        status.textContent =",
        "          'Admin sign-in is temporarily unavailable. '",
        "          + 'Please try again later.';",
    ])
    content = replace_once(
        content,
        legacy_init_error,
        friendly_init_error,
        "Auth-configuration error",
        allow_already_done=True,
    )

    return content


def patch_admin_auth_css(content: str) -> str:
    if BATCH_MARKER in content:
        raise RuntimeError(
            "Batch 60G v3 marker already exists in admin-auth.css."
        )

    css = "\n".join([
        f"/* {BATCH_MARKER} */",
        ".admin-login-note {",
        "  font-size: 16px !important;",
        "  line-height: 1.5 !important;",
        "}",
        "",
        ".admin-login-status:empty {",
        "  display: none !important;",
        "}",
        "",
    ])

    return content.rstrip() + "\n\n" + css


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    login_path = project_root / "frontend" / "admin" / "login.html"
    auth_css_path = (
        project_root
        / "frontend"
        / "admin"
        / "assets"
        / "css"
        / "admin-auth.css"
    )
    targets = [login_path, auth_css_path]
    backup_root: Path | None = None

    try:
        if not (project_root / ".git").exists():
            raise RuntimeError(
                f"Repository root could not be inferred: {project_root}"
            )

        branch = run_git(project_root, "branch", "--show-current")
        if branch != "main":
            raise RuntimeError(
                "Batch 60G v3 must be applied on main. "
                f"Current branch: {branch or '(detached HEAD)'}"
            )

        for path in targets:
            if not path.exists():
                raise RuntimeError(f"Required file not found: {path}")

        login_file = read_text_file(login_path)
        auth_css_file = read_text_file(auth_css_path)

        backup_root = create_backup(project_root, targets)

        try:
            patched_login = patch_login_html(login_file.text)
            patched_css = patch_admin_auth_css(auth_css_file.text)

            required = [
                BATCH_MARKER,
                "status.textContent = authConfig.is_cognito_configured",
                "            ? ''",
                "Login failed. Please check your email and password",
                'role="alert"',
                "font-size: 16px !important",
            ]
            combined = patched_login + "\n" + patched_css
            missing = [item for item in required if item not in combined]
            if missing:
                raise RuntimeError(
                    "Verification markers missing: "
                    + ", ".join(missing)
                )

            write_text_file(login_file, patched_login)
            write_text_file(auth_css_file, patched_css)

            run_git(
                project_root,
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--check",
            )

        except Exception:
            restore_backup(project_root, backup_root, targets)
            raise

        print()
        print("Batch 60G v3 applied successfully.")
        print(f"Backup: {backup_root}")
        print()
        print("Changed files:")
        print(run_git(project_root, "status", "--short") or "(none)")
        print()
        print("Diff summary:")
        print(run_git(project_root, "diff", "--stat") or "(none)")
        print()
        print(
            "The script did not commit, push, deploy, or start EC2."
        )
        return 0

    except Exception as error:
        if backup_root is not None:
            print(f"Backup retained at: {backup_root}", file=sys.stderr)
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
