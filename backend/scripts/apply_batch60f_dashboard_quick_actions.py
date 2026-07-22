#!/usr/bin/env python3
'''Apply RSA CMS Batch 60F — Dashboard Quick Actions One-Row Polish.

Expected script location:
    backend/scripts/apply_batch60f_dashboard_quick_actions.py

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


BATCH_MARKER = "batch60f-dashboard-quick-actions-one-row"


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


def replace_exactly_once(
    content: str,
    pattern: str,
    replacement: str,
    description: str,
) -> str:
    compiled = re.compile(pattern, re.DOTALL | re.VERBOSE)
    matches = list(compiled.finditer(content))

    if len(matches) != 1:
        raise RuntimeError(
            f"{description} expected exactly 1 match, "
            f"but found {len(matches)}."
        )

    return compiled.sub(lambda _match: replacement, content, count=1)


def create_backup(
    project_root: Path,
    source_paths: list[Path],
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(tempfile.gettempdir())
        / "rsa-cms-batch60f-backup"
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
    quick_actions_pattern = r'''
<div\s+class=["']quick-actions["']\s*>
\s*
<a\s+class=["']quick-action-link["']\s+
href=["']\./products\.html\?action=create["']\s*>
\s*Add\s+Product\s*
</a>
\s*
<a\s+class=["']quick-action-link["']\s+
href=["']\./categories\.html\?action=create["']\s*>
\s*Add\s+Category\s*
</a>
\s*
<a\s+class=["']quick-action-link["']\s+
href=["']\./brands\.html\?action=create["']\s*>
\s*Add\s+Brand\s*
</a>
\s*
</div>
'''

    quick_actions_replacement = '''<!-- batch60f-dashboard-quick-actions-one-row -->
<div class="quick-actions">
  <a
    class="quick-action-link"
    href="./products.html?action=create"
  >
    <span class="quick-action-add-indicator" aria-hidden="true">+</span>
    <span>Add Product</span>
  </a>

  <a
    class="quick-action-link"
    href="./categories.html?action=create"
  >
    <span class="quick-action-add-indicator" aria-hidden="true">+</span>
    <span>Add Category</span>
  </a>

  <a
    class="quick-action-link"
    href="./brands.html?action=create"
  >
    <span class="quick-action-add-indicator" aria-hidden="true">+</span>
    <span>Add Brand</span>
  </a>
</div>'''

    return replace_exactly_once(
        content,
        quick_actions_pattern,
        quick_actions_replacement,
        "Dashboard Quick Actions block",
    )


def patch_admin_css(content: str) -> str:
    css = r'''
/* batch60f-dashboard-quick-actions-one-row */
.quick-actions-panel .quick-actions {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 14px !important;
}

.quick-actions-panel .quick-action-link {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 11px !important;
  width: 100% !important;
  min-width: 0 !important;
  min-height: 62px !important;
  padding: 12px 18px !important;
  white-space: nowrap;
}

.quick-action-add-indicator {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  border: 2px solid currentColor;
  border-radius: 9px;
  font-size: 1.35rem;
  font-weight: 900;
  line-height: 1;
}

.quick-actions-panel .quick-action-link:hover
.quick-action-add-indicator {
  background: var(--rsa-red, #b91c1c);
  border-color: var(--rsa-red, #b91c1c);
  color: #ffffff;
}

@media (max-width: 760px) {
  .quick-actions-panel .quick-actions {
    grid-template-columns: 1fr !important;
  }

  .quick-actions-panel .quick-action-link {
    white-space: normal;
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
                "Batch 60F must be applied on main. "
                f"Current branch: {branch or '(detached HEAD)'}"
            )

        for path in targets:
            if not path.exists():
                raise RuntimeError(f"Required file not found: {path}")

        dashboard = read_text_file(dashboard_path)
        admin_css = read_text_file(admin_css_path)

        if (
            BATCH_MARKER in dashboard.text
            or BATCH_MARKER in admin_css.text
        ):
            raise RuntimeError(
                "Batch 60F marker already exists. "
                "The batch appears to have been applied."
            )

        backup_root = create_backup(project_root, targets)

        try:
            patched_dashboard = patch_dashboard_html(dashboard.text)
            patched_css = patch_admin_css(admin_css.text)

            if 'grid-template-columns: repeat(3' not in patched_css:
                raise RuntimeError(
                    "Three-column Quick Actions CSS marker is missing."
                )

            if patched_dashboard.count(
                'class="quick-action-add-indicator"'
            ) != 3:
                raise RuntimeError(
                    "Expected exactly three add indicators."
                )

            write_text_file(dashboard, patched_dashboard)
            write_text_file(admin_css, patched_css)

            run_git(project_root, "diff", "--check")

        except Exception:
            restore_backup(project_root, backup_root, targets)
            raise

        print()
        print("Batch 60F applied successfully.")
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
