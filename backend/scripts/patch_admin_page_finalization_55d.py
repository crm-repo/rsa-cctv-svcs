from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADMIN = ROOT / "frontend" / "admin"
PATCH_MARKER = "batch55d-admin-page-finalization"
UTILITY_SCRIPT = '<script src="./assets/js/admin-header-utilities-55d.js"></script>'

BAD_TOKENS = [
    "admin-icon-consistency-55c",
    "batch55c-admin-icon-consistency-update",
    "fa-boxes-stackedes-stacked",
    "\ufffd",
    "â",
]

NAV_ITEMS = [
    ("index", "Dashboard", "./index.html", "fa-solid fa-chart-column"),
    ("_heading", "Catalog", "", ""),
    ("products", "Products", "./products.html", "fa-solid fa-box-open"),
    ("categories", "Categories", "./categories.html", "fa-solid fa-table-list"),
    ("brands", "Brands", "./brands.html", "fa-solid fa-certificate"),
    ("key-features", "Key Features", "./key-features.html", "fa-solid fa-star"),
    ("_heading", "CRM", "", ""),
    ("customers", "Customers", "./customers.html", "fa-solid fa-users"),
    ("bookings", "Bookings", "./bookings.html", "fa-solid fa-calendar-check"),
    ("inquiries", "Inquiries", "./inquiries.html", "fa-solid fa-file-circle-question"),
    ("_heading", "CMS", "", ""),
    ("about", "About Us", "./about.html", "fa-solid fa-address-card"),
    ("project-gallery", "Project Gallery", "./project-gallery.html", "fa-solid fa-images"),
    ("services", "Services", "./services.html", "fa-solid fa-screwdriver-wrench"),
    ("contact-us", "Contact Us", "./contact-us.html", "fa-solid fa-address-book"),
    ("_heading", "System", "", ""),
    ("settings", "Settings", "./settings.html", "fa-solid fa-gear"),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def fail_if_bad_prestate() -> None:
    if not ADMIN.exists():
        raise SystemExit(f"[fail] Admin folder not found: {ADMIN}")

    offenders: list[str] = []
    targets = list(ADMIN.glob("*.html")) + list((ADMIN / "assets/js").glob("*.js")) + list((ADMIN / "assets/css").glob("*.css"))
    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            offenders.append(f"{rel(path)} is not valid UTF-8")
            continue
        for token in BAD_TOKENS:
            if token in text:
                offenders.append(f"{rel(path)} contains {token}")
    if offenders:
        raise SystemExit("[fail] Preflight stopped. Clean 55C rollback/residue first:\n" + "\n".join(offenders))


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
    lines.append('        <button class="nav-item nav-item-button" type="button" data-admin-logout><span class="nav-icon"><i class="fa-solid fa-right-from-bracket"></i></span><span>Logout</span></button>')
    lines.append('      </nav>')
    return "\n".join(lines)


def ensure_utility_script(text: str) -> str:
    if "admin-header-utilities-55d.js" in text:
        return text
    return text.replace("</body>", f"  {UTILITY_SCRIPT}\n</body>", 1)


def replace_nav(text: str, active: str) -> str:
    if '<nav class="admin-nav"' not in text:
        return text
    return re.sub(r'      <nav class="admin-nav"[\s\S]*?      </nav>', build_nav(active), text, count=1)


def patch_existing_admin_html(path: Path) -> bool:
    if path.name == "login.html":
        return False
    if path.name == "settings.html" and path.stat().st_size == 0:
        return False

    text = path.read_text(encoding="utf-8")
    original = text
    active = page_key(path)
    text = replace_nav(text, active)
    text = ensure_utility_script(text)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Updated {rel(path)}")
        return True
    return False


def write_settings_html() -> None:
    settings = ADMIN / "settings.html"
    nav = build_nav("settings")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Settings | RSA CMS Admin</title>
  <meta name="robots" content="noindex,nofollow" />
  <link rel="stylesheet" href="./assets/css/admin.css" />
  <link rel="stylesheet" href="./assets/css/admin-auth.css" />
  <link rel="stylesheet" href="./assets/css/admin-media.css" />
</head>
<body>
  <div class="admin-app" data-admin-app data-admin-page="settings">
    <aside class="admin-sidebar" aria-label="Admin navigation">
      <a class="brand-lockup" href="./index.html" aria-label="RSA CMS Admin Dashboard">
        <span class="brand-logo-wrap">
          <img src="./assets/images/rsa-logo.png" alt="RSA CCTV Installation Services" onerror="this.style.display='none'" />
          <span class="brand-logo-fallback" aria-hidden="true">RSA</span>
        </span>
        <span class="brand-copy"><strong>RSA CMS</strong><small>Mini-CRM Admin</small></span>
      </a>

{nav}
    </aside>

    <main class="admin-main">
      <header class="admin-topbar">
        <button class="sidebar-toggle" type="button" data-sidebar-toggle aria-label="Toggle navigation"><i class="fa-solid fa-bars"></i></button>
        <div><p class="eyebrow">System</p><h1>Settings</h1></div>
        <div class="topbar-actions">
          <label class="search-box"><span>Search</span><input type="search" placeholder="Search settings..." data-admin-search /></label>
          <button class="icon-button" type="button" aria-label="Notifications"><i class="fa-solid fa-bell"></i><span data-new-lead-count>0</span></button>
          <div class="admin-avatar" title="Admin User"><span>AD</span><div><strong>Admin User</strong><small>Admin</small></div></div>
        </div>
      </header>

      <section class="status-banner" data-status-banner><strong>Settings ready.</strong><span>Review admin session, in-app activity source, and system status.</span></section>

      <section class="admin-page-heading"><div class="page-icon"><i class="fa-solid fa-gear"></i></div><div><p class="eyebrow">Admin utilities</p><h2>Settings</h2><p>View account session details, notification source, and current system status.</p></div></section>

      <section class="settings-grid panel" data-settings-content>
        <article class="settings-card" data-settings-account>
          <div class="settings-card-heading"><span><i class="fa-solid fa-user-shield"></i></span><div><p class="eyebrow">Account &amp; Session</p><h2>Signed-in admin</h2></div></div>
          <dl class="settings-kv">
            <div><dt>Name</dt><dd data-settings-admin-name>Admin User</dd></div>
            <div><dt>Email</dt><dd data-settings-admin-email>Not available</dd></div>
            <div><dt>Role</dt><dd>Admin</dd></div>
            <div><dt>Auth mode</dt><dd data-settings-auth-mode>Checking session</dd></div>
          </dl>
          <div class="settings-actions"><button class="admin-button secondary" type="button" data-admin-logout>Logout</button></div>
        </article>

        <article class="settings-card" data-settings-notifications>
          <div class="settings-card-heading"><span><i class="fa-solid fa-bell"></i></span><div><p class="eyebrow">Notifications</p><h2>In-app activity source</h2></div></div>
          <p class="settings-note">Notification badge count is calculated from new or pending bookings plus new, unread, or open inquiries.</p>
          <dl class="settings-kv">
            <div><dt>Current count</dt><dd data-settings-notification-count>0</dd></div>
            <div><dt>Booking source</dt><dd>New and pending bookings</dd></div>
            <div><dt>Inquiry source</dt><dd>New, unread, and open inquiries</dd></div>
          </dl>
          <div class="settings-actions"><a class="admin-button secondary" href="./bookings.html">View Bookings</a><a class="admin-button secondary" href="./inquiries.html">View Inquiries</a></div>
        </article>

        <article class="settings-card settings-card-wide" data-settings-system>
          <div class="settings-card-heading"><span><i class="fa-solid fa-circle-check"></i></span><div><p class="eyebrow">System</p><h2>Admin app status</h2></div></div>
          <dl class="settings-kv settings-kv-wide">
            <div><dt>Admin app version</dt><dd data-settings-app-version>Batch 55D - Admin Page Finalization</dd></div>
            <div><dt>Data connection</dt><dd data-settings-api-status>Checking connection</dd></div>
            <div><dt>Current marker</dt><dd>{PATCH_MARKER}</dd></div>
          </dl>
        </article>
      </section>

      <footer class="admin-footer"><span>RSA CCTV Installation Services</span><span>Batch 55D Admin Page Finalization</span></footer>
    </main>
  </div>
  <script src="./assets/js/admin-auth.js"></script>
  <script src="./assets/js/admin-api.js"></script>
  <script src="./assets/js/admin-media.js"></script>
  <script src="./assets/js/admin-polish-v3.js"></script>
  {UTILITY_SCRIPT}
</body>
</html>
"""
    settings.write_text(html, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(settings)}")


def write_header_utility_js() -> None:
    target = ADMIN / "assets/js/admin-header-utilities-55d.js"
    js = r"""(function () {
  'use strict';

  const VERSION = 'batch55d-admin-page-finalization';
  window.RSA_BATCH55D_ADMIN_PAGE_FINALIZATION_VERSION = VERSION;

  const ACTION_BOOKING_STATUSES = new Set(['new', 'pending']);
  const ACTION_INQUIRY_STATUSES = new Set(['new', 'unread', 'open']);
  let activityCache = null;

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.from((root || document).querySelectorAll(selector));
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function decodeJwtPayload(token) {
    if (!token || typeof token !== 'string' || token.split('.').length < 2) return {};
    try {
      const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
      return JSON.parse(decodeURIComponent(Array.from(atob(padded)).map(ch => '%' + ch.charCodeAt(0).toString(16).padStart(2, '0')).join('')));
    } catch (error) {
      return {};
    }
  }

  function getStoredToken(key) {
    try { return window.localStorage.getItem(key) || ''; } catch (error) { return ''; }
  }

  function authModeLabel() {
    const configMode = window.RSAAdminAuth && window.RSAAdminAuth.config && window.RSAAdminAuth.config.mode;
    const storedMode = getStoredToken('rsa_admin_auth_mode');
    const mode = configMode || storedMode || '';
    if (mode === 'cognito') return 'Cognito';
    if (mode === 'mock') return 'Local preview fallback';
    if (mode === 'disabled') return 'Local preview fallback';
    return getStoredToken('rsa_admin_access_token') ? 'Cognito / local preview fallback' : 'Local preview fallback';
  }

  function getIdentity() {
    const idClaims = decodeJwtPayload(getStoredToken('rsa_admin_id_token'));
    const accessClaims = decodeJwtPayload(getStoredToken('rsa_admin_access_token'));
    const claims = Object.assign({}, accessClaims, idClaims);
    const username = claims['cognito:username'] || claims.username || claims.preferred_username || '';
    const email = claims.email || '';
    const name = claims.name || claims.given_name || email || username || 'Admin User';
    const displayName = String(name).trim() || 'Admin User';
    const initials = displayName.split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'AD';
    return {
      name: displayName,
      email: email || '',
      username: username || '',
      initials,
      role: 'Admin',
      authMode: authModeLabel()
    };
  }

  function clearAdminSession() {
    try {
      if (window.RSAAdminAuth && typeof window.RSAAdminAuth.clearToken === 'function') {
        window.RSAAdminAuth.clearToken();
      }
      const localKeys = [];
      for (let index = 0; index < window.localStorage.length; index += 1) {
        const key = window.localStorage.key(index);
        if (key && /rsa_admin|CognitoIdentityServiceProvider|amplify/i.test(key)) localKeys.push(key);
      }
      localKeys.forEach(key => window.localStorage.removeItem(key));
      const sessionKeys = [];
      for (let index = 0; index < window.sessionStorage.length; index += 1) {
        const key = window.sessionStorage.key(index);
        if (key && /rsa_admin|CognitoIdentityServiceProvider|amplify/i.test(key)) sessionKeys.push(key);
      }
      sessionKeys.forEach(key => window.sessionStorage.removeItem(key));
    } catch (error) {
      // Continue to login even if storage cleanup is blocked.
    }
  }

  function logout() {
    clearAdminSession();
    window.location.href = './login.html?logged_out=1';
  }

  function normalizeStatus(value) {
    return String(value || '').trim().toLowerCase().replace(/[\s_]+/g, '-');
  }

  function itemStatus(item) {
    return normalizeStatus(item.status || item.booking_status || item.inquiry_status || item.lead_status || item.request_status || item.state);
  }

  function pick(item, keys, fallback) {
    for (const key of keys) {
      if (item && item[key] !== undefined && item[key] !== null && String(item[key]).trim() !== '') return item[key];
    }
    return fallback || '';
  }

  function getItems(payload) {
    if (window.RSAAdminApi && typeof window.RSAAdminApi.getItems === 'function') return window.RSAAdminApi.getItems(payload);
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== 'object') return [];
    return payload.items || payload.data || payload.results || [];
  }

  async function fetchActivity() {
    if (activityCache) return activityCache;
    const api = window.RSAAdminApi;
    if (!api || typeof api.request !== 'function') {
      activityCache = { bookings: [], inquiries: [], error: 'Data service unavailable.' };
      return activityCache;
    }

    const bookingPath = api.endpoints && api.endpoints.bookings ? api.endpoints.bookings : '/bookings';
    const inquiryPath = api.endpoints && api.endpoints.inquiries ? api.endpoints.inquiries : '/inquiries';
    const settled = await Promise.allSettled([api.request(bookingPath), api.request(inquiryPath)]);
    const bookings = settled[0].status === 'fulfilled' ? getItems(settled[0].value) : [];
    const inquiries = settled[1].status === 'fulfilled' ? getItems(settled[1].value) : [];
    const error = settled.some(result => result.status === 'rejected') ? 'Unable to refresh all activity.' : '';
    activityCache = { bookings, inquiries, error };
    return activityCache;
  }

  function actionableBookings(bookings) {
    return bookings.filter(item => ACTION_BOOKING_STATUSES.has(itemStatus(item)));
  }

  function actionableInquiries(inquiries) {
    return inquiries.filter(item => ACTION_INQUIRY_STATUSES.has(itemStatus(item)));
  }

  function itemTime(item) {
    const value = pick(item, ['created_at', 'updated_at', 'preferred_date', 'booking_date', 'date'], '');
    const time = Date.parse(value);
    return Number.isNaN(time) ? 0 : time;
  }

  function buildNotificationItems(bookings, inquiries) {
    const bookingItems = actionableBookings(bookings).map(item => ({
      type: 'booking',
      title: 'New booking request',
      name: pick(item, ['customer_name', 'full_name', 'name', 'contact_name'], 'Customer'),
      detail: pick(item, ['service_name', 'preferred_service', 'service', 'booking_type', 'message'], 'Booking request'),
      href: './bookings.html',
      time: itemTime(item)
    }));
    const inquiryItems = actionableInquiries(inquiries).map(item => ({
      type: 'inquiry',
      title: 'New inquiry',
      name: pick(item, ['customer_name', 'full_name', 'name', 'contact_name'], 'Customer'),
      detail: pick(item, ['subject', 'product_name', 'message', 'inquiry_type'], 'Customer message'),
      href: './inquiries.html',
      time: itemTime(item)
    }));
    return bookingItems.concat(inquiryItems).sort((a, b) => b.time - a.time).slice(0, 6);
  }

  function renderNotificationMenu(menu, activity) {
    const bookings = actionableBookings(activity.bookings);
    const inquiries = actionableInquiries(activity.inquiries);
    const items = buildNotificationItems(activity.bookings, activity.inquiries);
    const count = bookings.length + inquiries.length;
    const body = items.length ? items.map(item => `
      <a class="notification-item" href="${item.href}">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${escapeHtml(item.name)} - ${escapeHtml(item.detail)}</span>
        <em>View ${item.type}</em>
      </a>`).join('') : '<p class="notification-empty">No new bookings or inquiries.</p>';

    menu.innerHTML = `
      <div class="dropdown-title"><strong>Notifications</strong><span>${count} active</span></div>
      <div class="notification-list">${body}</div>
      <div class="notification-links"><a href="./bookings.html">View all bookings</a><a href="./inquiries.html">View all inquiries</a></div>`;
  }

  function updateBadge(button, count) {
    const badge = button.querySelector('[data-new-lead-count]');
    if (!badge) return;
    badge.textContent = String(count);
    badge.hidden = count <= 0;
    badge.classList.toggle('is-empty', count <= 0);
  }

  function setupNotifications() {
    const button = qs('.topbar-actions .icon-button[aria-label="Notifications"]');
    if (!button) return;
    button.classList.add('notification-button');
    if (!button.querySelector('i')) {
      button.innerHTML = '<i class="fa-solid fa-bell"></i><span data-new-lead-count>0</span>';
    }
    button.setAttribute('aria-haspopup', 'true');
    button.setAttribute('aria-expanded', 'false');

    let menu = qs('[data-admin-notification-menu]');
    if (!menu) {
      menu = document.createElement('div');
      menu.className = 'admin-dropdown admin-notification-menu';
      menu.dataset.adminNotificationMenu = 'true';
      menu.hidden = true;
      button.insertAdjacentElement('afterend', menu);
    }

    function setOpen(open) {
      menu.hidden = !open;
      button.classList.toggle('is-active', open);
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    button.addEventListener('click', event => {
      event.preventDefault();
      const opening = menu.hidden;
      closeDropdowns(menu);
      setOpen(opening);
    });

    fetchActivity().then(activity => {
      const count = actionableBookings(activity.bookings).length + actionableInquiries(activity.inquiries).length;
      updateBadge(button, count);
      renderNotificationMenu(menu, activity);
      updateSettingsFromActivity(activity);
    }).catch(() => {
      updateBadge(button, 0);
      menu.innerHTML = '<div class="dropdown-title"><strong>Notifications</strong></div><p class="notification-empty">Unable to load activity right now.</p><div class="notification-links"><a href="./bookings.html">View all bookings</a><a href="./inquiries.html">View all inquiries</a></div>';
      updateSettingsConnection(false);
    });
  }

  function setupUserMenu() {
    const card = qs('.topbar-actions .admin-avatar');
    if (!card) return;
    const identity = getIdentity();
    card.classList.add('admin-user-card');
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-haspopup', 'true');
    card.setAttribute('aria-expanded', 'false');
    const initials = card.querySelector(':scope > span');
    const strong = card.querySelector('strong');
    const small = card.querySelector('small');
    if (initials) initials.textContent = identity.initials;
    if (strong) strong.textContent = identity.name;
    if (small) small.textContent = identity.role;

    let menu = qs('[data-admin-user-menu]');
    if (!menu) {
      menu = document.createElement('div');
      menu.className = 'admin-dropdown admin-user-menu';
      menu.dataset.adminUserMenu = 'true';
      menu.hidden = true;
      card.insertAdjacentElement('afterend', menu);
    }
    menu.innerHTML = `
      <div class="dropdown-title"><strong>Signed in as</strong></div>
      <div class="user-menu-identity"><strong>${escapeHtml(identity.name)}</strong><span>${escapeHtml(identity.email || identity.username || identity.role)}</span></div>
      <a href="./settings.html"><i class="fa-solid fa-gear"></i> Settings</a>
      <button type="button" data-admin-logout><i class="fa-solid fa-right-from-bracket"></i> Logout</button>`;

    function toggle() {
      const opening = menu.hidden;
      closeDropdowns(menu);
      menu.hidden = !opening;
      card.classList.toggle('is-active', opening);
      card.setAttribute('aria-expanded', opening ? 'true' : 'false');
    }

    card.addEventListener('click', event => {
      event.preventDefault();
      toggle();
    });
    card.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        toggle();
      }
    });

    updateSettingsIdentity(identity);
  }

  function closeDropdowns(except) {
    qsa('.admin-dropdown').forEach(menu => {
      if (menu !== except) menu.hidden = true;
    });
    qsa('.notification-button, .admin-user-card').forEach(button => {
      const menu = button.nextElementSibling;
      if (!except || menu !== except) {
        button.classList.remove('is-active');
        button.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function updateSettingsIdentity(identity) {
    const name = qs('[data-settings-admin-name]');
    const email = qs('[data-settings-admin-email]');
    const mode = qs('[data-settings-auth-mode]');
    if (name) name.textContent = identity.name;
    if (email) email.textContent = identity.email || identity.username || 'Not available';
    if (mode) mode.textContent = identity.authMode;
  }

  function updateSettingsConnection(ok) {
    const status = qs('[data-settings-api-status]');
    if (status) status.textContent = ok ? 'Connected' : 'Unable to confirm connection';
  }

  function updateSettingsFromActivity(activity) {
    const count = actionableBookings(activity.bookings).length + actionableInquiries(activity.inquiries).length;
    const countEl = qs('[data-settings-notification-count]');
    if (countEl) countEl.textContent = String(count);
    updateSettingsConnection(!activity.error);
  }

  function setupGlobalClose() {
    document.addEventListener('click', event => {
      if (event.target.closest('.admin-dropdown, .notification-button, .admin-user-card')) return;
      closeDropdowns(null);
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeDropdowns(null);
    });
    document.addEventListener('click', event => {
      const logoutButton = event.target.closest('[data-admin-logout]');
      if (!logoutButton) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      logout();
    }, true);
  }

  function init() {
    setupNotifications();
    setupUserMenu();
    setupGlobalClose();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.RSAAdminHeaderUtilities55D = { init, getIdentity, fetchActivity };
}());
"""
    target.write_text(js, encoding="utf-8", newline="")
    print(f"[ok] Wrote {rel(target)}")


def append_css() -> None:
    path = ADMIN / "assets/css/admin.css"
    css = path.read_text(encoding="utf-8") if path.exists() else ""
    if PATCH_MARKER in css:
        return
    block = r"""

/* batch55d-admin-page-finalization */
.topbar-actions { position: relative; }
.notification-button,
.admin-user-card { cursor: pointer; }
.notification-button.is-active,
.admin-user-card.is-active { box-shadow: 0 0 0 3px rgba(185, 28, 28, 0.12); }
.notification-button [data-new-lead-count][hidden] { display: none !important; }
.admin-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: min(360px, calc(100vw - 32px));
  background: #fff;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 18px;
  box-shadow: 0 22px 48px rgba(15, 23, 42, 0.18);
  z-index: 40;
  padding: 14px;
}
.admin-notification-menu { right: 72px; }
.admin-dropdown[hidden] { display: none !important; }
.dropdown-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 2px 2px 10px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  margin-bottom: 8px;
}
.dropdown-title strong { color: #111827; font-size: 0.92rem; }
.dropdown-title span { color: #64748b; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
.notification-list { display: grid; gap: 8px; max-height: 320px; overflow: auto; }
.notification-item {
  display: grid;
  gap: 3px;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 12px;
  text-decoration: none;
  background: #fff;
}
.notification-item:hover { background: #fff7f7; border-color: rgba(185, 28, 28, 0.22); }
.notification-item strong { color: #111827; font-size: 0.9rem; }
.notification-item span { color: #475569; font-size: 0.82rem; line-height: 1.35; }
.notification-item em { color: #b91c1c; font-style: normal; font-weight: 800; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.07em; }
.notification-empty { margin: 10px 2px; color: #64748b; font-size: 0.9rem; }
.notification-links { display: flex; justify-content: space-between; gap: 10px; padding-top: 10px; margin-top: 8px; border-top: 1px solid rgba(148, 163, 184, 0.24); }
.notification-links a,
.admin-user-menu a,
.admin-user-menu button {
  color: #b91c1c;
  font-weight: 800;
  font-size: 0.82rem;
  text-decoration: none;
  background: transparent;
  border: 0;
  padding: 8px 4px;
  cursor: pointer;
}
.admin-user-menu { width: min(300px, calc(100vw - 32px)); }
.user-menu-identity { display: grid; gap: 3px; padding: 8px 2px 12px; }
.user-menu-identity strong { color: #111827; }
.user-menu-identity span { color: #64748b; font-size: 0.86rem; overflow-wrap: anywhere; }
.admin-user-menu a,
.admin-user-menu button { display: flex; align-items: center; gap: 9px; width: 100%; text-align: left; border-radius: 10px; }
.admin-user-menu a:hover,
.admin-user-menu button:hover { background: #fff7f7; }
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  align-items: stretch;
}
.settings-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 18px;
  background: #fff;
  min-width: 0;
}
.settings-card-wide { grid-column: 1 / -1; }
.settings-card-heading { display: flex; gap: 12px; align-items: center; }
.settings-card-heading > span {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #b91c1c;
  background: #fff1f2;
  flex: 0 0 auto;
}
.settings-card-heading h2 { margin: 0; color: #111827; font-size: 1.05rem; }
.settings-kv { display: grid; gap: 10px; margin: 0; }
.settings-kv div {
  display: grid;
  grid-template-columns: minmax(110px, 0.38fr) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  padding: 10px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
}
.settings-kv dt { color: #64748b; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.07em; }
.settings-kv dd { margin: 0; color: #111827; font-weight: 700; overflow-wrap: anywhere; }
.settings-note { color: #475569; line-height: 1.5; margin: 0; }
.settings-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: auto; }
@media (max-width: 900px) {
  .admin-notification-menu { right: 0; }
  .settings-grid { grid-template-columns: 1fr; }
  .settings-card-wide { grid-column: auto; }
}
@media (max-width: 640px) {
  .settings-kv div { grid-template-columns: 1fr; gap: 4px; }
  .notification-links { flex-direction: column; }
}
"""
    path.write_text(css.rstrip() + block + "\n", encoding="utf-8", newline="")
    print(f"[ok] Appended CSS to {rel(path)}")


def patch_polish_v3_settings_link() -> None:
    path = ADMIN / "assets/js/admin-polish-v3.js"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    original = text

    disabled_fragment = "<a class=\"nav-item is-disabled\" href=\"#\" aria-disabled=\"true\"><span class=\"nav-icon\"><i class=\"fa-solid fa-gear\"></i></span><span>Settings</span></a><button"
    enabled_fragment = "<a class=\"nav-item${active === 'settings' ? ' is-active' : ''}\" href=\"./settings.html\"><span class=\"nav-icon\"><i class=\"fa-solid fa-gear\"></i></span><span>Settings</span></a><button"
    text = text.replace(disabled_fragment, enabled_fragment)

    disabled_fragment_single = "<a class=\"nav-item is-disabled\" href=\"#\" aria-disabled=\"true\"><span class=\"nav-icon\"><i class=\"fa-solid fa-gear\"></i></span><span>Settings</span></a>"
    enabled_fragment_single = "<a class=\"nav-item${active === 'settings' ? ' is-active' : ''}\" href=\"./settings.html\"><span class=\"nav-icon\"><i class=\"fa-solid fa-gear\"></i></span><span>Settings</span></a>"
    text = text.replace(disabled_fragment_single, enabled_fragment_single)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        print(f"[ok] Updated {rel(path)}")


def assert_result() -> None:
    required = [
        ADMIN / "settings.html",
        ADMIN / "assets/js/admin-header-utilities-55d.js",
        ADMIN / "assets/css/admin.css",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"[fail] Missing expected file after patch: {rel(path)}")

    offenders: list[str] = []
    targets = list(ADMIN.glob("*.html")) + list((ADMIN / "assets/js").glob("*.js")) + list((ADMIN / "assets/css").glob("*.css"))
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for token in BAD_TOKENS:
            if token in text:
                offenders.append(f"{rel(path)} contains {token}")
    if offenders:
        raise SystemExit("[fail] Bad residue detected after patch:\n" + "\n".join(offenders))


def main() -> None:
    fail_if_bad_prestate()
    for path in sorted(ADMIN.glob("*.html")):
        patch_existing_admin_html(path)
    write_settings_html()
    write_header_utility_js()
    append_css()
    patch_polish_v3_settings_link()
    assert_result()
    print("[done] batch55d-admin-page-finalization applied.")
    print("[done] Added Settings page, notification dropdown, user dropdown, and logout/session utilities.")
    print("[done] No backend/API route, DynamoDB table, S3/media, email, SMS, or paid notification change.")


if __name__ == "__main__":
    main()
