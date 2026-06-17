from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN_CSS = ROOT / "frontend" / "admin" / "assets" / "css" / "admin.css"
ADMIN_JS = ROOT / "frontend" / "admin" / "assets" / "js" / "admin-users-59a.js"
DOC = ROOT / "docs" / "phase8_batch59a_hotfix_v2_users_ui_polish.md"
MARKER = "batch59a-hotfix-v2-users-ui-polish"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(path)}")


CSS_APPEND = r'''

/* batch59a-hotfix-v2-users-ui-polish */
/* Hide the one-time temporary-password panel unless it actually contains a password. */
.users-temp-password[hidden],
.users-temp-password:empty,
.users-temp-password:not(:has(code)) {
  display: none !important;
}

/* Make Settings > Users read like the other admin pages: control area and table area are separated cards. */
.settings-card[data-settings-users] {
  gap: 22px;
}

.settings-card[data-settings-users] .settings-card-heading + .settings-note {
  margin-bottom: 6px;
}

.settings-card[data-settings-users] .users-toolbar {
  margin-top: 14px;
  padding: 18px 20px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
}

.settings-card[data-settings-users] .users-toolbar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.settings-card[data-settings-users] .users-table-wrap {
  margin-top: 0;
  padding: 0;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
  overflow: auto;
}

.settings-card[data-settings-users] .users-table {
  margin: 0;
  min-width: 1040px;
}

/* Add/Edit user modal spacing polish. */
.user-add-card,
.user-edit-card {
  width: min(640px, calc(100vw - 44px));
  max-height: calc(100vh - 44px);
  overflow: auto;
  padding: 34px 34px 30px;
  border-radius: 20px;
  gap: 18px;
}

.user-add-card .eyebrow,
.user-edit-card .eyebrow {
  margin-bottom: 2px;
}

.user-add-card h2,
.user-edit-card h2 {
  margin: 0;
}

.user-add-card .settings-note,
.user-edit-card .settings-note {
  margin: 0 0 4px;
}

.user-add-card form,
.user-edit-card form {
  display: grid;
  gap: 16px;
}

.user-add-card label,
.user-edit-card label {
  gap: 8px;
}

.user-add-card input,
.user-add-card select,
.user-edit-card input,
.user-edit-card select {
  min-height: 52px;
  padding: 13px 14px;
  border-radius: 12px;
}

.user-add-card .settings-actions,
.user-edit-card .settings-actions {
  margin-top: 8px;
  gap: 12px;
  flex-wrap: wrap;
}

.user-add-card .settings-actions .admin-button,
.user-edit-card .settings-actions .admin-button {
  min-height: 48px;
}

.user-add-card .modal-close,
.user-edit-card .modal-close {
  top: 18px;
  right: 18px;
  width: 42px;
  height: 42px;
}

@media (max-width: 720px) {
  .settings-card[data-settings-users] .users-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .settings-card[data-settings-users] .users-toolbar-actions,
  .settings-card[data-settings-users] .users-toolbar-actions .admin-button {
    width: 100%;
  }

  .user-add-card,
  .user-edit-card {
    padding: 28px 22px 24px;
  }
}
'''

DOC_TEXT = """# Phase 8 Batch 59A Hotfix v2 — Users UI Polish

Status: hotfix for Batch 59A local UI testing

## Purpose

This hotfix corrects the Settings > Users visual issues found after the Cognito users API started loading successfully.

## Fixes

- Hides the empty red temporary-password panel. It should only appear after Create User or Reset Password when a one-time password is returned.
- Keeps the Users table as a Full Name table. First Name and Last Name remain inside the Add/Edit User modal only.
- Separates the Users toolbar/card area and the Users table area visually, matching the other admin pages where filters/toolbars and tables are separate cards.
- Improves Add/Edit User modal spacing, input height, action button spacing, and close-button spacing.

## Files changed

- `frontend/admin/assets/css/admin.css`
- `frontend/admin/assets/js/admin-users-59a.js` only receives a small defensive helper to keep the temporary-password panel hidden when empty.

## Not changed

- No Cognito backend route changes.
- No IAM policy changes.
- No DynamoDB users table.
- No EC2/deployment change.
"""

JS_HELPER = r'''

  // batch59a-hotfix-v2-users-ui-polish
  function batch59aUiPolishHideEmptyTempPassword() {
    const panel = qs('[data-temp-password-panel]');
    if (!panel) return;
    const hasPassword = !!panel.querySelector('code');
    if (!hasPassword) {
      panel.hidden = true;
      panel.innerHTML = '';
    }
  }
'''


def patch_css() -> None:
    if not ADMIN_CSS.exists():
        raise SystemExit(f"[fail] Missing {rel(ADMIN_CSS)}")
    text = read(ADMIN_CSS)
    if MARKER in text:
        print(f"[skip] CSS polish already present in {rel(ADMIN_CSS)}")
        return
    write(ADMIN_CSS, text.rstrip() + CSS_APPEND)


def patch_js() -> None:
    if not ADMIN_JS.exists():
        print(f"[warn] Missing {rel(ADMIN_JS)}; CSS-only hotfix applied.")
        return
    text = read(ADMIN_JS)
    changed = False
    if "batch59aUiPolishHideEmptyTempPassword" not in text:
        anchor = "  function qsa(selector, root) { return Array.from((root || document).querySelectorAll(selector)); }\n"
        if anchor in text:
            text = text.replace(anchor, anchor + JS_HELPER, 1)
            changed = True
            print(f"[ok] Added empty temp-password defensive helper to {rel(ADMIN_JS)}")
        else:
            print(f"[warn] Could not find JS helper anchor in {rel(ADMIN_JS)}")
    if "batch59aUiPolishHideEmptyTempPassword();" not in text:
        anchor2 = "    loadUsers();"
        if anchor2 in text:
            text = text.replace(anchor2, "    batch59aUiPolishHideEmptyTempPassword();\n    loadUsers();", 1)
            changed = True
            print(f"[ok] Added temp-password hide call before loadUsers in {rel(ADMIN_JS)}")
        else:
            print(f"[warn] Could not find loadUsers call in {rel(ADMIN_JS)}")
    if changed:
        write(ADMIN_JS, text)
    else:
        print(f"[skip] JS polish already present or no JS change needed in {rel(ADMIN_JS)}")


def main() -> None:
    print(f"[start] Applying {MARKER}")
    patch_css()
    patch_js()
    write(DOC, DOC_TEXT)
    print(f"[done] {MARKER} applied.")
    print("[done] Empty red temp-password panel hidden; Users toolbar/table separated; modal spacing polished.")


if __name__ == "__main__":
    main()
