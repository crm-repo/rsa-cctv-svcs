#!/usr/bin/env python3
# Apply RSA CMS Batch 60H-1 — Header Social Icon Size + New Tab Hotfix.
#
# Expected script location:
#   backend/scripts/apply_batch60h1_header_social_icon_size_new_tab.py
#
# Changes only:
#   frontend/assets/js/main.js
#
# Behavior:
# - Restores the existing header-social-icon CSS class on dynamically rendered
#   header/mobile social icons so their original size/formatting is preserved.
# - Opens header/mobile social URLs in a new tab.
# - Opens Contact Us social-media cards in a new tab.
# - Adds rel="noopener noreferrer" for external-link safety.
#
# The script does not commit, push, deploy, or start EC2.

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


BATCH60H_MARKER = "batch60h-dynamic-header-social-links"
BATCH60H1_MARKER = "batch60h1-header-social-icon-size-new-tab"


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
    normalized = decoded.replace("\r\n", "\n").replace("\r", "\n")

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


def run_command(args: list[str], *, cwd: Path) -> str:
    result = subprocess.run(
        args,
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        details = "\n".join(part for part in [stdout, stderr] if part)
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\n{details}"
        )

    return (result.stdout or result.stderr or "").strip()


def run_git(project_root: Path, *args: str) -> str:
    return run_command(
        ["git", "-C", str(project_root), *args],
        cwd=project_root,
    )


def create_backup(project_root: Path, target: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(tempfile.gettempdir())
        / "rsa-cms-batch60h1-backup"
        / timestamp
    )

    destination = backup_root / target.relative_to(project_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, destination)

    return backup_root


def restore_backup(
    project_root: Path,
    backup_root: Path,
    target: Path,
) -> None:
    source = backup_root / target.relative_to(project_root)
    if source.exists():
        shutil.copy2(source, target)


def replace_once(
    content: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"{description} expected exactly 1 match, but found {count}."
        )
    return content.replace(old, new, 1)


def patch_main_js(content: str) -> str:
    if BATCH60H_MARKER not in content:
        raise RuntimeError(
            "Batch 60H marker was not found. Apply Batch 60H v2 first."
        )

    if BATCH60H1_MARKER in content:
        raise RuntimeError(
            "Batch 60H-1 marker already exists in frontend/assets/js/main.js."
        )

    old_header_block = '''        link.hidden = false;
        link.href = url;
        link.setAttribute("aria-label", label);
        link.setAttribute("title", label);
        link.innerHTML =
          `<i class="${escapeHtml(socialIconClass(record))}" aria-hidden="true"></i>`;
'''

    new_header_block = f'''        /* {BATCH60H1_MARKER} */
        link.hidden = false;
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.setAttribute("aria-label", label);
        link.setAttribute("title", label);
        link.innerHTML =
          `<i class="${{escapeHtml(socialIconClass(record))}} header-social-icon" aria-hidden="true"></i>`;
'''

    content = replace_once(
        content,
        old_header_block,
        new_header_block,
        "Batch 60H dynamic header icon renderer",
    )

    old_hidden_block = '''      groupLinks.slice(items.length).forEach((link) => {
        link.hidden = true;
        link.removeAttribute("href");
        link.removeAttribute("aria-label");
        link.removeAttribute("title");
      });
'''

    new_hidden_block = '''      groupLinks.slice(items.length).forEach((link) => {
        link.hidden = true;
        link.removeAttribute("href");
        link.removeAttribute("target");
        link.removeAttribute("rel");
        link.removeAttribute("aria-label");
        link.removeAttribute("title");
      });
'''

    content = replace_once(
        content,
        old_hidden_block,
        new_hidden_block,
        "unused header social-link cleanup",
    )

    old_contact_card = '''      channelGrid.innerHTML = channels.map((channel) => `
        <a href="${escapeHtml(channel.url)}" class="home-soft-card contact-channel-card">
          <i class="${escapeHtml(channel.icon)}"></i><h3>${escapeHtml(channel.title)}</h3><p>${escapeHtml(channel.detail)}</p>
        </a>`).join("") || `<div class="rsa-cms-loading-state">No social media contacts available.</div>`;
'''

    new_contact_card = '''      channelGrid.innerHTML = channels.map((channel) => `
        <a href="${escapeHtml(channel.url)}" target="_blank" rel="noopener noreferrer" class="home-soft-card contact-channel-card">
          <i class="${escapeHtml(channel.icon)}"></i><h3>${escapeHtml(channel.title)}</h3><p>${escapeHtml(channel.detail)}</p>
        </a>`).join("") || `<div class="rsa-cms-loading-state">No social media contacts available.</div>`;
'''

    content = replace_once(
        content,
        old_contact_card,
        new_contact_card,
        "Contact Us social card anchor",
    )

    return content


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    target = project_root / "frontend" / "assets" / "js" / "main.js"
    backup_root: Path | None = None

    try:
        if not (project_root / ".git").exists():
            raise RuntimeError(
                f"Repository root could not be inferred: {project_root}"
            )

        branch = run_git(project_root, "branch", "--show-current")
        if branch != "main":
            raise RuntimeError(
                "Batch 60H-1 must be applied on main. "
                f"Current branch: {branch or '(detached HEAD)'}"
            )

        if not target.exists():
            raise RuntimeError(f"Required file not found: {target}")

        source = read_text_file(target)
        backup_root = create_backup(project_root, target)

        try:
            patched = patch_main_js(source.text)

            required_markers = [
                BATCH60H1_MARKER,
                'header-social-icon" aria-hidden="true"',
                'link.target = "_blank";',
                'link.rel = "noopener noreferrer";',
                'target="_blank" rel="noopener noreferrer" class="home-soft-card contact-channel-card"',
            ]

            missing = [
                marker for marker in required_markers
                if marker not in patched
            ]
            if missing:
                raise RuntimeError(
                    "Verification markers missing: " + ", ".join(missing)
                )

            write_text_file(source, patched)

            run_git(
                project_root,
                "-c",
                "core.whitespace=cr-at-eol",
                "diff",
                "--check",
                "--",
                "frontend/assets/js/main.js",
            )

            node = shutil.which("node")
            if node:
                run_command(
                    [node, "--check", str(target)],
                    cwd=project_root,
                )
            else:
                print(
                    "WARNING: Node.js was not found; JavaScript syntax check "
                    "was skipped.",
                    file=sys.stderr,
                )

        except Exception:
            restore_backup(project_root, backup_root, target)
            raise

        print()
        print("Batch 60H-1 applied successfully.")
        print(f"Backup: {backup_root}")
        print()
        print("Changed file:")
        print("  frontend/assets/js/main.js")
        print()
        print("Git status:")
        print(run_git(project_root, "status", "--short") or "(none)")
        print()
        print("Diff summary:")
        print(run_git(project_root, "diff", "--stat") or "(none)")
        print()
        print("Behavior fixed:")
        print("  - Dynamic header/mobile icons retain header-social-icon sizing.")
        print("  - Header/mobile social links open in a new tab.")
        print("  - Contact Us social cards open in a new tab.")
        print("  - External links use rel=noopener noreferrer.")
        print()
        print("The script did not commit, push, deploy, or start EC2.")
        return 0

    except Exception as error:
        if backup_root is not None:
            print(f"Backup retained at: {backup_root}", file=sys.stderr)
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
