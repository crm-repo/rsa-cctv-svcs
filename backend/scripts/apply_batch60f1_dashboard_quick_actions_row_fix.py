#!/usr/bin/env python3
'''Apply RSA CMS Batch 60F-1 — Dashboard Quick Actions One-Row Fix.

Expected script location:
    backend/scripts/apply_batch60f1_dashboard_quick_actions_row_fix.py

Changes only:
    frontend/admin/index.html
    frontend/admin/assets/css/admin.css

The script does not commit, push, deploy, or start EC2.
'''

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


HTML_MARKER = "batch60f-dashboard-quick-actions-one-row"
FIX_MARKER = "batch60f1-dashboard-quick-actions-row-fix"


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

    return TextFile(
        path=path,
        text=raw.decode("utf-8"),
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


def create_backup(
    project_root: Path,
    source_paths: list[Path],
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(tempfile.gettempdir())
        / "rsa-cms-batch60f1-backup"
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


def patch_dashboard_html(content: str) -> str:
    if HTML_MARKER not in content:
        raise RuntimeError(
            "Batch 60F HTML marker was not found. "
            "Apply Batch 60F before Batch 60F-1."
        )

    if FIX_MARKER in content:
        raise RuntimeError(
            "Batch 60F-1 HTML marker already exists."
        )

    pattern = re.compile(
        rf"(<!--\s*{re.escape(HTML_MARKER)}\s*-->\s*)"
        r'<div\s+class=["\']quick-actions["\']\s*>',
        re.DOTALL,
    )
    matches = list(pattern.finditer(content))

    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one Batch 60F Quick Actions container, "
            f"but found {len(matches)}."
        )

    replacement = (
        rf"<!-- {HTML_MARKER} -->\n"
        rf"<!-- {FIX_MARKER} -->\n"
        '<div class="quick-actions quick-actions-one-row">'
    )

    return pattern.sub(replacement, content, count=1)


def patch_admin_css(content: str) -> str:
    if FIX_MARKER in content:
        raise RuntimeError(
            "Batch 60F-1 CSS marker already exists."
        )

    css = r'''
/* batch60f1-dashboard-quick-actions-row-fix */
.quick-actions.quick-actions-one-row {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  grid-auto-flow: row !important;
  gap: 14px !important;
  width: 100% !important;
}

.quick-actions.quick-actions-one-row .quick-action-link {
  grid-column: auto !important;
  width: 100% !important;
  min-width: 0 !important;
  min-height: 62px !important;
}

.quick-actions.quick-actions-one-row
.quick-action-link:last-child:nth-child(odd) {
  grid-column: auto !important;
}

@media (max-width: 720px) {
  .quick-actions.quick-actions-one-row {
    grid-template-columns: 1fr !important;
  }
}
'''

    return content.rstrip() + "\n\n" + css.strip() + "\n"


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    dashboard_path = project_root / "frontend" / "admin" / "index.html"
    admin_css_path = (
        project_root
        / "frontend"
        / "admin"
        / "assets"
        / "css"
        / "admin.css"
    )
    targets = [dashboard_path, admin_css_path]
    backup_root: Path | None = None

    try:
        if not (project_root / ".git").exists():
            raise RuntimeError(
                f"Repository root could not be inferred: {project_root}"
            )

        branch = run_git(project_root, "branch", "--show-current")
        if branch != "main":
            raise RuntimeError(
                "Batch 60F-1 must be applied on main. "
                f"Current branch: {branch or '(detached HEAD)'}"
            )

        for path in targets:
            if not path.exists():
                raise RuntimeError(f"Required file not found: {path}")

        dashboard = read_text_file(dashboard_path)
        admin_css = read_text_file(admin_css_path)

        backup_root = create_backup(project_root, targets)

        try:
            patched_dashboard = patch_dashboard_html(dashboard.text)
            patched_css = patch_admin_css(admin_css.text)

            if (
                'class="quick-actions quick-actions-one-row"'
                not in patched_dashboard
            ):
                raise RuntimeError(
                    "Dashboard one-row class was not added."
                )

            if (
                "grid-template-columns: repeat(3, minmax(0, 1fr))"
                not in patched_css
            ):
                raise RuntimeError(
                    "Three-column dashboard CSS was not added."
                )

            write_text_file(dashboard, patched_dashboard)
            write_text_file(admin_css, patched_css)

            run_git(project_root, "diff", "--check")

        except Exception:
            restore_backup(project_root, backup_root, targets)
            raise

        print()
        print("Batch 60F-1 applied successfully.")
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
