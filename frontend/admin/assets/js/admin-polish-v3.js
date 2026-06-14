(function () {
  'use strict';

  const VERSION = 'batch55c-hotfix-v3-admin-polish-final-sweep';
  window.RSA_BATCH55C_HOTFIX_V3_VERSION = VERSION;

  const NAV_SPEC = [
    { type: 'link', key: 'index', label: 'Dashboard', href: './index.html', icon: 'fa-solid fa-chart-column' },
    { type: 'heading', label: 'Catalog' },
    { type: 'link', key: 'products', label: 'Products', href: './products.html', icon: 'fa-solid fa-box-open' },
    { type: 'link', key: 'categories', label: 'Categories', href: './categories.html', icon: 'fa-solid fa-table-list' },
    { type: 'link', key: 'brands', label: 'Brands', href: './brands.html', icon: 'fa-solid fa-certificate' },
    { type: 'link', key: 'key-features', label: 'Key Features', href: './key-features.html', icon: 'fa-solid fa-star' },
    { type: 'heading', label: 'CRM' },
    { type: 'link', key: 'customers', label: 'Customers', href: './customers.html', icon: 'fa-solid fa-users' },
    { type: 'link', key: 'bookings', label: 'Bookings', href: './bookings.html', icon: 'fa-solid fa-calendar-check' },
    { type: 'link', key: 'inquiries', label: 'Inquiries', href: './inquiries.html', icon: 'fa-solid fa-file-circle-question' },
    { type: 'heading', label: 'CMS' },
    { type: 'link', key: 'about', label: 'About Us', href: './about.html', icon: 'fa-solid fa-address-card' },
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
    }).join('') + `<a class="nav-item${active === 'settings' ? ' is-active' : ''}" href="./settings.html"><span class="nav-icon"><i class="fa-solid fa-gear"></i></span><span>Settings</span></a><button class="nav-item nav-item-button" type="button" data-admin-logout><span class="nav-icon"><i class="fa-solid fa-right-from-bracket"></i></span><span>Logout</span></button>`;
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
