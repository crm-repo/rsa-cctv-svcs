from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATCH_MARKER = "batch55c-hotfix-v3-admin-polish-final-sweep"
ADMIN = ROOT / "frontend" / "admin"

NAV_ITEMS = [
    ("index", "Dashboard", "./index.html", "fa-solid fa-gauge-high"),
    ("_heading", "Catalog", "", ""),
    ("products", "Products", "./products.html", "fa-solid fa-boxes-stacked"),
    ("categories", "Categories", "./categories.html", "fa-solid fa-layer-group"),
    ("brands", "Brands", "./brands.html", "fa-solid fa-tags"),
    ("key-features", "Key Features", "./key-features.html", "fa-solid fa-list-check"),
    ("_heading", "CRM", "", ""),
    ("customers", "Customers", "./customers.html", "fa-solid fa-users"),
    ("bookings", "Bookings", "./bookings.html", "fa-solid fa-calendar-check"),
    ("inquiries", "Inquiries", "./inquiries.html", "fa-solid fa-envelope-open-text"),
    ("_heading", "CMS", "", ""),
    ("about", "About Us", "./about.html", "fa-solid fa-circle-info"),
    ("project-gallery", "Project Gallery", "./project-gallery.html", "fa-solid fa-images"),
    ("services", "Services", "./services.html", "fa-solid fa-screwdriver-wrench"),
    ("contact-us", "Contact Us", "./contact-us.html", "fa-solid fa-address-book"),
    ("_heading", "System", "", ""),
]


def page_key(path: Path) -> str:
    stem = path.stem
    return "index" if stem == "index" else stem


def build_nav(active: str) -> str:
    lines = ['      <nav class="admin-nav" data-admin-nav="true">']
    for key, label, href, icon in NAV_ITEMS:
        if key == "_heading":
            lines.append(f'        <p class="nav-heading">{label}</p>')
        else:
            active_class = " is-active" if key == active else ""
            lines.append(f'        <a class="nav-item{active_class}" href="{href}"><span class="nav-icon"><i class="{icon}"></i></span><span>{label}</span></a>')
    lines.append('        <a class="nav-item is-disabled" href="#" aria-disabled="true"><span class="nav-icon"><i class="fa-solid fa-gear"></i></span><span>Settings</span></a>')
    lines.append('        <button class="nav-item nav-item-button" type="button" data-admin-logout><span class="nav-icon"><i class="fa-solid fa-right-from-bracket"></i></span><span>Logout</span></button>')
    lines.append('      </nav>')
    return "\n".join(lines)


def replace_nav(text: str, active: str) -> str:
    return re.sub(r'      <nav class="admin-nav"[\s\S]*?      </nav>', build_nav(active), text, count=1)


def ensure_script(text: str, page: str) -> str:
    tag = '<script src="./assets/js/admin-polish-v3.js"></script>'
    if tag in text or 'admin-polish-v3.js' in text:
        return text
    targets = [
        '<script src="./assets/js/admin-dashboard.js"></script>',
        '<script src="./assets/js/admin-catalog.js"></script>',
        '<script src="./assets/js/admin-cms.js"></script>',
        '<script src="./assets/js/admin-leads.js"></script>',
    ]
    for target in targets:
        if target in text:
            return text.replace(target, f'{tag}\n  {target}', 1)
    if page == 'login' and '<script>' in text:
        return text.replace('<script>', f'{tag}\n  <script>', 1)
    return text.replace('</body>', f'  {tag}\n</body>', 1)


def clean_admin_html(path: Path) -> None:
    text = path.read_text(encoding='utf-8')
    original = text
    active = page_key(path)
    if path.name != 'login.html':
        text = replace_nav(text, active)
        text = ensure_script(text, active)
    else:
        text = ensure_script(text, 'login')
        text = text.replace('Checking admin authentication configuration…', 'Preparing admin sign-in…')
        text = text.replace('Checking admin auth configuration…', '')
        text = text.replace('No sign-in is required while local auth is disabled.', '')
        text = text.replace('Local preview mode', 'Password')
        text = text.replace('Continue to Dashboard', 'Sign In')
        text = text.replace('Open Dashboard', 'Sign In')
        text = text.replace('You have logged out. Local preview mode is active; continue only when you are ready to open the dashboard again.', 'You have been logged out.')
    text = re.sub(r'\s*<p class="helper-text">Use the left menu to open each admin management page\.</p>', '', text)
    text = text.replace('>All Products<', '>Products<')
    text = text.replace('<p class="nav-heading">Products</p>', '<p class="nav-heading">Catalog</p>')
    text = re.sub(r'\s*<a class="nav-item[^"]*" href="\.\/promotions\.html"[\s\S]*?</a>', '', text)
    text = text.replace('Local preview mode', '')
    text = text.replace('Unprotected until Cognito batch.', '')
    text = text.replace('Batch 55B', '')
    text = text.replace('Batch 55C', '')
    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f'[ok] Updated {path.relative_to(ROOT)}')


def write_polish_v3_js() -> None:
    js = r'''(function () {
  'use strict';

  const VERSION = 'batch55c-hotfix-v3-admin-polish-final-sweep';
  window.RSA_BATCH55C_HOTFIX_V3_VERSION = VERSION;

  const NAV_SPEC = [
    { type: 'link', key: 'index', label: 'Dashboard', href: './index.html', icon: 'fa-solid fa-gauge-high' },
    { type: 'heading', label: 'Catalog' },
    { type: 'link', key: 'products', label: 'Products', href: './products.html', icon: 'fa-solid fa-boxes-stacked' },
    { type: 'link', key: 'categories', label: 'Categories', href: './categories.html', icon: 'fa-solid fa-layer-group' },
    { type: 'link', key: 'brands', label: 'Brands', href: './brands.html', icon: 'fa-solid fa-tags' },
    { type: 'link', key: 'key-features', label: 'Key Features', href: './key-features.html', icon: 'fa-solid fa-list-check' },
    { type: 'heading', label: 'CRM' },
    { type: 'link', key: 'customers', label: 'Customers', href: './customers.html', icon: 'fa-solid fa-users' },
    { type: 'link', key: 'bookings', label: 'Bookings', href: './bookings.html', icon: 'fa-solid fa-calendar-check' },
    { type: 'link', key: 'inquiries', label: 'Inquiries', href: './inquiries.html', icon: 'fa-solid fa-envelope-open-text' },
    { type: 'heading', label: 'CMS' },
    { type: 'link', key: 'about', label: 'About Us', href: './about.html', icon: 'fa-solid fa-circle-info' },
    { type: 'link', key: 'project-gallery', label: 'Project Gallery', href: './project-gallery.html', icon: 'fa-solid fa-images' },
    { type: 'link', key: 'services', label: 'Services', href: './services.html', icon: 'fa-solid fa-screwdriver-wrench' },
    { type: 'link', key: 'contact-us', label: 'Contact Us', href: './contact-us.html', icon: 'fa-solid fa-address-book' },
    { type: 'heading', label: 'System' }
  ];

  function pageKey() {
    const appPage = document.querySelector('[data-admin-app]')?.getAttribute('data-admin-page');
    if (appPage) return appPage;
    const file = (window.location.pathname.split('/').pop() || 'index.html').replace('.html', '');
    return file === 'index' || file === '' ? 'index' : file;
  }

  function normalizeSidebar() {
    const nav = document.querySelector('.admin-nav');
    if (!nav) return;
    const active = pageKey();
    nav.dataset.adminNav = 'true';
    nav.innerHTML = NAV_SPEC.map(item => {
      if (item.type === 'heading') return `<p class="nav-heading">${item.label}</p>`;
      const isActive = item.key === active ? ' is-active' : '';
      return `<a class="nav-item${isActive}" href="${item.href}"><span class="nav-icon"><i class="${item.icon}"></i></span><span>${item.label}</span></a>`;
    }).join('') + `<a class="nav-item is-disabled" href="#" aria-disabled="true"><span class="nav-icon"><i class="fa-solid fa-gear"></i></span><span>Settings</span></a><button class="nav-item nav-item-button" type="button" data-admin-logout><span class="nav-icon"><i class="fa-solid fa-right-from-bracket"></i></span><span>Logout</span></button>`;
  }

  function removeVisibleNotes() {
    document.querySelectorAll('.helper-text').forEach(el => {
      if (/left menu|admin management page/i.test(el.textContent || '')) el.remove();
    });
    document.querySelectorAll('.admin-auth-dev-badge').forEach(el => el.remove());
    document.querySelectorAll('[data-admin-login-status]').forEach(el => {
      if (/local preview|auth configuration|local auth|mock login/i.test(el.textContent || '')) el.textContent = '';
    });
    document.querySelectorAll('[data-admin-login-note]').forEach(el => {
      el.textContent = (el.textContent || '')
        .replace(/Local preview mode is active;?/gi, '')
        .replace(/continue only when you are ready to open the dashboard again\.?/gi, '')
        .trim();
      if (!el.textContent) el.remove();
    });
  }

  function sortOptions(includeDisplaySeq) {
    return `<option value="recent" selected>Most Recent</option>${includeDisplaySeq ? '<option value="display_seq">Display Seq</option>' : ''}<option value="oldest">Oldest First</option><option value="az">Name A-Z</option><option value="za">Name Z-A</option>`;
  }

  function ensureSortToolbar() {
    const page = pageKey();
    const catalogPages = new Set(['products', 'categories', 'brands', 'key-features']);
    const cmsPages = new Set(['about', 'project-gallery', 'services', 'contact-us']);
    const crmPages = new Set(['customers', 'bookings', 'inquiries']);
    const includeDisplaySeq = ['products', 'categories', 'brands', 'project-gallery', 'services', 'contact-us'].includes(page);

    const group = document.querySelector('.catalog-toolbar-group, .lead-toolbar-group');
    if (!group) return;

    if (catalogPages.has(page)) {
      group.querySelectorAll('label').forEach(label => {
        if (label.querySelector('[data-visibility-filter], [data-type-filter]') || /^\s*(Visibility|Type)\s*$/i.test(label.querySelector('span')?.textContent || '')) {
          label.remove();
        }
      });
      let sort = group.querySelector('[data-sort-filter]');
      if (!sort) {
        group.insertAdjacentHTML('afterbegin', `<label><span>Sort By</span><select data-sort-filter>${sortOptions(includeDisplaySeq)}</select></label>`);
      } else {
        const label = sort.closest('label');
        const span = label ? label.querySelector('span') : null;
        if (span) span.textContent = 'Sort By';
        sort.innerHTML = sortOptions(includeDisplaySeq);
        sort.value = 'recent';
      }
    }

    if (cmsPages.has(page)) {
      let sort = group.querySelector('[data-sort-filter]');
      if (!sort) {
        group.insertAdjacentHTML('afterbegin', `<label><span>Sort By</span><select data-sort-filter>${sortOptions(includeDisplaySeq)}</select></label>`);
      } else {
        const label = sort.closest('label');
        const span = label ? label.querySelector('span') : null;
        if (span) span.textContent = 'Sort By';
        if (!sort.querySelector('option[value="display_seq"]') && includeDisplaySeq) sort.innerHTML = sortOptions(true);
        sort.value = 'recent';
      }
    }

    if (crmPages.has(page)) {
      const sort = group.querySelector('[data-sort-filter]');
      if (sort) {
        const label = sort.closest('label');
        const span = label ? label.querySelector('span') : null;
        if (span) span.textContent = 'Sort By';
        sort.value = 'recent';
      }
    }
  }

  function normalizeDashboardLayout() {
    const grid = document.querySelector('.dashboard-grid');
    if (!grid || grid.dataset.v3Masonry === 'true') return;
    const panels = Array.from(grid.children).filter(child => child.classList && child.classList.contains('panel'));
    if (panels.length < 4) return;

    const left = document.createElement('div');
    const right = document.createElement('div');
    left.className = 'dashboard-column dashboard-column-left';
    right.className = 'dashboard-column dashboard-column-right';

    panels.forEach(panel => {
      const text = (panel.textContent || '').toLowerCase();
      if (text.includes('latest inquiries') || text.includes('sale / low stock') || text.includes('lead summary')) {
        right.appendChild(panel);
      } else {
        left.appendChild(panel);
      }
    });

    grid.textContent = '';
    grid.classList.add('dashboard-masonry');
    grid.dataset.v3Masonry = 'true';
    grid.append(left, right);
  }

  function normalizeMediaLabels() {
    document.querySelectorAll('input[name="image_path"], input[name="brand_logo_path"], input[name="person_image_path"], input[name="service_image_path"], input[name="project_image_path"], input[name="hero_image_path"], input[name="logo_path"]').forEach(input => {
      const label = input.closest('label');
      if (label) label.classList.add('media-field-label', 'span-2');
    });
  }

  function init() {
    normalizeSidebar();
    removeVisibleNotes();
    ensureSortToolbar();
    normalizeDashboardLayout();
    normalizeMediaLabels();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.RSAAdminPolishV3 = { init, normalizeSidebar, ensureSortToolbar, normalizeDashboardLayout };
}());
'''
    target = ADMIN / 'assets/js/admin-polish-v3.js'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(js, encoding='utf-8')
    print(f'[ok] Wrote {target.relative_to(ROOT)}')


def append_css() -> None:
    css_path = ADMIN / 'assets/css/admin.css'
    css = css_path.read_text(encoding='utf-8') if css_path.exists() else ''
    block = r'''

/* batch55c-hotfix-v3-admin-polish-final-sweep */
.admin-nav .nav-item[href$="promotions.html"] { display: none !important; }
.admin-auth-dev-badge,
.helper-text { display: none !important; }

.dashboard-grid.dashboard-masonry {
  display: grid !important;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.85fr);
  gap: 18px;
  align-items: start;
}
.dashboard-column { display: grid; gap: 18px; min-width: 0; align-content: start; }
.dashboard-column > .panel { min-width: 0; }
.quick-actions {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 10px !important;
}
.quick-actions .quick-action-link { min-width: 0; width: 100%; }
.quick-actions .quick-action-link:last-child:nth-child(odd) { grid-column: 1 / 2; }

.drawer-header {
  border-bottom: 0 !important;
  padding-bottom: 10px !important;
}
.drawer-body { padding-top: 8px !important; }
.detail-drawer .catalog-form,
.detail-drawer .drawer-update-form,
.catalog-form,
.drawer-update-form {
  border-top: 0 !important;
}
.detail-drawer hr,
.catalog-form hr,
.drawer-update-form hr { display: none !important; }

.catalog-form-grid > label.media-field-label,
.catalog-form-grid > label:has(input[name="image_path"]),
.catalog-form-grid > label:has(input[name="brand_logo_path"]),
.catalog-form-grid > label:has(input[name="person_image_path"]),
.catalog-form-grid > label:has(input[name="service_image_path"]),
.catalog-form-grid > label:has(input[name="project_image_path"]),
.catalog-form-grid > label:has(input[name="hero_image_path"]),
.catalog-form-grid > label:has(input[name="logo_path"]),
.drawer-update-form > label.media-field-label,
.drawer-update-form > label:has(input[name="image_path"]),
.drawer-update-form > label:has(input[name="brand_logo_path"]),
.drawer-update-form > label:has(input[name="person_image_path"]),
.drawer-update-form > label:has(input[name="service_image_path"]),
.drawer-update-form > label:has(input[name="project_image_path"]),
.drawer-update-form > label:has(input[name="hero_image_path"]),
.drawer-update-form > label:has(input[name="logo_path"]) {
  grid-column: 1 / -1 !important;
  max-width: 100%;
  min-width: 0;
}
.admin-media-picker {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: stretch !important;
  gap: 8px !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
  overflow: visible !important;
  box-sizing: border-box !important;
}
.admin-media-picker .admin-media-filename {
  flex: 1 1 280px !important;
  min-width: 0 !important;
  max-width: 100% !important;
}
.admin-media-picker .admin-media-button,
.admin-media-picker .admin-media-clear,
.admin-media-picker .admin-media-restore {
  flex: 0 0 auto !important;
  max-width: 100% !important;
  white-space: nowrap !important;
}
.admin-media-picker .admin-media-note {
  flex: 1 0 100% !important;
  max-width: 100% !important;
  overflow-wrap: anywhere !important;
}
.catalog-form-grid label:has(select[name="show_flag"]) select,
.catalog-form-grid label:has(select[name="show_pack_flag"]) select {
  min-height: 44px !important;
  height: 44px !important;
}

@media (max-width: 1180px) {
  .dashboard-grid.dashboard-masonry { grid-template-columns: 1fr !important; }
}
@media (max-width: 720px) {
  .quick-actions { grid-template-columns: 1fr !important; }
  .admin-media-picker .admin-media-filename,
  .admin-media-picker .admin-media-button,
  .admin-media-picker .admin-media-clear,
  .admin-media-picker .admin-media-restore { flex: 1 1 100% !important; }
}
'''
    if PATCH_MARKER not in css:
        css_path.write_text(css.rstrip() + block + '\n', encoding='utf-8')
        print(f'[ok] Appended CSS to {css_path.relative_to(ROOT)}')


def patch_dashboard_js() -> None:
    path = ADMIN / 'assets/js/admin-dashboard.js'
    if not path.exists():
        return
    text = path.read_text(encoding='utf-8')
    original = text
    text = text.replace("setStatus('is-warning', 'Action unavailable.', 'Use the left menu to open the matching admin page.');", "setStatus('is-warning', 'Action unavailable.', 'This admin section is not active yet.');")
    if PATCH_MARKER not in text:
        text = text.replace("'use strict';", "'use strict';\n\n  const BATCH55C_HOTFIX_V3_VERSION = 'batch55c-hotfix-v3-admin-polish-final-sweep';\n  window.RSA_BATCH55C_DASHBOARD_HOTFIX_V3_VERSION = BATCH55C_HOTFIX_V3_VERSION;", 1)
    if text != original:
        path.write_text(text, encoding='utf-8')
        print(f'[ok] Updated {path.relative_to(ROOT)}')


def patch_media_css() -> None:
    path = ADMIN / 'assets/css/admin-media.css'
    if not path.exists():
        return
    css = path.read_text(encoding='utf-8')
    block = r'''

/* batch55c-hotfix-v3-admin-polish-final-sweep */
.admin-media-picker {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: stretch !important;
  gap: 8px !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: visible !important;
}
.admin-media-picker .admin-media-filename { flex: 1 1 280px !important; min-width: 0 !important; }
.admin-media-picker .admin-media-button,
.admin-media-picker .admin-media-clear,
.admin-media-picker .admin-media-restore { flex: 0 0 auto !important; white-space: nowrap !important; }
.admin-media-note { flex: 1 0 100% !important; overflow-wrap: anywhere !important; }
'''
    if PATCH_MARKER not in css:
        path.write_text(css.rstrip() + block + '\n', encoding='utf-8')
        print(f'[ok] Appended CSS to {path.relative_to(ROOT)}')


def main() -> None:
    if not ADMIN.exists():
        raise SystemExit(f'Admin folder not found: {ADMIN}')
    for path in sorted(ADMIN.glob('*.html')):
        clean_admin_html(path)
    write_polish_v3_js()
    append_css()
    patch_media_css()
    patch_dashboard_js()
    print('[done] Batch 55C-Hotfix v3 admin polish final sweep applied.')
    print('[note] No DynamoDB tables were deleted, no counters were reset, and no S3/upload storage was enabled.')

if __name__ == '__main__':
    main()
