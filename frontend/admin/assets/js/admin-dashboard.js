(function () {
  'use strict';

  const api = window.RSAAdminApi;
  const app = document.querySelector('[data-admin-app]');
  const statusBanner = document.querySelector('[data-status-banner]');

  function setStatus(type, title, message) {
    if (!statusBanner) return;
    statusBanner.classList.remove('is-success', 'is-warning');
    if (type) statusBanner.classList.add(type);
    statusBanner.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(message)}</span>`;
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function pick(...values) {
    return values.find((value) => value !== undefined && value !== null && value !== '') ?? '—';
  }

  function formatDate(value) {
    if (!value) return '—';
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value);
    return parsed.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: '2-digit' });
  }

  function statusClass(value) {
    const normalized = String(value || '').toLowerCase();
    if (normalized.includes('new')) return 'is-new';
    if (normalized.includes('schedule')) return 'is-scheduled';
    if (normalized.includes('confirm')) return 'is-confirmed';
    if (normalized.includes('reply')) return 'is-replied';
    if (normalized.includes('pending')) return 'is-pending';
    return '';
  }

  function initials(name) {
    return String(name || 'NA')
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0])
      .join('')
      .toUpperCase() || 'NA';
  }

  function setMetric(name, value) {
    const el = document.querySelector(`[data-metric="${name}"]`);
    if (el) el.textContent = value;
  }

  function setSnapshot(name, value) {
    const el = document.querySelector(`[data-snapshot="${name}"]`);
    if (el) el.textContent = value;
  }

  function renderBookings(bookings) {
    const tbody = document.querySelector('[data-bookings-table]');
    if (!tbody) return;

    const rows = bookings.slice(0, 6).map((booking) => {
      const id = pick(booking.booking_id, booking.id);
      const name = pick(booking.customer_name, booking.full_name, booking.name);
      const contact = pick(booking.contact_number, booking.phone_number, booking.mobile_number);
      const date = pick(booking.preferred_date, booking.schedule_date, booking.created_at);
      const status = pick(booking.status, 'New');

      return `
        <tr>
          <td><strong>${escapeHtml(id)}</strong></td>
          <td>${escapeHtml(name)}</td>
          <td>${escapeHtml(contact)}</td>
          <td>${escapeHtml(formatDate(date))}</td>
          <td><span class="status-pill ${statusClass(status)}">${escapeHtml(status)}</span></td>
        </tr>
      `;
    }).join('');

    tbody.innerHTML = rows || '<tr><td colspan="5" class="empty-cell">No bookings found.</td></tr>';
  }

  function renderInquiries(inquiries) {
    const container = document.querySelector('[data-inquiries-list]');
    if (!container) return;

    container.innerHTML = inquiries.slice(0, 5).map((inquiry) => {
      const name = pick(inquiry.customer_name, inquiry.name, 'Unknown Customer');
      const subject = pick(inquiry.subject, inquiry.service_interest, inquiry.product_name, 'General Inquiry');
      const status = pick(inquiry.status, 'New');
      return `
        <div class="lead-item">
          <span class="lead-avatar">${escapeHtml(initials(name))}</span>
          <div>
            <strong>${escapeHtml(name)}</strong>
            <small>${escapeHtml(subject)} · <span class="status-pill ${statusClass(status)}">${escapeHtml(status)}</span></small>
          </div>
        </div>
      `;
    }).join('') || '<p class="empty-state">No inquiries found.</p>';
  }

  function renderProducts(products) {
    const container = document.querySelector('[data-products-list]');
    if (!container) return;

    const interesting = products
      .filter((product) => product.sale_price || Number(product.stock_quantity || 0) <= Number(product.low_stock_threshold || 0))
      .slice(0, 5);

    container.innerHTML = interesting.map((product) => {
      const price = product.sale_price || product.price || '—';
      const stock = pick(product.stock_quantity, '—');
      return `
        <div class="product-item">
          <span class="product-thumb">${escapeHtml((product.category_key || 'P')[0].toUpperCase())}</span>
          <div>
            <strong>${escapeHtml(pick(product.product_name, product.name))}</strong>
            <small>Stock: ${escapeHtml(stock)} · Price: ₱${escapeHtml(price)}</small>
          </div>
        </div>
      `;
    }).join('') || '<p class="empty-state">No sale or low-stock products found.</p>';
  }

  function countByStatus(items, status) {
    const target = status.toLowerCase();
    return items.filter((item) => String(item.status || '').toLowerCase() === target).length;
  }

  async function loadDashboard() {
    if (!api) {
      setStatus('is-warning', 'Admin API client missing.', 'Make sure admin-api.js is loaded before admin-dashboard.js.');
      return;
    }

    setStatus('', 'Loading admin dashboard…', `Fetching data from ${api.getApiBaseUrl()}`);

    const settled = await Promise.allSettled([
      api.request(api.endpoints.products),
      api.request(api.endpoints.brands),
      api.request(api.endpoints.bookings),
      api.request(api.endpoints.inquiries),
      api.request(api.endpoints.customers),
      api.request(api.endpoints.pagesAbout),
      api.request(api.endpoints.pagesServices),
      api.request(api.endpoints.pagesContact)
    ]);

    const failures = settled.filter((result) => result.status === 'rejected');
    if (failures.length) {
      console.warn('Admin dashboard partial load failure:', failures);
    }

    const [productsPayload, brandsPayload, bookingsPayload, inquiriesPayload, customersPayload] = settled.map((result) => result.status === 'fulfilled' ? result.value : null);

    const products = api.getItems(productsPayload);
    const brands = api.getItems(brandsPayload);
    const bookings = api.getItems(bookingsPayload);
    const inquiries = api.getItems(inquiriesPayload);
    const customers = api.getItems(customersPayload);

    setMetric('products', api.getCount(productsPayload));
    setMetric('brands', api.getCount(brandsPayload));
    setMetric('bookings', api.getCount(bookingsPayload));
    setMetric('inquiries', api.getCount(inquiriesPayload));
    setMetric('customers', api.getCount(customersPayload));

    renderBookings(bookings);
    renderInquiries(inquiries);
    renderProducts(products);

    setSnapshot('newBookings', countByStatus(bookings, 'New'));
    setSnapshot('newInquiries', countByStatus(inquiries, 'New'));
    setSnapshot('repliedInquiries', countByStatus(inquiries, 'Replied'));

    const newLeadCount = document.querySelector('[data-new-lead-count]');
    if (newLeadCount) newLeadCount.textContent = countByStatus(bookings, 'New') + countByStatus(inquiries, 'New');

    if (failures.length) {
      setStatus('is-warning', 'Dashboard loaded with warnings.', 'Some API panels could not be loaded. Check backend logs and CORS settings.');
    } else {
      setStatus('is-success', 'Dashboard connected.', `Admin shell is reading API data from ${api.getApiBaseUrl()}.`);
    }
  }

  function setupShell() {
    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (toggle && app) {
      toggle.addEventListener('click', () => app.classList.toggle('sidebar-open'));
    }

    document.querySelectorAll('.nav-item.is-disabled, .quick-actions button').forEach((item) => {
      item.addEventListener('click', (event) => {
        event.preventDefault();
        setStatus('is-warning', 'Coming in a later admin batch.', 'Batch 17 is the dashboard shell only. Full admin CRUD will be added later.');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupShell();
    loadDashboard();
  });
}());
