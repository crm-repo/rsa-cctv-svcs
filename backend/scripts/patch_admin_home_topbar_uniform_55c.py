from pathlib import Path

CSS_PATH = Path("frontend/admin/assets/css/admin.css")
MARKER_START = "/* batch55c-admin-home-topbar-uniform-polish START */"
MARKER_END = "/* batch55c-admin-home-topbar-uniform-polish END */"

CSS_BLOCK = f"""
{MARKER_START}
/* CSS-only polish for the admin dashboard top-right controls.
   Keeps Search, notification, and Admin User controls at one uniform height. */
.admin-topbar .topbar-actions {{
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}}

.admin-topbar .topbar-actions .search-box {{
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  width: clamp(260px, 26vw, 330px);
  min-width: 260px;
  min-height: 56px;
  height: 56px;
  margin: 0;
  padding: 0 16px;
  box-sizing: border-box;
}}

.admin-topbar .topbar-actions .search-box span {{
  flex: 0 0 auto;
  margin: 0;
  line-height: 1;
  white-space: nowrap;
}}

.admin-topbar .topbar-actions .search-box input {{
  flex: 1 1 auto;
  min-width: 0;
  height: 100%;
  padding: 0;
  border: 0;
  outline: 0;
  background: transparent;
}}

.admin-topbar .topbar-actions .icon-button {{
  display: grid;
  place-items: center;
  width: 56px;
  min-width: 56px;
  height: 56px;
  min-height: 56px;
  padding: 0;
  box-sizing: border-box;
}}

.admin-topbar .topbar-actions .admin-avatar {{
  min-height: 56px;
  height: 56px;
  margin: 0;
  padding: 8px 14px 8px 8px;
  box-sizing: border-box;
}}

.admin-topbar .topbar-actions .admin-avatar > span {{
  flex: 0 0 38px;
}}

@media (max-width: 980px) {{
  .admin-topbar .topbar-actions {{
    align-items: stretch;
  }}

  .admin-topbar .topbar-actions .search-box,
  .admin-topbar .topbar-actions .admin-avatar {{
    width: 100%;
    min-width: 0;
    height: 56px;
  }}

  .admin-topbar .topbar-actions .icon-button {{
    width: 56px;
    flex: 0 0 56px;
  }}
}}
{MARKER_END}
""".strip() + "\n"


def remove_existing_block(text: str) -> str:
    start = text.find(MARKER_START)
    if start == -1:
        return text
    end = text.find(MARKER_END, start)
    if end == -1:
        raise SystemExit("[fail] Existing topbar polish marker start found without marker end.")
    end += len(MARKER_END)
    while end < len(text) and text[end] in "\r\n":
        end += 1
    return text[:start].rstrip() + "\n\n" + text[end:].lstrip()


def main() -> None:
    if not CSS_PATH.exists():
        raise SystemExit(f"[fail] Missing {CSS_PATH}")

    # Read/write as UTF-8 text only for CSS. This patch does not touch HTML/JS/icon files.
    text = CSS_PATH.read_text(encoding="utf-8")
    text = remove_existing_block(text)
    if not text.endswith("\n"):
        text += "\n"
    text = text.rstrip() + "\n\n" + CSS_BLOCK
    CSS_PATH.write_text(text, encoding="utf-8", newline="\n")

    print("[done] batch55c-admin-home-topbar-uniform-polish applied")
    print("[done] CSS-only change: frontend/admin/assets/css/admin.css")
    print("[done] No HTML, JS, icon, backend/API, DynamoDB, or runtime behavior change.")


if __name__ == "__main__":
    main()
