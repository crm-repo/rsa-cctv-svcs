(function () {
  'use strict';

  const BATCH55C_HOTFIX_V2_VERSION = 'batch55c-hotfix-v2-admin-polish-corrections';
  window.RSA_BATCH55C_HOTFIX_V2_VERSION = BATCH55C_HOTFIX_V2_VERSION;

  const BATCH55C_HOTFIX_VERSION = 'batch55c-hotfixes-admin-polish-corrections';
  window.RSA_BATCH55C_HOTFIX_VERSION = BATCH55C_HOTFIX_VERSION;

  const BATCH55C_ADMIN_POLISH_VERSION = 'batch55c-admin-page-overall-polish';
  window.RSA_BATCH55C_ADMIN_POLISH_VERSION = BATCH55C_ADMIN_POLISH_VERSION;

  const BATCH55B_PROTECTION_VERSION = 'batch55b-admin-category-subcategory-brand-protection-ui-table-editor';
  window.RSA_BATCH55B_PROTECTION_VERSION = BATCH55B_PROTECTION_VERSION;

  const api = window.RSAAdminApi;
  const app = document.querySelector('[data-admin-app]');
  const page = app ? app.getAttribute('data-admin-page') : '';
  const state = { records: [], filtered: [], categories: [], brands: [], keyFeatures: [] };

  const configs = {
    products: {
      endpoint: '/admin/products?per_page=500',
      publicEndpoint: '/products?per_page=200',
      writeEndpoint: '/admin/products',
      idField: 'product_id',
      title: 'Products',
      singular: 'Product',
      kicker: 'Product Catalog',
      columns: [['product_id', 'Product ID'], ['product_name', 'Product'], ['category_name', 'Category'], ['product_brand_name', 'Brand'], ['price', 'Price'], ['sale_price', 'Sale Price'], ['show_flag', 'Visible'], ['show_pack_flag', 'Promote Package'], ['stock_quantity', 'Stock']],
      detailFields: ['product_id', 'product_name', 'product_model', 'product_slug', 'category_id', 'category_key', 'category_name', 'category_prefix', 'subcategory_key', 'subcategory', 'brand_id', 'product_brand_key', 'product_brand_name', 'description', 'price', 'sale_price', 'stock_quantity', 'low_stock_threshold', 'show_flag', 'show_pack_flag', 'image_path', 'feature_01', 'feature_02', 'feature_03', 'feature_04', 'feature_05', 'feature_06', 'feature_07', 'feature_08', 'feature_09', 'feature_10', 'created_at', 'updated_at']
    },
    categories: {
      endpoint: '/admin/categories',
      publicEndpoint: '/categories',
      writeEndpoint: '/admin/categories',
      idField: 'category_id',
      title: 'Categories',
      singular: 'Category',
      kicker: 'Category Setup',
      columns: [['category_id', 'Category ID'], ['category_name', 'Name'], ['category_key', 'Key'], ['category_prefix', 'Prefix'], ['icon_code', 'Icon'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible'], ['subcategories', 'Subcategories']],
      detailFields: ['category_id', 'category_name', 'category_key', 'category_prefix', 'icon_code', 'description', 'display_seq', 'show_flag', 'subcategories', 'created_at', 'updated_at']
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
  function fmt(field, value) {
    if (field === 'price' || field === 'sale_price') return money(value);
    if (field === 'subcategories') return Array.isArray(value) ? `${value.length} subcategories` : label(value);
    return label(value);
  }

  function slugify(value) {
    return String(value || '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'item';
  }

  function activeCategoriesForProduct(currentKey) {
    return state.categories.filter(category => category.show_flag === 'Y' || String(category.category_key || '') === String(currentKey || ''));
  }

  function activeBrandsForProduct(currentKey) {
    return state.brands.filter(brand => brand.show_flag === 'Y' || String(brand.brand_key || '') === String(currentKey || ''));
  }

  function getCategoryByKey(categoryKey) {
    return state.categories.find(item => String(item.category_key || '') === String(categoryKey || '')) || null;
  }

  function subcategoriesForCategory(categoryKey) {
    const category = getCategoryByKey(categoryKey);
    return category && Array.isArray(category.subcategories) ? category.subcategories.slice().sort((a, b) => Number(a.display_seq || 0) - Number(b.display_seq || 0)) : [];
  }

  function subcategoryLines(record) {
    const items = Array.isArray(record.subcategories) ? record.subcategories : [];
    return items
      .slice()
      .sort((a, b) => Number(a.display_seq || 0) - Number(b.display_seq || 0))
      .map(item => `${item.display_seq || 0} | ${item.subcategory_key || slugify(item.subcategory_name)} | ${item.subcategory_name || ''}`)
      .join('\n');
  }


  function sortedSubcategories(record) {
    const items = Array.isArray(record.subcategories) ? record.subcategories : [];
    return items.slice().sort((a, b) => Number(a.display_seq || 0) - Number(b.display_seq || 0));
  }

  function subcategoryEditorRow(item = {}, index = 0) {
    const displaySeq = item.display_seq ?? ((index + 1) * 10);
    const name = item.subcategory_name || item.name || '';
    const key = item.subcategory_key || slugify(name);
    return `<div class="subcategory-editor-row" data-subcategory-row>
      <input type="number" class="subcategory-editor-seq" value="${esc(displaySeq)}" min="0" step="1" data-subcategory-display-seq aria-label="Subcategory display sequence" />
      <input type="text" class="subcategory-editor-key is-readonly-field" value="${esc(key)}" placeholder="system-generated" data-subcategory-key aria-label="Subcategory key" readonly />
      <input type="text" class="subcategory-editor-name" value="${esc(name)}" placeholder="Subcategory name" data-subcategory-name aria-label="Subcategory name" />
      <button type="button" class="table-action-link subcategory-remove-button" data-remove-subcategory-row>Remove</button>
    </div>`;
  }

  function renderSubcategoryEditor(record) {
    const rows = sortedSubcategories(record).map((item, index) => subcategoryEditorRow(item, index)).join('');
    return `<div class="span-2 subcategory-admin-editor" data-subcategory-editor>
      <div class="subcategory-editor-topline">
        <div>
          <span class="subcategory-editor-title">Subcategories</span>
          <small>Edit each subcategory in its own row. Used subcategory removal is blocked by backend validation.</small>
        </div>
        <button type="button" class="admin-button secondary compact-action" data-add-subcategory-row>Add Subcategory</button>
      </div>
      <div class="subcategory-editor-table" role="table" aria-label="Category subcategories">
        <div class="subcategory-editor-row subcategory-editor-head" role="row">
          <span>Seq</span>
          <span>Subcategory Key</span>
          <span>Subcategory Name</span>
          <span>Action</span>
        </div>
        <div data-subcategory-rows>${rows}</div>
      </div>
      <p class="form-note compact-note">Subcategory keys are system-generated from the name and are read-only. Do not remove a subcategory that is already used by products.</p>
    </div>`;
  }

  function nextSubcategoryDisplaySeq(editor) {
    const values = Array.from(editor.querySelectorAll('[data-subcategory-display-seq]'))
      .map(input => Number.parseInt(input.value, 10))
      .filter(value => Number.isFinite(value));
    return values.length ? Math.max(...values) + 10 : 10;
  }

  function addSubcategoryEditorRow(editor, item = {}, focus = false) {
    const rows = editor.querySelector('[data-subcategory-rows]');
    if (!rows) return;
    const index = rows.querySelectorAll('[data-subcategory-row]').length;
    const data = { display_seq: item.display_seq ?? nextSubcategoryDisplaySeq(editor), ...item };
    rows.insertAdjacentHTML('beforeend', subcategoryEditorRow(data, index));
    if (focus) rows.querySelector('[data-subcategory-row]:last-child [data-subcategory-name]')?.focus();
  }

  function collectSubcategoriesFromEditor(form) {
    return Array.from(form.querySelectorAll('[data-subcategory-row]'))
      .map((row, index) => {
        const displaySeq = Number.parseInt(row.querySelector('[data-subcategory-display-seq]')?.value || '', 10) || ((index + 1) * 10);
        const name = String(row.querySelector('[data-subcategory-name]')?.value || '').trim();
        const keyInput = String(row.querySelector('[data-subcategory-key]')?.value || '').trim();
        const key = slugify(keyInput || name);
        if (!name && !keyInput) return null;
        return { display_seq: displaySeq, subcategory_key: key, subcategory_name: name || key };
      })
      .filter(Boolean)
      .sort((a, b) => Number(a.display_seq || 0) - Number(b.display_seq || 0));
  }

  function bindSubcategoryEditor(form) {
    const editor = form.querySelector('[data-subcategory-editor]');
    if (!editor || editor.dataset.boundSubcategoryEditor === 'true') return;
    editor.dataset.boundSubcategoryEditor = 'true';

    editor.addEventListener('click', event => {
      const target = event.target;
      if (!(target instanceof Element)) return;
      if (target.closest('[data-add-subcategory-row]')) {
        addSubcategoryEditorRow(editor, {}, true);
        return;
      }
      if (target.closest('[data-remove-subcategory-row]')) {
        const row = target.closest('[data-subcategory-row]');
        if (row) row.remove();
      }
    });

    editor.addEventListener('input', event => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) return;
      const row = target.closest('[data-subcategory-row]');
      if (!row) return;
      const keyInput = row.querySelector('[data-subcategory-key]');
      if (target.matches('[data-subcategory-name]') && keyInput && keyInput instanceof HTMLInputElement) {
        keyInput.value = slugify(target.value);
      }
    });
  }

  function parseSubcategoryLines(value) {
    return String(value || '')
      .split(/\r?\n/)
      .map(line => line.trim())
      .filter(Boolean)
      .map((line, index) => {
        const parts = line.split('|').map(part => part.trim());
        if (parts.length >= 3) {
          return { display_seq: Number.parseInt(parts[0], 10) || (index + 1) * 10, subcategory_key: slugify(parts[1]), subcategory_name: parts.slice(2).join(' | ') };
        }
        if (parts.length === 2) {
          return { display_seq: (index + 1) * 10, subcategory_key: slugify(parts[0]), subcategory_name: parts[1] };
        }
        return { display_seq: (index + 1) * 10, subcategory_key: slugify(parts[0]), subcategory_name: parts[0] };
      });
  }

  function subcategoryDetail(value) {
    if (!Array.isArray(value) || !value.length) return '—';
    return value
      .slice()
      .sort((a, b) => Number(a.display_seq || 0) - Number(b.display_seq || 0))
      .map(item => `${item.subcategory_name || item.subcategory_key} (${item.subcategory_key || ''})`)
      .join(', ');
  }
  function flag(value, pack) { const yes = value === 'Y'; return `<span class="flag-pill ${yes ? (pack ? 'is-pack' : 'is-y') : 'is-n'}">${pack ? (yes ? 'Yes' : 'No') : (yes ? 'Visible' : 'Hidden')}</span>`; }

  function setStatus(type, title, message) {
    const banner = document.querySelector('[data-status-banner]');
    if (!banner) return;
    banner.className = 'status-banner';
    if (type) banner.classList.add(type);
    banner.innerHTML = `<strong>${esc(title)}</strong><span>${esc(message)}</span>`;
  }

  function text(record) { return Object.values(record || {}).map(value => String(value ?? '')).join(' ').toLowerCase(); }
  function searchValue() { return String(document.querySelector('[data-catalog-search]')?.value || document.querySelector('[data-admin-search]')?.value || '').trim().toLowerCase(); }
  function sortValue() { return String(document.querySelector('[data-sort-filter]')?.value || 'recent'); }
  function recordDateValue(record) {
    const raw = record.created_at || record.updated_at || '';
    const parsed = Date.parse(raw);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  function displayName(record) {
    return String(record.product_name || record.category_name || record.brand_name || record.key_feat_name || record[config.idField] || '').toLowerCase();
  }
  function hasSalePrice(record) {
    const value = record ? record.sale_price : null;

    return (
      value !== null &&
      value !== undefined &&
      String(value).trim() !== ''
    );
  }
function sortRecords(records) {
  const mode = sortValue();

  return records.slice().sort((a, b) => {
    if (page === 'products' && mode === 'sale') {
      const saleComparison =
        Number(hasSalePrice(b)) - Number(hasSalePrice(a));

      if (saleComparison !== 0) {
        return saleComparison;
      }

      return recordDateValue(b) - recordDateValue(a);
    }

    if (mode === 'display_seq') {
      return Number(a.display_seq || 0) - Number(b.display_seq || 0);
    }

    if (mode === 'oldest') {
      return recordDateValue(a) - recordDateValue(b);
    }

    if (mode === 'az') {
      return displayName(a).localeCompare(displayName(b));
    }

    if (mode === 'za') {
      return displayName(b).localeCompare(displayName(a));
    }

    return recordDateValue(b) - recordDateValue(a);
  });
}

  function applyFilters() {
    const query = searchValue();
    const category = document.querySelector('[data-category-filter]')?.value || '';
    const brand = document.querySelector('[data-brand-filter]')?.value || '';
    state.filtered = sortRecords(state.records.filter(record =>
      (!query || text(record).includes(query)) &&
      (!category || record.category_key === category) &&
      (!brand || record.product_brand_key === brand || record.brand_key === brand)
    ));
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
    setCount(`${state.filtered.length} ${config.title} records found`);
    if (!state.filtered.length) {
      body.innerHTML = `<tr><td colspan="${config.columns.length + 1}" class="empty-cell">No matching catalog records found.</td></tr>`;
      return;
    }
    body.innerHTML = state.filtered.map((record, index) => {
      const cells = config.columns.map(([field]) => {
        if (field === 'show_flag') return `<td>${flag(record[field], false)}</td>`;
        if (field === 'show_pack_flag') return `<td>${flag(record[field], true)}</td>`;
        if (field === 'subcategories') return `<td>${esc(fmt(field, record[field]))}</td>`;
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
    return config.detailFields.map(field => {
      const value = field === 'subcategories' ? subcategoryDetail(record[field]) : fmt(field, record[field]);
      return `<div class="detail-row"><span>${esc(field.replace(/_/g, ' '))}</span><span>${esc(value)}</span></div>`;
    }).join('');
  }

  function optionList(items, valueField, labelField, current) {
    return items.map(item => `<option value="${esc(item[valueField] || '')}" ${String(item[valueField] || '') === String(current || '') ? 'selected' : ''}>${esc(item[labelField] || item[valueField] || '')}</option>`).join('');
  }

  function keyFeatureOptions() {
    return state.keyFeatures
      .map(item => item.key_feat_name || item.feature_name || item.name || '')
      .filter(Boolean)
      .map(name => `<option value="${esc(name)}"></option>`)
      .join('');
  }

  function getBrandNameFromKey(brandKey) {
    const brand = state.brands.find(item => String(item.brand_key || '') === String(brandKey || ''));
    return brand ? (brand.brand_name || brand.brand_key || '') : '';
  }

  function buildSuggestedProductName(form) {
    if (!form) return '';
    const brandKey = form.querySelector('[name="product_brand_key"]')?.value || '';
    const brandName = getBrandNameFromKey(brandKey);
    const featureOne = form.querySelector('[name="feature_01"]')?.value || '';
    const subcategory = form.querySelector('[name="subcategory"]')?.value || '';
    return [brandName, featureOne, subcategory].map(value => String(value || '').trim()).filter(Boolean).join(' ');
  }

  function updateProductNamePreview(form) {
    const preview = form.querySelector('[data-product-name-preview]');
    const productName = form.querySelector('[name="product_name"]');
    if (!preview || !productName) return;

    const suggested = buildSuggestedProductName(form);
    const previousSuggestion = productName.dataset.lastSuggestion || '';

    preview.textContent = suggested || 'Select a brand, Feature 01, and subcategory to preview the default product name.';

    if (!productName.dataset.manualEdit || productName.value.trim() === '' || productName.value.trim() === previousSuggestion) {
      if (suggested) {
        productName.value = suggested;
        productName.dataset.lastSuggestion = suggested;
        productName.dataset.manualEdit = '';
      }
    }
  }

  function enhanceProductForm(form) {
    if (!form || page !== 'products') return;

    const productName = form.querySelector('[name="product_name"]');
    const categorySelect = form.querySelector('[name="category_key"]');
    const brandSelect = form.querySelector('[name="product_brand_key"]');
    const featureOne = form.querySelector('[name="feature_01"]');
    const subcategoryKey = form.querySelector('[name="subcategory_key"]');
    const subcategoryName = form.querySelector('[name="subcategory"]');
    const showPackSelect = form.querySelector('[name="show_pack_flag"]');

    function renderSubcategories() {
      if (!categorySelect || !subcategoryKey) return;
      const current = subcategoryKey.value || subcategoryKey.dataset.currentValue || '';
      const items = subcategoriesForCategory(categorySelect.value);
      subcategoryKey.innerHTML = '<option value="">Select subcategory</option>' + items.map(item => `<option value="${esc(item.subcategory_key)}" ${String(item.subcategory_key || '') === String(current || '') ? 'selected' : ''}>${esc(item.subcategory_name || item.subcategory_key)}</option>`).join('');
      const selected = items.find(item => String(item.subcategory_key || '') === String(subcategoryKey.value || ''));
      if (subcategoryName) subcategoryName.value = selected ? (selected.subcategory_name || '') : '';
    }

    function updateShowPackAvailability() {
      if (!showPackSelect || !categorySelect) return;
      const isPackage = categorySelect.value === 'packages';
      if (!isPackage) showPackSelect.value = 'N';
      showPackSelect.disabled = !isPackage;
      showPackSelect.closest('label')?.classList.toggle('is-readonly-field', !isPackage);
      const note = form.querySelector('[data-show-pack-note]');
      if (note) note.textContent = isPackage ? 'Package products can be promoted on homepage/package highlights.' : 'Promote Package is available only for Packages/Kits.';
    }


    if (productName && !productName.dataset.boundNamePreview) {
      productName.dataset.boundNamePreview = 'true';
      productName.addEventListener('input', () => {
        const suggested = buildSuggestedProductName(form);
        productName.dataset.manualEdit = productName.value.trim() && productName.value.trim() !== suggested ? 'true' : '';
      });
    }

    if (categorySelect && !categorySelect.dataset.boundSubcategoryFilter) {
      categorySelect.dataset.boundSubcategoryFilter = 'true';
      categorySelect.addEventListener('change', () => {
        if (subcategoryKey) {
          subcategoryKey.dataset.currentValue = '';
          subcategoryKey.value = '';
        }
        renderSubcategories();
        updateShowPackAvailability();
        updateProductNamePreview(form);
      });
      renderSubcategories();
    }

    updateShowPackAvailability();

    if (subcategoryKey && !subcategoryKey.dataset.boundSubcategoryName) {
      subcategoryKey.dataset.boundSubcategoryName = 'true';
      subcategoryKey.addEventListener('change', () => {
        const items = subcategoriesForCategory(categorySelect ? categorySelect.value : '');
        const selected = items.find(item => String(item.subcategory_key || '') === String(subcategoryKey.value || ''));
        if (subcategoryName) subcategoryName.value = selected ? (selected.subcategory_name || '') : '';
        updateProductNamePreview(form);
      });
    }

    [brandSelect, featureOne, subcategoryKey].forEach(inputEl => {
      if (!inputEl || inputEl.dataset.boundNamePreview) return;
      inputEl.dataset.boundNamePreview = 'true';
      inputEl.addEventListener('input', () => updateProductNamePreview(form));
      inputEl.addEventListener('change', () => updateProductNamePreview(form));
    });

    updateProductNamePreview(form);
  }

  function requiredLabel(labelText, attrs = '') {
    return String(attrs || '').includes('required') ? `${labelText} <span class="required-star" aria-hidden="true">*</span>` : labelText;
  }

  function input(name, labelText, value = '', type = 'text', attrs = '') {
    const readonly = String(attrs || '').includes('readonly');
    const mediaNames = new Set(['image_path', 'brand_logo_path', 'hero_image_path', 'company_story_image_path', 'service_image_path', 'project_image_path', 'logo_path', 'icon_path', 'person_image_path']);
    const isMedia = mediaNames.has(String(name || '')) || String(name || '').endsWith('_image_path') || String(name || '').endsWith('_logo_path');
    const labelClasses = [readonly ? 'is-readonly-field' : '', isMedia ? 'media-field-label span-2' : ''].filter(Boolean).join(' ');
    const classAttr = labelClasses ? ` class="${labelClasses}"` : '';
    return `<label${classAttr}><span>${requiredLabel(esc(labelText), attrs)}</span><input class="${readonly ? 'is-readonly-field' : ''}" name="${esc(name)}" type="${esc(type)}" value="${esc(value ?? '')}" ${attrs} /></label>`;
  }

  function select(name, labelText, value, options, attrs = '') {
    return `<label><span>${requiredLabel(esc(labelText), attrs)}</span><select name="${esc(name)}" ${attrs}>${options.map(opt => `<option value="${esc(opt.value)}" ${String(opt.value) === String(value ?? '') ? 'selected' : ''}>${esc(opt.label)}</option>`).join('')}</select></label>`;
  }


  function bindSystemGeneratedKeys(form) {
    if (!form || form.dataset.boundSystemKeys === 'true') return;
    form.dataset.boundSystemKeys = 'true';
    const pairs = [
      ['brand_name', 'brand_key'],
      ['category_name', 'category_key'],
      ['key_feat_name', 'key_feat_key'],
      ['subcategory_name', 'subcategory_key']
    ];
    pairs.forEach(([nameField, keyField]) => {
      const source = form.querySelector(`[name="${nameField}"]`);
      const target = form.querySelector(`[name="${keyField}"]`);
      if (!source || !target) return;
      const sync = () => { target.value = slugify(source.value); };
      if (!target.value || form.querySelector('[name="_mode"]')?.value === 'create') sync();
      source.addEventListener('input', sync);
      source.addEventListener('change', sync);
    });
  }

  function productForm(record) {
    const isCreate = !record.product_id;
    const features = Array.from({ length: 10 }, (_, index) => {
      const n = String(index + 1).padStart(2, '0');
      const req = index < 3 ? 'required ' : '';
      return input(`feature_${n}`, `Feature ${n}`, record[`feature_${n}`] || '', 'text', `${req}list="key-feature-suggestions"`);
    }).join('');
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <p class="form-note">Manage product details, category, brand, features, visibility, and media. Product images use the safe media picker until real upload storage is enabled.</p>
      <div class="catalog-form-grid">
        <label class="span-2 product-name-preview-field"><span>Product Name <span class="required-star" aria-hidden="true">*</span></span><input name="product_name" type="text" value="${esc(record.product_name || '')}" required /><small>Default suggestion: <strong data-product-name-preview>Brand + Feature 01 + Subcategory</strong></small></label>
        ${input('product_id', 'Product ID', record.product_id || 'Auto-generated on save', 'text', 'readonly')}
        <label><span>Category <span class="required-star" aria-hidden="true">*</span></span><select name="category_key" required><option value="">Select category</option>${optionList(activeCategoriesForProduct(record.category_key), 'category_key', 'category_name', record.category_key)}</select></label>
        <label><span>Brand <span class="required-star" aria-hidden="true">*</span></span><select name="product_brand_key" required><option value="">Select brand</option>${optionList(activeBrandsForProduct(record.product_brand_key), 'brand_key', 'brand_name', record.product_brand_key)}</select></label>
        <label><span>Subcategory <span class="required-star" aria-hidden="true">*</span></span><select name="subcategory_key" data-current-value="${esc(record.subcategory_key || slugify(record.subcategory || ''))}" required><option value="">Select subcategory</option></select></label>
        <input name="subcategory" type="hidden" value="${esc(record.subcategory || '')}" />
        ${input('product_model', 'Model', record.product_model || '')}
        ${input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number')}
        ${input('stock_quantity', 'Stock Quantity', record.stock_quantity ?? 0, 'number', 'required')}
        ${input('low_stock_threshold', 'Low Stock Threshold', record.low_stock_threshold ?? 10, 'number', 'required')}
        ${input('price', 'Price', record.price ?? '', 'number', 'step="0.01"')}
        ${input('sale_price', 'Sale Price', record.sale_price ?? '', 'number', 'step="0.01"')}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }], 'required')}
        <label><span>Promote Package</span><select name="show_pack_flag"><option value="N" ${String(record.show_pack_flag || 'N') !== 'Y' ? 'selected' : ''}>No</option><option value="Y" ${String(record.show_pack_flag || 'N') === 'Y' ? 'selected' : ''}>Yes</option></select><small data-show-pack-note>Promote Package is available only for Packages/Kits.</small></label>
        ${input('image_path', 'Product Image', record.image_path || '')}
        <label class="span-2"><span>Description</span><textarea name="description" rows="4">${esc(record.description || '')}</textarea></label>
      </div>
      <h3>Product Features</h3><div class="feature-grid">${features}</div>
      <datalist id="key-feature-suggestions">${keyFeatureOptions()}</datalist>
      <p class="form-note compact-note">At least three product features are required. Suggestions are reusable, but custom text is allowed.</p>
      <div class="drawer-actions"><button class="admin-button" type="submit" data-save-button>${isCreate ? 'Create Product' : 'Save Product'}</button><button class="admin-button secondary" type="button" data-close-drawer>Close</button></div>`;
  }

  function simpleForm(record) {
    const isCreate = !record[config.idField];
    const id = record[config.idField] || 'Auto-generated on save';
    const nameField = page === 'brands' ? 'brand_name' : page === 'categories' ? 'category_name' : 'key_feat_name';
    const keyField = page === 'brands' ? 'brand_key' : page === 'categories' ? 'category_key' : '';
    const prefix = page === 'categories' ? input('category_prefix', 'Prefix', record.category_prefix || '', 'text', 'maxlength="4" required') : '';
    const iconCode = page === 'categories' ? input('icon_code', 'Icon Code', record.icon_code || '', 'text', 'placeholder="fa-solid fa-video" required') : '';
    const logo = page === 'brands' ? input('brand_logo_path', 'Brand Logo', record.brand_logo_path || '') : '';
    const subcategoryEditor = page === 'categories' ? renderSubcategoryEditor(record) : '';
    const formNote = page === 'categories'
      ? 'Manage category details and subcategories. Manage category details and subcategories.'
      : page === 'brands'
        ? 'Manage brand details and logo. Manage brand details and logo.'
        : 'Manage reusable product feature suggestions.';
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <p class="form-note">${formNote}</p>
      <div class="catalog-form-grid">
        ${input(config.idField, 'ID', id, 'text', 'readonly')}
        ${input(nameField, 'Name', record[nameField] || '', 'text', 'required')}
        ${keyField ? input(keyField, 'Key', record[keyField] || '', 'text', 'required readonly data-system-key="true"') : ''}
        ${prefix}
        ${iconCode}
        ${logo}
        ${page !== 'key-features' ? input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number') : ''}
        ${page !== 'key-features' ? select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }], 'required') : ''}
        ${page !== 'key-features' ? `<label class="span-2"><span>Description</span><textarea name="description" rows="4">${esc(record.description || '')}</textarea></label>` : ''}
        ${subcategoryEditor}
      </div>
      <div class="drawer-actions"><button class="admin-button" type="submit" data-save-button>${isCreate ? `Create ${config.singular}` : 'Save Changes'}</button><button class="admin-button secondary" type="button" data-close-drawer>Close</button></div>`;
  }

  function snapshotForm(form) {
    return JSON.stringify(collectFormPayload(form));
  }

  function setSaveDirtyState(form, changed = false) {
    const button = form.querySelector('[data-save-button]');
    if (!button) return;
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    button.disabled = mode !== 'create' && !changed;
  }

  function bindDirtyTracking(form) {
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    window.setTimeout(() => {
      form.dataset.initialPayload = snapshotForm(form);
      setSaveDirtyState(form, mode === 'create');
    }, 0);
    if (form.dataset.boundDirtyTracking === 'true') return;
    form.dataset.boundDirtyTracking = 'true';
    form.addEventListener('input', () => setSaveDirtyState(form, snapshotForm(form) !== form.dataset.initialPayload));
    form.addEventListener('change', () => setSaveDirtyState(form, snapshotForm(form) !== form.dataset.initialPayload));
    form.addEventListener('click', event => {
      if (event.target.closest('[data-add-subcategory-row]') || event.target.closest('[data-remove-subcategory-row]')) {
        window.setTimeout(() => setSaveDirtyState(form, snapshotForm(form) !== form.dataset.initialPayload), 0);
      }
    });
  }

  function openDrawer(record = {}, mode = 'view') {
    const drawer = document.querySelector('[data-detail-drawer]');
    const title = document.querySelector('[data-drawer-title]');
    const kicker = document.querySelector('[data-drawer-kicker]');
    const body = document.querySelector('[data-drawer-body]');
    const form = document.querySelector('[data-catalog-form]');
    if (!drawer || !title || !body || !form) return;
    title.textContent = mode === 'create' ? `Add ${config.singular}` : (record[config.idField] || `Edit ${config.singular}`);
    if (kicker) kicker.textContent = config.kicker;
    body.innerHTML = '';
    form.hidden = false;
    form.dataset.recordId = record[config.idField] || '';
    form.innerHTML = page === 'products' ? productForm(record) : simpleForm(record);
    enhanceProductForm(form);
    bindSubcategoryEditor(form);
    bindSystemGeneratedKeys(form);
    bindDirtyTracking(form);
    if (window.RSAAdminMedia && typeof window.RSAAdminMedia.enhanceAll === 'function') window.RSAAdminMedia.enhanceAll(form);
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
    if (page === 'categories' && form.querySelector('[data-subcategory-editor]')) {
      payload.subcategories = collectSubcategoriesFromEditor(form);
    }
    for (const [key, rawValue] of formData.entries()) {
      if (key.startsWith('_') || key.endsWith('_id')) continue;
      if (key === 'subcategories_text') {
        payload.subcategories = parseSubcategoryLines(rawValue);
        continue;
      }
      const value = convertValue(key, String(rawValue).trim());
      if (value !== null || ['sale_price', 'description', 'brand_logo_path', 'product_brand_key', 'subcategory', 'subcategory_key'].includes(key)) {
        payload[key] = value;
      }
    }
    if (page === 'products' && payload.category_key !== 'packages') {
      payload.show_pack_flag = 'N';
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
      setStatus('', `Saving ${config.singular.toLowerCase()}…`, 'Please wait while the changes are saved.');
      const saved = await save(path, payload);
      setStatus('is-success', `${config.singular} saved.`, mode === 'create' ? `${config.singular} created successfully.` : 'Changes saved successfully.');
      await loadRecords();
      closeDrawer();
    } catch (error) {
      console.error(error);
      setStatus('is-warning', `Unable to save ${config.singular.toLowerCase()}.`, error.message || 'Please review the form and try again.');
    }
  }

  function populateFilters() {
    const categoryFilter = document.querySelector('[data-category-filter]');
    if (categoryFilter) categoryFilter.innerHTML = '<option value="">All categories</option>' + state.categories.map(category => `<option value="${esc(category.category_key)}">${esc(category.category_name || category.category_key)}</option>`).join('');
    const brandFilter = document.querySelector('[data-brand-filter]');
    if (brandFilter) brandFilter.innerHTML = '<option value="">All brands</option>' + state.brands.map(brand => `<option value="${esc(brand.brand_key)}">${esc(brand.brand_name || brand.brand_key)}</option>`).join('');
  }

  async function preloadLookups() {
    const [categories, brands, keyFeatures] = await Promise.all([
      api.request('/admin/categories').catch(() => api.request('/categories').catch(() => ({ items: [] }))),
      api.request('/admin/brands').catch(() => api.request('/brands').catch(() => ({ items: [] }))),
      api.request('/admin/key-features').catch(() => api.request('/key-features').catch(() => ({ items: [] })))
    ]);
    state.categories = api.getItems(categories);
    state.brands = api.getItems(brands);
    state.keyFeatures = api.getItems(keyFeatures);
    populateFilters();
  }

  async function loadRecords() {
    if (!api || !config) {
      setStatus('is-warning', 'Catalog page could not start.', 'Missing admin API client or page configuration.');
      return;
    }
    setStatus('', `Loading ${config.title.toLowerCase()}…`, 'Please wait while records are loaded.');
    try {
      await preloadLookups();
      let payload;
      try { payload = await api.request(config.endpoint); }
      catch (adminError) { payload = await api.request(config.publicEndpoint); }
      state.records = api.getItems(payload);
      state.filtered = state.records.slice();
      renderHead();
      applyFilters();
      setStatus('is-success', `${config.title} loaded successfully.`, `${state.records.length} ${config.title} records found.`);
    } catch (error) {
      console.error(error);
      state.records = [];
      state.filtered = [];
      renderHead();
      renderTable();
      setStatus('is-warning', `Unable to load ${config.title.toLowerCase()}.`, error.message || 'Please check that the admin server is running.');
    }
  }

  function setup() {
    const toggle = document.querySelector('[data-sidebar-toggle]');
    if (toggle && app) toggle.addEventListener('click', () => app.classList.toggle('sidebar-open'));
    ['[data-catalog-search]', '[data-admin-search]', '[data-category-filter]', '[data-brand-filter]', '[data-sort-filter]'].forEach(selector => {
      const element = document.querySelector(selector);
      if (element) element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters);
    });
    document.querySelector('[data-clear-filters]')?.addEventListener('click', () => {
      document.querySelectorAll('[data-catalog-search],[data-admin-search]').forEach(element => { element.value = ''; });
      document.querySelectorAll('[data-category-filter],[data-brand-filter]').forEach(element => { element.value = ''; });
      document.querySelectorAll('[data-sort-filter]').forEach(element => { element.value = 'recent'; });
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

  document.addEventListener('DOMContentLoaded', async () => { setup(); await loadRecords(); if (new URLSearchParams(window.location.search).get('action') === 'create') openDrawer({}, 'create'); });
}());

// --- batch59b-full-admin-delete-actions ---
(function () {
  'use strict';

  const MARKER = 'batch59b-full-admin-delete-actions';
  const PAGE_CONFIG = {
    products: { endpoint: '/admin/products', noun: 'product' },
    brands: { endpoint: '/admin/brands', noun: 'brand' },
    categories: { endpoint: '/admin/categories', noun: 'category' },
    'key-features': { endpoint: '/admin/key-features', noun: 'key feature' },
  };

  function qs(selector, root) { return (root || document).querySelector(selector); }
  function qsa(selector, root) { return Array.from((root || document).querySelectorAll(selector)); }

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

  function isAdmin() {
    if (window.RSAAdminRole && window.RSAAdminRole.isAdmin === true) return true;
    if (document.body && document.body.getAttribute('data-admin-role') === 'Admin') return true;
    const access = decodeJwt(window.localStorage.getItem('rsa_admin_access_token'));
    const id = decodeJwt(window.localStorage.getItem('rsa_admin_id_token'));
    const groups = access['cognito:groups'] || id['cognito:groups'] || [];
    return Array.isArray(groups) && groups.includes('Admin');
  }

  function currentPage() {
    const app = qs('[data-admin-app]');
    return app ? app.getAttribute('data-admin-page') : '';
  }

  function setStatus(kind, title, detail) {
    const banner = qs('[data-status-banner]');
    if (!banner) return;
    banner.className = 'status-banner';
    if (kind) banner.classList.add(kind);
    banner.innerHTML = `<strong>${escapeHtml(title)}</strong><span>${escapeHtml(detail || '')}</span>`;
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function rowId(row) {
    const firstStrong = row.querySelector('td strong');
    return firstStrong ? firstStrong.textContent.trim() : '';
  }

  function ensureDeleteButtons() {
    const page = currentPage();
    const cfg = PAGE_CONFIG[page];
    if (!cfg) return;

    // Only System Administrator/Admin gets the delete button. Standard users never see it.
    if (!isAdmin()) return;

    qsa('[data-table-body] tr[data-row-index]').forEach((row) => {
      if (row.querySelector('[data-batch59b-delete]')) return;
      const id = rowId(row);
      if (!id || id === '—') return;
      const actionCell = row.querySelector('td:last-child');
      if (!actionCell) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'table-action-link table-action-delete batch59b-delete-action';
      button.setAttribute('data-batch59b-delete', 'true');
      button.setAttribute('data-record-id', id);
      button.setAttribute('data-record-label', cfg.noun);
      button.textContent = 'Delete';
      actionCell.appendChild(document.createTextNode(' '));
      actionCell.appendChild(button);
    });
  }

  async function deleteRecord(id, cfg) {
    if (!window.RSAAdminApi) throw new Error('Admin API client is not loaded.');
    const base = window.RSAAdminApi.getApiBaseUrl().replace(/\/$/, '');
    const url = `${base}${cfg.endpoint}/${encodeURIComponent(id)}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        ...(typeof window.RSAAdminApi.getAuthHeaders === 'function' ? window.RSAAdminApi.getAuthHeaders() : {}),
      },
    });
    if (!response.ok) {
      let detail = '';
      try {
        const payload = await response.json();
        detail = payload && payload.detail ? payload.detail : JSON.stringify(payload);
      } catch (error) {
        detail = await response.text().catch(() => '');
      }
      throw new Error(detail || `${response.status} ${response.statusText}`);
    }
  }

  document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-batch59b-delete]');
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();

    const page = currentPage();
    const cfg = PAGE_CONFIG[page];
    const id = button.getAttribute('data-record-id') || '';
    if (!cfg || !id) return;

    const confirmed = window.confirm(`Delete this ${cfg.noun}? This is permanent and only allowed when dependency checks pass.`);
    if (!confirmed) return;

    try {
      button.disabled = true;
      setStatus('', `Deleting ${cfg.noun}…`, id);
      await deleteRecord(id, cfg);
      setStatus('is-success', `${cfg.noun.charAt(0).toUpperCase() + cfg.noun.slice(1)} deleted.`, id);
      const refresh = qs('[data-refresh-list]');
      if (refresh) refresh.click();
      else window.location.reload();
    } catch (error) {
      console.error(error);
      button.disabled = false;
      setStatus('is-warning', `Unable to delete ${cfg.noun}.`, error.message || 'The backend rejected this delete action.');
      window.alert(error.message || `Unable to delete ${cfg.noun}.`);
    }
  }, true);

  function scheduleEnsureDeleteButtons() {
    [0, 75, 250, 700, 1500].forEach((delay) => window.setTimeout(ensureDeleteButtons, delay));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleEnsureDeleteButtons);
  } else {
    scheduleEnsureDeleteButtons();
  }
  document.addEventListener('rsa-admin-role-ready', scheduleEnsureDeleteButtons);

  const target = qs('[data-table-body]') || document.body;
  if (target) {
    const observer = new MutationObserver(() => window.setTimeout(ensureDeleteButtons, 0));
    observer.observe(target, { childList: true, subtree: true });
  }

  window.RSABatch59BDeleteActions = { marker: MARKER, ensureDeleteButtons };
}());
