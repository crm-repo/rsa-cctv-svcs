#!/usr/bin/env python3
'''Apply RSA CMS Batch 60E — Admin Contact Split Tables.

This script is intended to live in:
    backend/scripts/apply_batch60e_contact_split_tables.py

It updates only:
    frontend/admin/contact-us.html
    frontend/admin/assets/js/admin-cms.js
    frontend/admin/assets/css/admin.css

It does not commit, push, deploy, or start EC2.
'''

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


BATCH_MARKER = "batch60e-contact-split-tables"


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

    text = raw.decode("utf-8")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    return TextFile(path=path, text=text, newline=newline, had_bom=had_bom)


def write_text_file(source: TextFile, text: str) -> None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if source.newline == "\r\n":
        normalized = normalized.replace("\n", "\r\n")

    encoded = normalized.encode("utf-8")
    if source.had_bom:
        encoded = b"\xef\xbb\xbf" + encoded

    source.path.write_bytes(encoded)


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
            f"{description} expected exactly 1 match, but found "
            f"{len(matches)}. No Git commit or push was performed."
        )

    return compiled.sub(lambda _match: replacement, content, count=1)


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


def verify_clean_main(project_root: Path) -> None:
    if not (project_root / ".git").exists():
        raise RuntimeError(
            f"Project root is not a Git working tree: {project_root}"
        )

    current_branch = run_git(project_root, "branch", "--show-current")
    if current_branch != "main":
        raise RuntimeError(
            "Batch 60E must be applied from the clean main branch. "
            f"Current branch: {current_branch or '(detached HEAD)'}"
        )

    status = run_git(project_root, "status", "--porcelain")
    allowed_batch_files = {
        "backend/scripts/apply_batch60e_contact_split_tables.py",
        "backend/scripts/README_BATCH60E.md",
    }

    unexpected_changes = []
    for line in status.splitlines():
        if not line.strip():
            continue

        path_text = line[3:].strip()
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1].strip()

        normalized_path = path_text.replace("\\", "/").strip('"')
        if normalized_path not in allowed_batch_files:
            unexpected_changes.append(line)

    if unexpected_changes:
        details = "\n".join(unexpected_changes)
        raise RuntimeError(
            "Batch 60E found existing working-tree changes outside the "
            "two extracted batch files. Commit, stash, or discard these "
            f"changes before running the batch:\n{details}"
        )


def create_backup(
    project_root: Path,
    source_paths: list[Path],
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_root = (
        Path(tempfile.gettempdir())
        / "rsa-cms-batch60e-backup"
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


def patch_contact_html(content: str) -> str:
    contact_type_filter_pattern = r'''
        <label>\s*
          <span>\s*Contact\s+Type\s*</span>\s*
          <select\b[^>]*\bdata-contact-type-filter\b[^>]*>
            .*?
          </select>\s*
        </label>
    '''

    content = replace_exactly_once(
        content,
        contact_type_filter_pattern,
        "",
        "Contact Type filter removal",
    )

    single_table_pattern = r'''
        <section\b
          (?=[^>]*\bclass=["'][^"']*
            \bpanel\b[^"']*
            \blead-table-panel\b[^"']*
            \bcatalog-table-panel\b[^"']*
          ["'])
          [^>]*>
          .*?
          <thead\b[^>]*\bdata-table-head\b[^>]*>.*?</thead>
          .*?
          <tbody\b[^>]*\bdata-table-body\b[^>]*>.*?</tbody>
          .*?
        </section>
    '''

    split_tables_html = r'''<!-- batch60e-contact-split-tables -->
<div class="contact-table-stack" data-contact-table-stack>
  <section
    class="panel lead-table-panel catalog-table-panel contact-type-table"
    data-contact-table="company"
  >
    <div class="panel-header">
      <div>
        <p class="eyebrow">Company Details</p>
        <h2>Company Contact</h2>
      </div>
      <span
        class="panel-tag"
        data-contact-table-count="company"
      >Loading…</span>
    </div>

    <div class="table-wrap lead-table-wrap">
      <table class="admin-data-table">
        <thead data-contact-table-head="company"></thead>
        <tbody data-contact-table-body="company">
          <tr>
            <td class="empty-cell">Loading company contact…</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section
    class="panel lead-table-panel catalog-table-panel contact-type-table"
    data-contact-table="person"
  >
    <div class="panel-header">
      <div>
        <p class="eyebrow">Team Directory</p>
        <h2>Contact Persons</h2>
      </div>
      <span
        class="panel-tag"
        data-contact-table-count="person"
      >Loading…</span>
    </div>

    <div class="table-wrap lead-table-wrap">
      <table class="admin-data-table">
        <thead data-contact-table-head="person"></thead>
        <tbody data-contact-table-body="person">
          <tr>
            <td class="empty-cell">Loading contact persons…</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section
    class="panel lead-table-panel catalog-table-panel contact-type-table"
    data-contact-table="social"
  >
    <div class="panel-header">
      <div>
        <p class="eyebrow">Public Channels</p>
        <h2>Social Media</h2>
      </div>
      <span
        class="panel-tag"
        data-contact-table-count="social"
      >Loading…</span>
    </div>

    <div class="table-wrap lead-table-wrap">
      <table class="admin-data-table">
        <thead data-contact-table-head="social"></thead>
        <tbody data-contact-table-body="social">
          <tr>
            <td class="empty-cell">Loading social media records…</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</div>'''

    return replace_exactly_once(
        content,
        single_table_pattern,
        split_tables_html,
        "Single Contact Us table replacement",
    )


def patch_admin_cms(content: str) -> str:
    render_block_pattern = (
        r"function\s+applyFilters\(\)\s*\{"
        r".*?"
        r"function\s+detailRows\(record\)\s*\{"
    )

    render_block_replacement = r'''/* batch60e-contact-split-tables */
function applyFilters() {
  const query = searchValue();

  state.filtered = sortRecords(
    state.records.filter(
      record => !query || text(record).includes(query)
    )
  );

  renderTable();
}

function setCount(message) {
  const element = document.querySelector('[data-record-count]');
  if (element) element.textContent = message;
}

const contactTableConfigs = [
  {
    key: 'company',
    type: 'Company Contact',
    title: 'Company Contact',
    columns: [
      ['contact_us_id', 'ID'],
      ['display_seq', 'Display Seq'],
      ['show_flag', 'Visible'],
      ['primary_contact_number', 'Primary Contact'],
      ['company_email', 'Company Email'],
      ['business_hours', 'Business Hours']
    ]
  },
  {
    key: 'person',
    type: 'Contact Person',
    title: 'Contact Person',
    columns: [
      ['contact_us_id', 'ID'],
      ['display_seq', 'Display Seq'],
      ['show_flag', 'Visible'],
      ['person_name', 'Person'],
      ['position_title', 'Position'],
      ['department', 'Department'],
      ['phone_number', 'Phone Number'],
      ['email_address', 'Email']
    ]
  },
  {
    key: 'social',
    type: 'Social Media',
    title: 'Social Media',
    columns: [
      ['contact_us_id', 'ID'],
      ['display_seq', 'Display Seq'],
      ['show_flag', 'Visible'],
      ['platform_name', 'Platform'],
      ['profile_url', 'Phone Number/URL'],
      ['icon_code', 'Icon Code']
    ]
  }
];

function renderTableHead(head, columns) {
  if (!head) return;

  head.innerHTML = `
    <tr>
      ${columns
        .map(([, labelText]) => `<th>${esc(labelText)}</th>`)
        .join('')}
      <th>Action</th>
    </tr>
  `;
}

function renderTableCell(field, record) {
  if (field === 'show_flag') {
    return `<td>${flag(record[field])}</td>`;
  }

  const value = fmt(field, record[field]);

  if (field.endsWith('_id')) {
    return `<td><strong>${esc(value)}</strong></td>`;
  }

  return `<td>${esc(value)}</td>`;
}

function renderContactTables() {
  contactTableConfigs.forEach(section => {
    const head = document.querySelector(
      `[data-contact-table-head="${section.key}"]`
    );
    const body = document.querySelector(
      `[data-contact-table-body="${section.key}"]`
    );
    const count = document.querySelector(
      `[data-contact-table-count="${section.key}"]`
    );

    renderTableHead(head, section.columns);

    const records = state.filtered
      .map((record, index) => ({ record, index }))
      .filter(item => item.record.contact_type === section.type);

    if (count) {
      const noun = records.length === 1 ? 'record' : 'records';
      count.textContent = `${records.length} ${noun} found`;
    }

    if (!body) return;

    if (!records.length) {
      body.innerHTML = `
        <tr>
          <td
            colspan="${section.columns.length + 1}"
            class="empty-cell"
          >
            No matching ${esc(section.title)} records found.
          </td>
        </tr>
      `;
      return;
    }

    body.innerHTML = records
      .map(({ record, index }) => {
        const cells = section.columns
          .map(([field]) => renderTableCell(field, record))
          .join('');

        return `
          <tr data-row-index="${index}">
            ${cells}
            <td>
              <button
                class="table-action-link"
                type="button"
                data-view-index="${index}"
              >
                View / Edit
              </button>
            </td>
          </tr>
        `;
      })
      .join('');
  });
}

function renderHead() {
  if (!config) return;

  if (page === 'contact-us') {
    contactTableConfigs.forEach(section => {
      renderTableHead(
        document.querySelector(
          `[data-contact-table-head="${section.key}"]`
        ),
        section.columns
      );
    });
    return;
  }

  const head = document.querySelector('[data-table-head]');
  if (!head) return;

  renderTableHead(head, config.columns);
}

function renderTable() {
  if (!config) return;

  if (page === 'contact-us') {
    renderContactTables();
    return;
  }

  const body = document.querySelector('[data-table-body]');
  if (!body) return;

  setCount(`${state.filtered.length} ${config.title} records found`);

  if (!state.filtered.length) {
    body.innerHTML = `
      <tr>
        <td
          colspan="${config.columns.length + 1}"
          class="empty-cell"
        >
          No matching ${esc(config.title)} records found.
        </td>
      </tr>
    `;
    return;
  }

  body.innerHTML = state.filtered
    .map((record, index) => {
      const cells = config.columns
        .map(([field]) => renderTableCell(field, record))
        .join('');

      return `
        <tr data-row-index="${index}">
          ${cells}
          <td>
            <button
              class="table-action-link"
              type="button"
              data-view-index="${index}"
            >
              View / Edit
            </button>
          </td>
        </tr>
      `;
    })
    .join('');
}

function detailRows(record) {'''

    return replace_exactly_once(
        content,
        render_block_pattern,
        render_block_replacement,
        "Contact Us table renderer replacement",
    )


def patch_admin_css(content: str) -> str:
    css_block = r'''
/* batch60e-contact-split-tables */
.contact-table-stack {
  display: grid;
  gap: 20px;
}

.contact-type-table {
  min-height: 0;
}

.contact-type-table .panel-header {
  align-items: center;
  margin-bottom: 14px;
}

.contact-type-table .panel-header .eyebrow {
  margin-bottom: 5px;
}

.contact-type-table .panel-header h2 {
  font-size: 1.08rem;
}

.contact-type-table .lead-table-wrap {
  max-height: none;
}

.contact-type-table .admin-data-table {
  min-width: 880px;
}

.contact-type-table[data-contact-table="person"] .admin-data-table {
  min-width: 1120px;
}

.contact-type-table .panel-tag {
  white-space: nowrap;
}

@media (max-width: 760px) {
  .contact-table-stack {
    gap: 16px;
  }

  .contact-type-table .panel-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
'''

    return content.rstrip() + "\n\n" + css_block.strip() + "\n"


def verify_markers(
    contact_html: str,
    admin_cms: str,
    admin_css: str,
) -> None:
    required = {
        "Company Contact table": 'data-contact-table="company"',
        "Contact Person table": 'data-contact-table="person"',
        "Social Media table": 'data-contact-table="social"',
        "Contact table configurations": "const contactTableConfigs",
        "Contact table renderer": "function renderContactTables()",
        "Batch CSS marker": "/* batch60e-contact-split-tables */",
    }

    combined = "\n".join((contact_html, admin_cms, admin_css))
    missing = [
        description
        for description, marker in required.items()
        if marker not in combined
    ]

    if missing:
        raise RuntimeError(
            "Batch verification markers are missing: "
            + ", ".join(missing)
        )


def run_optional_node_check(admin_cms_path: Path) -> None:
    node = shutil.which("node")
    if not node:
        print(
            "WARNING: Node.js was not found. "
            "JavaScript syntax validation was skipped."
        )
        return

    result = subprocess.run(
        [node, "--check", str(admin_cms_path)],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            "Node syntax validation failed for admin-cms.js:\n"
            + message
        )


def parse_args() -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(
        description=(
            "Apply RSA CMS Batch 60E — Admin Contact Split Tables."
        )
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=default_root,
        help=(
            "RSA CMS repository root. Defaults to the repository inferred "
            "from backend/scripts."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()

    contact_html_path = (
        project_root / "frontend" / "admin" / "contact-us.html"
    )
    admin_cms_path = (
        project_root
        / "frontend"
        / "admin"
        / "assets"
        / "js"
        / "admin-cms.js"
    )
    admin_css_path = (
        project_root
        / "frontend"
        / "admin"
        / "assets"
        / "css"
        / "admin.css"
    )

    target_paths = [
        contact_html_path,
        admin_cms_path,
        admin_css_path,
    ]

    backup_root: Path | None = None

    try:
        verify_clean_main(project_root)

        for path in target_paths:
            if not path.exists():
                raise RuntimeError(f"Required file not found: {path}")

        source_files = {
            path: read_text_file(path)
            for path in target_paths
        }

        if any(
            BATCH_MARKER in source.text
            for source in source_files.values()
        ):
            raise RuntimeError(
                "Batch 60E marker already exists. "
                "The batch appears to have been applied previously."
            )

        backup_root = create_backup(project_root, target_paths)

        try:
            patched_contact_html = patch_contact_html(
                source_files[contact_html_path].text
            )
            patched_admin_cms = patch_admin_cms(
                source_files[admin_cms_path].text
            )
            patched_admin_css = patch_admin_css(
                source_files[admin_css_path].text
            )

            verify_markers(
                patched_contact_html,
                patched_admin_cms,
                patched_admin_css,
            )

            write_text_file(
                source_files[contact_html_path],
                patched_contact_html,
            )
            write_text_file(
                source_files[admin_cms_path],
                patched_admin_cms,
            )
            write_text_file(
                source_files[admin_css_path],
                patched_admin_css,
            )

            run_optional_node_check(admin_cms_path)
            run_git(project_root, "diff", "--check")

        except Exception:
            restore_backup(
                project_root,
                backup_root,
                target_paths,
            )
            raise

        print()
        print("Batch 60E applied successfully.")
        print(f"Backup: {backup_root}")
        print()
        print("Changed files:")
        status = run_git(project_root, "status", "--short")
        print(status or "(none)")
        print()
        print("Diff summary:")
        diff_stat = run_git(project_root, "diff", "--stat")
        print(diff_stat or "(none)")
        print()
        print(
            "Next: test the Contact Us admin page locally. "
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
