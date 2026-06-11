(function () {
  'use strict';

  const api = window.RSAAdminApi;
  const app = document.querySelector('[data-admin-app]');
  const page = app ? app.getAttribute('data-admin-page') : '';
  const state = { records: [], filtered: [], categories: [], brands: [] };

  const configs = {
    products: {
      endpoint: '/admin/products?per_page=500',
      publicEndpoint: '/products?per_page=200',
      writeEndpoint: '/admin/products',
      idField: 'product_id',
      title: 'Products',
      singular: 'Product',
      kicker: 'Product Catalog',
      columns: [['product_id', 'Product ID'], ['product_name', 'Product'], ['category_name', 'Category'], ['product_brand_name', 'Brand'], ['price', 'Price'], ['sale_price', 'Sale Price'], ['show_flag', 'Visible'], ['show_pack_flag', 'Package'], ['stock_quantity', 'Stock']],
      detailFields: ['product_id', 'product_name', 'product_model', 'product_slug', 'category_id', 'category_key', 'category_name', 'category_prefix', 'subcategory', 'brand_id', 'product_brand_key', 'product_brand_name', 'description', 'price', 'sale_price', 'stock_quantity', 'low_stock_threshold', 'show_flag', 'show_pack_flag', 'image_path', 'feature_01', 'feature_02', 'feature_03', 'feature_04', 'feature_05', 'feature_06', 'feature_07', 'feature_08', 'feature_09', 'feature_10', 'created_at', 'updated_at']
    },
    categories: {
      endpoint: '/admin/categories',
      publicEndpoint: '/categories',
      writeEndpoint: '/admin/categories',
      idField: 'category_id',
      title: 'Categories',
      singular: 'Category',
      kicker: 'Category Setup',
      columns: [['category_id', 'Category ID'], ['category_name', 'Name'], ['category_key', 'Key'], ['category_prefix', 'Prefix'], ['icon_code', 'Icon'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible']],
      detailFields: ['category_id', 'category_name', 'category_key', 'category_prefix', 'icon_code', 'description', 'display_seq', 'show_flag', 'created_at', 'updated_at']
    },
    brands: {
      endpoint: '/admin/brands',
      publicEndpoint: '/brands',
      writeEndpoint: '/admin/brands',
      idField: 'brand_id',
      title: 'Brands',
      singular: 'Brand',
      kicker: 'Brand Setup',
      columns: [['brand_id', 'Brand ID'], ['brand_name', 'Brand'], ['brand_key', 'Key'], ['brand_logo_path', 'Logo Path'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible']],
      detailFields: ['brand_id', 'brand_name', 'brand_key', 'brand_logo_path', 'description', 'display_seq', 'show_flag', 'created_at', 'updated_at']
    },
    'key-features': {
      endpoint: '/admin/key-features',
      publicEndpoint: '/key-features',
      writeEndpoint: '/admin/key-features',
      idField: 'key_feat_id',
      title: 'Key Features',
      singular: 'Key Feature',
      kicker: 'Feature Suggestions',
      columns: [['key_feat_id', 'Feature ID'], ['key_feat_name', 'Feature Name'], ['created_at', 'Created At'], ['updated_at', 'Updated At']],
      detailFields: ['key_feat_id', 'key_feat_name', 'created_at', 'updated_at', 'created_by', 'updated_by']
    }
  };

  const config = configs[page];

  function esc(value) {
    return String(value ?? '').replace(/[&<>\"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
  }

  function label(value) { return value === null || value === undefined || value === '' ? '—' : String(value); }
  function money(value) { const n = Number(value); return value === null || value === undefined || value === '' ? '—' : Number.isFinite(n) ? `₱${n.toLocaleString('en-PH')}` : String(value); }
  function fmt(field, value) { return field === 'price' || field === 'sale_price' ? money(value) : label(value); }
  function flag(value, pack) { const yes = value === 'Y'; return `<span class="flag-pill ${yes ? (pack ? 'is-pack' : 'is-y') : 'is-n'}">${yes ? (pack ? 'Package' : 'Visible') : 'No'}</span>`; }

  function setStatus(type, title, message) {
    const banner = document.querySelector('[data-status-banner]');
    if (!banner) return;
    banner.className = 'status-banner';
    if (type) banner.classList.add(type);
    banner.innerHTML = `<strong>${esc(title)}</strong><span>${esc(message)}</span>`;
  }

  function text(record) { return Object.values(record || {}).map(value => String(value ?? '')).join(' ').toLowerCase(); }
  function searchValue() { return String(document.querySelector('[data-catalog-search]')?.value || document.querySelector('[data-admin-search]')?.value || '').trim().toLowerCase(); }

  function applyFilters() {
    const query = searchValue();
    const category = document.querySelector('[data-category-filter]')?.value || '';
    const brand = document.querySelector('[data-brand-filter]')?.value || '';
    const visibility = document.querySelector('[data-flag-filter]')?.value || '';
    state.filtered = state.records.filter(record =>
      (!query || text(record).includes(query)) &&
      (!category || record.category_key === category) &&
      (!brand || record.product_brand_key === brand || record.brand_key === brand) &&
      (!visibility || record.show_flag === visibility)
    );
    renderTable();
  }

  function setCount(message) { const el = document.querySelector('[data-record-count]'); if (el) el.textContent = message; }

  function renderHead() {
    const head = document.querySelector('[data-table-head]');
    if (!head) return;
    head.innerHTML = `<tr>${config.columns.map(([, labelText]) => `<th>${esc(labelText)}</th>`).join('')}<th>Action</th></tr>`;
  }

  function renderTable() {
    const body = document.querySelector('[data-table-body]');
    if (!body) return;
    setCount(`${state.filtered.length} of ${state.records.length} records`);
    if (!state.filtered.length) {
      body.innerHTML = `<tr><td colspan="${config.columns.length + 1}" class="empty-cell">No matching records found.</td></tr>`;
      return;
    }
    body.innerHTML = state.filtered.map((record, index) => {
      const cells = config.columns.map(([field]) => {
        if (field === 'show_flag') return `<td>${flag(record[field], false)}</td>`;
        if (field === 'show_pack_flag') return `<td>${flag(record[field], true)}</td>`;
        const value = fmt(field, record[field]);
        if (field === 'price') return `<td><span class="money">${esc(value)}</span></td>`;
        if (field === 'sale_price') return `<td><span class="sale-money">${esc(value)}</span></td>`;
        if (field.endsWith('_id')) return `<td><strong>${esc(value)}</strong></td>`;
        return `<td>${esc(value)}</td>`;
      }).join('');
      return `<tr data-row-index="${index}">${cells}<td><button class="table-action-link" type="button" data-view-index="${index}">View / Edit</button></td></tr>`;
    }).join('');
  }

  function detailRows(record) {
    return config.detailFields.map(field => `<div class="detail-row"><span>${esc(field.replace(/_/g, ' '))}</span><span>${esc(fmt(field, record[field]))}</span></div>`).join('');
  }

  function optionList(items, valueField, labelField, current) {
    return items.map(item => `<option value="${esc(item[valueField] || '')}" ${String(item[valueField] || '') === String(current || '') ? 'selected' : ''}>${esc(item[labelField] || item[valueField] || '')}</option>`).join('');
  }

  function input(name, labelText, value = '', type = 'text', attrs = '') {
    return `<label><span>${esc(labelText)}</span><input name="${esc(name)}" type="${esc(type)}" value="${esc(value ?? '')}" ${attrs} /></label>`;
  }

  function select(name, labelText, value, options) {
    return `<label><span>${esc(labelText)}</span><select name="${esc(name)}">${options.map(opt => `<option value="${esc(opt.value)}" ${String(opt.value) === String(value ?? '') ? 'selected' : ''}>${esc(opt.label)}</option>`).join('')}</select></label>`;
  }

  function productForm(record) {
    const isCreate = !record.product_id;
    const features = Array.from({ length: 10 }, (_, index) => {
      const n = String(index + 1).padStart(2, '0');
      return input(`feature_${n}`, `Feature ${n}`, record[`feature_${n}`] || '');
    }).join('');
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <h3>${isCreate ? 'Add Product' : 'Edit Product'}</h3>
      <p class="form-note">Batch 20 enables safe create/update. Delete and image upload are still disabled.</p>
      <div class="catalog-form-grid">
        ${input('product_name', 'Product Name', record.product_name || '')}
        ${input('product_id', 'Product ID', record.product_id || 'Auto-generated on save', 'text', 'readonly')}
        <label><span>Category</span><select name="category_key" required><option value="">Select category</option>${optionList(state.categories, 'category_key', 'category_name', record.category_key)}</select></label>
        <label><span>Brand</span><select name="product_brand_key"><option value="">No brand / generic</option>${optionList(state.brands, 'brand_key', 'brand_name', record.product_brand_key)}</select></label>
        ${input('subcategory', 'Subcategory', record.subcategory || '')}
        ${input('product_model', 'Model', record.product_model || '')}
        ${input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number')}
        ${input('stock_quantity', 'Stock Quantity', record.stock_quantity ?? 0, 'number')}
        ${input('low_stock_threshold', 'Low Stock Threshold', record.low_stock_threshold ?? 10, 'number')}
        ${input('price', 'Price', record.price ?? '', 'number', 'step="0.01" required')}
        ${input('sale_price', 'Sale Price', record.sale_price ?? '', 'number', 'step="0.01"')}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }])}
        ${select('show_pack_flag', 'Package Placement', record.show_pack_flag || 'N', [{ value: 'N', label: 'N - Normal' }, { value: 'Y', label: 'Y - Package hero' }])}
        ${input('image_path', 'Image Path', record.image_path || '')}
        <label class="span-2"><span>Description</span><textarea name="description" rows="4">${esc(record.description || '')}</textarea></label>
      </div>
      <h3>Product Features</h3><div class="feature-grid">${features}</div>
      <div class="drawer-actions"><button class="admin-button" type="submit">${isCreate ? 'Create Product' : 'Save Product'}</button><button class="admin-button secondary" type="button" data-close-drawer>Close</button></div>`;
  }

  function simpleForm(record) {
    const isCreate = !record[config.idField];
    const id = record[config.idField] || 'Auto-generated on save';
    const nameField = page === 'brands' ? 'brand_name' : page === 'categories' ? 'category_name' : 'key_feat_name';
    const keyField = page === 'brands' ? 'brand_key' : page === 'categories' ? 'category_key' : '';
    const prefix = page === 'categories' ? input('category_prefix', 'Prefix', record.category_prefix || '', 'text', 'maxlength="4" required') : '';
    const logo = page === 'brands' ? input('brand_logo_path', 'Logo Path', record.brand_logo_path || '') : '';
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <h3>${isCreate ? 'Add' : 'Edit'} ${config.singular}</h3>
      <p class="form-note">Batch 20 enables safe create/update. Delete actions remain disabled.</p>
      <div class="catalog-form-grid">
        ${input(config.idField, 'ID', id, 'text', 'readonly')}
        ${input(nameField, 'Name', record[nameField] || '', 'text', 'required')}
        ${keyField ? input(keyField, 'Key', record[keyField] || '') : ''}
        ${prefix}
        ${logo}
        ${page !== 'key-features' ? input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number') : ''}
        ${page !== 'key-features' ? select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }]) : ''}
        ${page !== 'key-features' ? `<label class="span-2"><span>Description</span><textarea name="description" rows="4">${esc(record.description || '')}</textarea></label>` : ''}
      </div>
      <div class="drawer-actions"><button class="admin-button" type="submit">${isCreate ? `Create ${config.singular}` : 'Save Changes'}</button><button class="admin-button secondary" type="button" data-close-drawer>Close</button></div>`;
  }

  function openDrawer(record = {}, mode = 'view') {
    const drawer = document.querySelector('[data-detail-drawer]');
    const title = document.querySelector('[data-drawer-title]');
    const kicker = document.querySelector('[data-drawer-kicker]');
    const body = document.querySelector('[data-drawer-body]');
    const form = document.querySelector('[data-catalog-form]');
    if (!drawer || !title || !body || !form) return;
    title.textContent = mode === 'create' ? `Add ${config.singular}` : (record[config.idField] || 'Catalog Detail');
    if (kicker) kicker.textContent = config.kicker;
    body.innerHTML = mode === 'create' ? '<p class="helper-text">Create a new catalog record. Required fields are marked by browser validation.</p>' : `<div class="detail-grid">${detailRows(record)}</div>`;
    form.hidden = false;
    form.dataset.recordId = record[config.idField] || '';
    form.innerHTML = page === 'products' ? productForm(record) : simpleForm(record);
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
  }

  function closeDrawer() {
    const drawer = document.querySelector('[data-detail-drawer]');
    if (drawer) {
      drawer.classList.remove('is-open');
      drawer.setAttribute('aria-hidden', 'true');
    }
  }

  function convertValue(key, value) {
    if (value === '') return null;
    if (['display_seq', 'stock_quantity', 'low_stock_threshold'].includes(key)) return Number.parseInt(value, 10) || 0;
    if (['price', 'sale_price'].includes(key)) return value === null ? null : Number(value);
    return value;
  }

  function collectFormPayload(form) {
    const formData = new FormData(form);
    const payload = {};
    for (const [key, rawValue] of formData.entries()) {
      if (key.startsWith('_') || key.endsWith('_id')) continue;
      const value = convertValue(key, String(rawValue).trim());
      if (value !== null || ['sale_price', 'description', 'brand_logo_path', 'product_brand_key'].includes(key)) {
        payload[key] = value;
      }
    }
    payload.updated_by = 'local-admin';
    return payload;
  }

  async function saveCatalogRecord(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    const recordId = form.dataset.recordId;
    const payload = collectFormPayload(form);
    const path = mode === 'create' ? config.writeEndpoint : `${config.writeEndpoint}/${encodeURIComponent(recordId)}`;
    const save = mode === 'create' ? api.postJson : api.putJson;

    try {
      setStatus('', 'Saving catalog record…', `${mode === 'create' ? 'Creating' : 'Updating'} ${config.singular.toLowerCase()}.`);
      const saved = await save(path, payload);
      setStatus('is-success', `${config.singular} saved.`, `${saved[config.idField] || 'Record'} was saved successfully.`);
      await loadRecords();
      const refreshed = state.records.find(record => record[config.idField] === saved[config.idField]) || saved;
      openDrawer(refreshed, 'view');
    } catch (error) {
      console.error(error);
      setStatus('is-warning', `Unable to save ${config.singular.toLowerCase()}.`, error.message || 'Check backend validation details.');
    }
  }

  function populateFilters() {
    const categoryFilter = document.querySelector('[data-category-filter]');
    if (categoryFilter) categoryFilter.innerHTML = '<option value="">All categories</option>' + state.categories.map(category => `<option value="${esc(category.category_key)}">${esc(category.category_name || category.category_key)}</option>`).join('');
    const brandFilter = document.querySelector('[data-brand-filter]');
    if (brandFilter) brandFilter.innerHTML = '<option value="">All brands</option>' + state.brands.map(brand => `<option value="${esc(brand.brand_key)}">${esc(brand.brand_name || brand.brand_key)}</option>`).join('');
  }

  async function preloadLookups() {
    const [categories, brands] = await Promise.all([
      api.request('/admin/categories').catch(() => api.request('/categories').catch(() => ({ items: [] }))),
      api.request('/admin/brands').catch(() => api.request('/brands').catch(() => ({ items: [] })))
    ]);
    state.categories = api.getItems(categories);
    state.brands = api.getItems(brands);
    populateFilters();
  }

  async function loadRecords() {
    if (!api || !config) {
      setStatus('is-warning', 'Catalog page could not start.', 'Missing admin API client or page configuration.');
      return;
    }
    setStatus('', `Loading ${config.title.toLowerCase()}…`, `Fetching from ${api.getApiBaseUrl()}${config.endpoint}.`);
    try {
      await preloadLookups();
      let payload;
      try { payload = await api.request(config.endpoint); }
      catch (adminError) { payload = await api.request(config.publicEndpoint); }
      state.records = api.getItems(payload);
      state.filtered = state.records.slice();
      renderHead();
      applyFilters();
      setStatus('is-success', `${config.title} loaded.`, `${state.records.length} records loaded from the backend API.`);
    } catch (error) {
      console.error(error);
      state.records = [];
      state.filtered = [];
      renderHead();
      renderTable();
      setStatus('is-warning', `Unable to load ${config.title.toLowerCase()}.`, error.message || 'Check backend server and CORS settings.');
    }
  }

  function setup() {
    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (toggle && app) toggle.addEventListener('click', () => app.classList.toggle('sidebar-open'));
    ['[data-catalog-search]', '[data-admin-search]', '[data-category-filter]', '[data-brand-filter]', '[data-flag-filter]'].forEach(selector => {
      const element = document.querySelector(selector);
      if (element) element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters);
    });
    document.querySelector('[data-clear-filters]')?.addEventListener('click', () => {
      document.querySelectorAll('[data-catalog-search],[data-admin-search]').forEach(element => { element.value = ''; });
      document.querySelectorAll('[data-category-filter],[data-brand-filter],[data-flag-filter]').forEach(element => { element.value = ''; });
      applyFilters();
    });
    document.querySelector('[data-refresh-list]')?.addEventListener('click', loadRecords);
    document.querySelector('[data-open-create]')?.addEventListener('click', () => openDrawer({}, 'create'));
    document.querySelector('[data-catalog-form]')?.addEventListener('submit', saveCatalogRecord);
    document.addEventListener('click', event => {
      const view = event.target.closest('[data-view-index]');
      const row = event.target.closest('[data-row-index]');
      const index = view ? view.getAttribute('data-view-index') : row ? row.getAttribute('data-row-index') : null;
      if (index !== null) {
        const record = state.filtered[Number(index)];
        if (record) openDrawer(record, 'view');
      }
      if (event.target.closest('[data-close-drawer]')) closeDrawer();
      const disabled = event.target.closest('.nav-item.is-disabled');
      if (disabled) {
        event.preventDefault();
        setStatus('is-warning', 'Coming in a later admin batch.', 'This admin module is not active yet.');
      }
    });
    document.addEventListener('keydown', event => { if (event.key === 'Escape') closeDrawer(); });
  }

  document.addEventListener('DOMContentLoaded', () => { setup(); loadRecords(); });
}());
