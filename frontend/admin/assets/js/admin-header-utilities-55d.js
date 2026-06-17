(function () {
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

// batch59a-hotfix-v8-users-role-temp-password-reset
(function () {
  'use strict';

  const MARKER = 'batch59a-hotfix-v8-users-role-temp-password-reset';
  const ACCESS_TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';

  function decodeJwt(token) {
    try {
      const parts = String(token || '').split('.');
      if (parts.length < 2) return {};
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
      return JSON.parse(atob(padded));
    } catch (error) {
      return {};
    }
  }

  function claims() {
    const access = decodeJwt(window.localStorage.getItem(ACCESS_TOKEN_KEY));
    const id = decodeJwt(window.localStorage.getItem(ID_TOKEN_KEY));
    return { access, id };
  }

  function groupsFromClaims() {
    const c = claims();
    const groups = c.access['cognito:groups'] || c.id['cognito:groups'] || [];
    return Array.isArray(groups) ? groups : [];
  }

  function roleFromGroups() {
    const groups = groupsFromClaims();
    if (groups.includes('Admin')) return 'Admin';
    if (groups.includes('Standard')) return 'Standard';
    return 'No role';
  }

  function nameFromClaims() {
    const c = claims();
    const source = c.id && Object.keys(c.id).length ? c.id : c.access;
    const fullName = source.name || [source.given_name, source.family_name].filter(Boolean).join(' ');
    return String(fullName || source.email || source.username || source['cognito:username'] || 'Admin User').trim();
  }

  function initialsFromName(name) {
    const clean = String(name || '').trim();
    if (!clean) return 'AD';
    const parts = clean.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return clean.slice(0, 2).toUpperCase();
  }

  function hideSettingsForStandard(role) {
    const isAdmin = role === 'Admin';
    document.documentElement.classList.toggle('rsa-cognito-role-admin', isAdmin);
    document.documentElement.classList.toggle('rsa-cognito-role-standard', !isAdmin);
    if (isAdmin) return;
    document.querySelectorAll('a[href$="settings.html"], a[href*="/settings.html"], [data-nav-settings]').forEach((item) => {
      item.hidden = true;
      item.setAttribute('aria-hidden', 'true');
      item.style.display = 'none';
    });
  }

  function syncTopbarRole() {
    const role = roleFromGroups();
    const name = nameFromClaims();
    hideSettingsForStandard(role);

    document.querySelectorAll('.admin-avatar, .admin-user-card').forEach((card) => {
      const strong = card.querySelector('strong');
      const small = card.querySelector('small');
      const initials = card.querySelector('span, .avatar-initials');
      if (strong) strong.textContent = name;
      if (small) small.textContent = role;
      if (initials && initials.children.length === 0) initials.textContent = initialsFromName(name);
      card.setAttribute('data-cognito-role', role);
      card.setAttribute('title', `${name} · ${role}`);
    });

    document.querySelectorAll('[data-admin-role], [data-settings-admin-role]').forEach((el) => {
      el.textContent = role;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncTopbarRole);
  } else {
    syncTopbarRole();
  }
  [100, 350, 900, 1800].forEach((delay) => setTimeout(syncTopbarRole, delay));
  window.RSAHotfix59ATopbarRoleV8 = { marker: MARKER, syncTopbarRole, roleFromGroups };
}());

// batch59a-hotfix-v9-users-role-labels-reset-spacing
(function () {
  'use strict';

  const MARKER = 'batch59a-hotfix-v9-users-role-labels-reset-spacing';
  const ACCESS_TOKEN_KEY = 'rsa_admin_access_token';
  const ID_TOKEN_KEY = 'rsa_admin_id_token';

  function decodeJwt(token) {
    try {
      const parts = String(token || '').split('.');
      if (parts.length < 2) return {};
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
      return JSON.parse(atob(padded));
    } catch (error) {
      return {};
    }
  }

  function claims() {
    const access = decodeJwt(window.localStorage.getItem(ACCESS_TOKEN_KEY));
    const id = decodeJwt(window.localStorage.getItem(ID_TOKEN_KEY));
    return { access, id };
  }

  function groupsFromClaims() {
    const c = claims();
    const groups = c.access['cognito:groups'] || c.id['cognito:groups'] || [];
    return Array.isArray(groups) ? groups : [];
  }

  function rawRoleFromGroups() {
    const groups = groupsFromClaims();
    if (groups.includes('Admin')) return 'Admin';
    if (groups.includes('Standard')) return 'Standard';
    return 'No role';
  }

  function roleLabel(role) {
    if (role === 'Admin') return 'System Administrator';
    if (role === 'Standard') return 'Standard User';
    return role || 'No role';
  }

  function nameFromClaims() {
    const c = claims();
    const source = c.id && Object.keys(c.id).length ? c.id : c.access;
    const fullName = source.name || [source.given_name, source.family_name].filter(Boolean).join(' ');
    return String(fullName || source.email || source.username || source['cognito:username'] || 'Admin User').trim();
  }

  function initialsFromName(name) {
    const clean = String(name || '').trim();
    if (!clean) return 'AD';
    const parts = clean.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return clean.slice(0, 2).toUpperCase();
  }

  function hideSettingsForStandard(rawRole) {
    const isAdmin = rawRole === 'Admin';
    document.documentElement.classList.toggle('rsa-cognito-role-admin', isAdmin);
    document.documentElement.classList.toggle('rsa-cognito-role-standard', !isAdmin);
    if (isAdmin) return;
    document.querySelectorAll('a[href$="settings.html"], a[href*="/settings.html"], [data-nav-settings]').forEach((item) => {
      item.hidden = true;
      item.setAttribute('aria-hidden', 'true');
      item.style.display = 'none';
    });
  }

  function syncTopbarRole() {
    const rawRole = rawRoleFromGroups();
    const displayRole = roleLabel(rawRole);
    const name = nameFromClaims();
    hideSettingsForStandard(rawRole);

    document.querySelectorAll('.admin-avatar, .admin-user-card').forEach((card) => {
      const strong = card.querySelector('strong');
      const small = card.querySelector('small');
      const initials = card.querySelector('span, .avatar-initials');
      if (strong) strong.textContent = name;
      if (small) small.textContent = displayRole;
      if (initials && initials.children.length === 0) initials.textContent = initialsFromName(name);
      card.setAttribute('data-cognito-role', rawRole);
      card.setAttribute('title', `${name} · ${displayRole}`);
    });

    document.querySelectorAll('[data-admin-role], [data-settings-admin-role]').forEach((el) => {
      el.textContent = displayRole;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', syncTopbarRole);
  } else {
    syncTopbarRole();
  }
  [50, 150, 350, 900, 1800].forEach((delay) => setTimeout(syncTopbarRole, delay));
  window.RSAHotfix59ATopbarRoleV9 = { marker: MARKER, syncTopbarRole, rawRoleFromGroups, roleLabel };
}());
