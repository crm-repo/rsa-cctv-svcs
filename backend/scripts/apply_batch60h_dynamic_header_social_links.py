#!/usr/bin/env python3
# Apply RSA CMS Batch 60H — Dynamic Header Social Links (v2).
#
# Expected script location:
#   backend/scripts/apply_batch60h_dynamic_header_social_links.py
#
# Changes only:
#   frontend/assets/js/main.js
#
# Behavior:
# - Reads visible Contact Us records whose contact_type is Social Media through
#   the existing public Contact API flow.
# - Includes only records containing a web URL.
# - Excludes bare phone numbers and tel/sms/mailto/viber values.
# - Uses each record's icon_code through the existing socialIconClass() helper.
# - Reuses/clones the existing header anchor elements so the current icon
#   formatting, spacing, classes, and responsive layout remain unchanged.
# - Supports new future Social Media URL records without another hardcoded list.
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


BATCH_MARKER = "batch60h-dynamic-header-social-links"


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


def run_command(
    args: list[str],
    *,
    cwd: Path,
    required: bool = True,
) -> str:
    result = subprocess.run(
        args,
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )

    if required and result.returncode != 0:
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
        / "rsa-cms-batch60h-backup"
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
    if BATCH_MARKER in content:
        raise RuntimeError(
            "Batch 60H marker already exists in frontend/assets/js/main.js."
        )

    social_href_block = '''  function socialHref(value) {
    const url = String(value || "").trim();

    if (!url) return "#";
    if (/^https?:\\/\\//i.test(url)) return url;
    if (/^\\/\\//.test(url)) return `https:${url}`;

    return `https://${url.replace(/^\\/+/, "")}`;
  }
'''

    helper_block = social_href_block + r'''
  /* batch60h-dynamic-header-social-links:
     Render only URL-backed Social Media records in the existing header icon
     slots while preserving the current anchor classes and layout. */
  function headerSocialUrl(record) {
    const raw = String(firstNonEmpty(
      record && record.profile_url,
      record && record.phone_number_url,
      record && record.url,
      record && record.contact_value
    ) || "").trim();

    if (!raw) return "";
    if (/^(tel:|sms:|mailto:|viber:)/i.test(raw)) return "";
    if (/^\+?\d[\d\s().-]+$/.test(raw)) return "";

    const hasWebAddress =
      /^https?:\/\//i.test(raw) ||
      /^\/\//.test(raw) ||
      /[a-z0-9-]+\.[a-z]{2,}/i.test(raw);

    if (!hasWebAddress) return "";

    const normalized = socialHref(raw);
    return /^https?:\/\//i.test(normalized) ? normalized : "";
  }

  function renderHeaderSocialGroup(selector, items) {
    const links = Array.from(document.querySelectorAll(selector));
    if (!links.length) return;

    const groups = [];

    links.forEach((link) => {
      const parent = link.parentElement;
      if (!parent) return;

      let group = groups.find((entry) => entry.parent === parent);
      if (!group) {
        group = { parent, links: [] };
        groups.push(group);
      }

      group.links.push(link);
    });

    groups.forEach(({ links: groupLinks }) => {
      const template = groupLinks[0];
      let lastLink = groupLinks[groupLinks.length - 1];

      items.forEach(({ record, url }, index) => {
        let link = groupLinks[index];

        if (!link) {
          link = template.cloneNode(true);
          lastLink.insertAdjacentElement("afterend", link);
          lastLink = link;
        }

        const label = firstNonEmpty(
          record && record.platform_name,
          record && record.platform_key,
          "Social Media"
        );

        link.hidden = false;
        link.href = url;
        link.setAttribute("aria-label", label);
        link.setAttribute("title", label);
        link.innerHTML =
          `<i class="${escapeHtml(socialIconClass(record))}" aria-hidden="true"></i>`;
      });

      groupLinks.slice(items.length).forEach((link) => {
        link.hidden = true;
        link.removeAttribute("href");
        link.removeAttribute("aria-label");
        link.removeAttribute("title");
      });
    });
  }
'''

    content = replace_once(
        content,
        social_href_block,
        helper_block,
        "socialHref helper insertion point",
    )

    old_header_social_block = '''    const socialLinks = Array.from(document.querySelectorAll(".header-social-link, .mobile-social-row a"));
    socialLinks.forEach((link, index) => {
      const record = socials[index];
      if (record && record.profile_url) {
        link.href = socialHref(record.profile_url);
      }
    });
'''

    new_header_social_block = '''    const headerSocials = (Array.isArray(socials) ? socials : [])
      .map((record) => ({
        record,
        url: headerSocialUrl(record)
      }))
      .filter((item) => item.url);

    renderHeaderSocialGroup(".header-social-link", headerSocials);
    renderHeaderSocialGroup(".mobile-social-row a", headerSocials);
'''

    content = replace_once(
        content,
        old_header_social_block,
        new_header_social_block,
        "static header social-link updater",
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
                "Batch 60H must be applied on main. "
                f"Current branch: {branch or '(detached HEAD)'}"
            )

        if not target.exists():
            raise RuntimeError(f"Required file not found: {target}")

        source = read_text_file(target)
        backup_root = create_backup(project_root, target)

        try:
            patched = patch_main_js(source.text)

            required_markers = [
                BATCH_MARKER,
                "function headerSocialUrl(record)",
                "function renderHeaderSocialGroup(selector, items)",
                'renderHeaderSocialGroup(".header-social-link", headerSocials);',
                'renderHeaderSocialGroup(".mobile-social-row a", headerSocials);',
            ]

            missing = [
                marker for marker in required_markers
                if marker not in patched
            ]
            if missing:
                raise RuntimeError(
                    "Verification markers missing: " + ", ".join(missing)
                )

            if "if (record.icon_code) return record.icon_code;" not in patched:
                raise RuntimeError(
                    "Existing socialIconClass() no longer prioritizes icon_code."
                )

            write_text_file(source, patched)

            # Validate only the file changed by Batch 60H. The repository may
            # already contain unrelated documentation or local-proxy changes
            # with different Windows line-ending settings.
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
        print("Batch 60H v2 applied successfully.")
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
        print("Behavior added:")
        print("  - Header icons come from visible Social Media records.")
        print("  - Only web URL records are included.")
        print("  - Bare phone numbers are excluded.")
        print("  - icon_code controls each icon.")
        print("  - Existing header icon classes/layout are preserved.")
        print("  - Future URL-backed Social Media records are added dynamically.")
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
