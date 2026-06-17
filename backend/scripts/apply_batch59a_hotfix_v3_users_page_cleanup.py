from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_HTML = ROOT / "frontend" / "admin" / "settings.html"
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
ADMIN_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-users-59a.js"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_v3_users_page_cleanup.md"
MARKER = "batch59a-hotfix-v3-users-page-cleanup"

FA_LINK = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />'

NAV_ICON_MAP = {
    "Dashboard": "fa-solid fa-gauge-high",
    "Products": "fa-solid fa-box-open",
    "Categories": "fa-solid fa-table-list",
    "Brands": "fa-solid fa-certificate",
    "Key Features": "fa-solid fa-star",
    "Customers": "fa-solid fa-users",
    "Bookings": "fa-solid fa-calendar-check",
    "Inquiries": "fa-solid fa-file-circle-question",
    "About Us": "fa-solid fa-address-card",
    "Project Gallery": "fa-solid fa-images",
    "Services": "fa-solid fa-screwdriver-wrench",
    "Contact Us": "fa-solid fa-address-book",
    "Settings": "fa-solid fa-gear",
    "Logout": "fa-solid fa-right-from-bracket",
}

CSS_APPEND = r'''

/* batch59a-hotfix-v3-users-page-cleanup */
/* Keep Settings > Users visually independent from the earlier settings cards. */
.settings-card[data-settings-users],
.settings-card[data-settings-users].settings-users-standalone {
  margin-top: 32px !important;
  border: 1px solid rgba(226, 232, 240, 0.95) !important;
  border-radius: 22px !important;
  background: #ffffff !important;
  box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06) !important;
  padding: 26px 28px 28px !important;
}

.settings-grid.panel + .settings-card[data-settings-users],
.settings-grid + .settings-card[data-settings-users] {
  margin-top: 32px !important;
}

/* Do not show a redundant count label above the table. The green status card already confirms load count. */
.settings-card[data-settings-users] .users-toolbar {
  justify-content: flex-end !important;
  margin-top: 28px !important;
  margin-bottom: 22px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-card[data-settings-users] .users-toolbar > strong {
  display: none !important;
}

.settings-card[data-settings-users] .users-toolbar-actions {
  display: flex !important;
  justify-content: flex-end !important;
  align-items: center !important;
  gap: 12px !important;
  width: auto !important;
}

.settings-card[data-settings-users] .users-table-wrap {
  margin-top: 0 !important;
  border: 1px solid rgba(226, 232, 240, 0.95) !important;
  border-radius: 18px !important;
  background: #ffffff !important;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.035) !important;
}

/* Hide the temporary password panel unless an actual password/code is present. */
.settings-card[data-settings-users] .users-temp-password[hidden],
.settings-card[data-settings-users] .users-temp-password:empty,
.settings-card[data-settings-users] .users-temp-password:not(:has(code)) {
  display: none !important;
}

/* Font Awesome icons inside the sidebar/page icons should render normally, not as empty squares. */
.admin-sidebar .nav-icon i,
.admin-page-heading .page-icon i,
.settings-card-heading > span i {
  display: inline-block;
  line-height: 1;
  font-size: 0.9rem;
}

/* Add/Edit user modal spacing polish. */
.user-add-card,
.user-edit-card {
  width: min(640px, calc(100vw - 44px)) !important;
  max-height: calc(100vh - 44px) !important;
  overflow: auto !important;
  padding: 34px 34px 30px !important;
  border-radius: 20px !important;
  gap: 18px !important;
}

.user-add-card form,
.user-edit-card form {
  display: grid !important;
  gap: 16px !important;
}

.user-add-card label,
.user-edit-card label {
  gap: 8px !important;
}

.user-add-card input,
.user-add-card select,
.user-edit-card input,
.user-edit-card select {
  min-height: 52px !important;
  padding: 13px 14px !important;
  border-radius: 12px !important;
}

.user-add-card .settings-actions,
.user-edit-card .settings-actions {
  margin-top: 8px !important;
  gap: 12px !important;
  flex-wrap: wrap !important;
}

.user-add-card .modal-close,
.user-edit-card .modal-close {
  top: 18px !important;
  right: 18px !important;
  width: 42px !important;
  height: 42px !important;
}

@media (max-width: 720px) {
  .settings-card[data-settings-users] {
    padding: 24px 20px !important;
  }
  .settings-card[data-settings-users] .users-toolbar-actions,
  .settings-card[data-settings-users] .users-toolbar-actions .admin-button {
    width: 100% !important;
  }
  .user-add-card,
  .user-edit-card {
    padding: 28px 22px 24px !important;
  }
}
'''

DOC_TEXT = """# Phase 8 Batch 59A Hotfix v3 — Settings Users Page Cleanup

Status: targeted Batch 59A UI cleanup after local browser testing

## Purpose

This hotfix corrects the remaining Settings > Users UI issues from local testing.

## Fixes

- Moves the Cognito Users section out of the earlier Settings grid so it is visually separated from the Account, Notifications, and System status cards.
- Removes the redundant visible `1 users` count above the Users table; the status message already shows the loaded count.
- Ensures sidebar icons render by adding/normalizing Font Awesome icons on Settings page navigation.
- Keeps Add User as a modal workflow.
- Keeps First Name and Last Name inside Add/Edit forms only; the table remains Full Name based.
- Keeps the empty temporary-password panel hidden unless an actual password is returned.
- Updates visible Settings system marker text from Batch 55D to Batch 59A where the old static marker is still present.

## Files changed

- `frontend/admin/settings.html`
- `frontend/admin/assets/css/admin.css`
- `docs/phase8_batch59a_hotfix_v3_users_page_cleanup.md`

## Not changed

- No Cognito route logic change.
- No IAM policy change.
- No DynamoDB users table.
- No EC2/deployment change.
"""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


def ensure_fontawesome(text: str) -> str:
    if "font-awesome" in text or "fontawesome" in text or "cdnjs.cloudflare.com/ajax/libs/font-awesome" in text:
        return text
    if '<link rel="stylesheet" href="./assets/css/admin.css" />' in text:
        return text.replace('<link rel="stylesheet" href="./assets/css/admin.css" />', FA_LINK + '\n  <link rel="stylesheet" href="./assets/css/admin.css" />', 1)
    return text.replace("</head>", f"  {FA_LINK}\n</head>", 1)


def normalize_sidebar_icons(text: str) -> str:
    # Replace only the icon content in nav rows where the label is known.
    for label, icon in NAV_ICON_MAP.items():
        pattern = re.compile(
            r'(<a class="nav-item[^"]*"[^>]*>\s*<span class="nav-icon">)(.*?)(</span>\s*<span>' + re.escape(label) + r'</span>\s*</a>)',
            flags=re.DOTALL,
        )
        text = pattern.sub(r'\1<i class="' + icon + r'" aria-hidden="true"></i>\3', text)
    return text


def update_static_batch_marker(text: str) -> str:
    replacements = {
        "Batch 55D - Admin Page Finalization": "Batch 59A - Cognito Groups + Users",
        "batch55d-admin-page-finalization": "batch59a-cognito-groups-settings-users",
        "Batch 55D Admin Page Finalization": "Batch 59A Cognito Groups + Users",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def move_users_section_out_of_settings_grid(text: str) -> str:
    article_start = text.find('<article class="settings-card settings-card-wide" data-settings-users')
    if article_start == -1:
        article_start = text.find('<article class="settings-card settings-card-wide settings-users-standalone" data-settings-users')
    if article_start == -1:
        print("[warn] Users article not found; separation move skipped.")
        return text

    grid_start = text.rfind('<section class="settings-grid panel"', 0, article_start)
    if grid_start == -1:
        print("[skip] Users section already appears outside the settings grid or grid marker not found.")
        return text

    grid_close_start = text.find('      </section>', grid_start)
    if grid_close_start == -1:
        print("[warn] Settings grid close marker not found; separation move skipped.")
        return text

    if not (grid_start < article_start < grid_close_start):
        print("[skip] Users section already separated from settings grid.")
        return text

    # Capture everything from users article through user modals before the settings-grid closing section.
    users_block = text[article_start:grid_close_start].strip("\n")
    if 'settings-users-standalone' not in users_block:
        users_block = users_block.replace('class="settings-card settings-card-wide" data-settings-users', 'class="settings-card settings-card-wide settings-users-standalone" data-settings-users', 1)

    text_without_users = text[:article_start] + text[grid_close_start:]
    new_grid_close_start = text_without_users.find('      </section>', grid_start)
    if new_grid_close_start == -1:
        return text_without_users
    insert_at = new_grid_close_start + len('      </section>')
    separated_block = "\n\n" + users_block + "\n"
    print("[ok] Moved Settings > Users out of the earlier settings grid.")
    return text_without_users[:insert_at] + separated_block + text_without_users[insert_at:]


def patch_settings_html() -> None:
    if not SETTINGS_HTML.exists():
        raise SystemExit(f"[fail] Missing {rel(SETTINGS_HTML)}")
    text = read(SETTINGS_HTML)
    original = text
    text = ensure_fontawesome(text)
    text = normalize_sidebar_icons(text)
    text = update_static_batch_marker(text)
    text = move_users_section_out_of_settings_grid(text)
    if text != original:
        write(SETTINGS_HTML, text)
    else:
        print(f"[skip] No settings.html changes needed in {rel(SETTINGS_HTML)}")


def patch_css() -> None:
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")
    text = read(ADMIN_CSS)
    if MARKER in text:
        print(f"[skip] CSS cleanup already present in {rel(ADMIN_CSS)}")
        return
    write(ADMIN_CSS, text.rstrip() + CSS_APPEND)


def main() -> None:
    print(f"[start] Applying {MARKER}")
    patch_settings_html()
    patch_css()
    write(DOC, DOC_TEXT)
    print(f"[done] {MARKER} applied.")
    print("[done] Users section separated from earlier Settings cards, redundant count hidden, sidebar icons normalized.")
    print("[done] No Cognito backend, IAM, DynamoDB, EC2, Route 53, CloudFront, or paid notification change.")


if __name__ == "__main__":
    main()
