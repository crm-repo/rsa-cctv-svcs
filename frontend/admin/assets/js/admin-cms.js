(function () {
  'use strict';

  const BATCH55C_HOTFIX_V2_VERSION = 'batch55c-hotfix-v2-admin-polish-corrections';
  window.RSA_BATCH55C_CMS_HOTFIX_V2_VERSION = BATCH55C_HOTFIX_V2_VERSION;

  const BATCH55C_HOTFIX_VERSION = 'batch55c-hotfixes-admin-polish-corrections';
  window.RSA_BATCH55C_CMS_HOTFIX_VERSION = BATCH55C_HOTFIX_VERSION;

  const api = window.RSAAdminApi;
  const app = document.querySelector('[data-admin-app]');
  const page = app ? app.getAttribute('data-admin-page') : '';
  const state = { records: [], filtered: [] };

  const configs = {
    about: {
      endpoint: '/admin/about',
      publicEndpoint: '/about',
      writeEndpoint: '/admin/about',
      idField: 'about_id',
      title: 'About Us',
      singular: 'About Record',
      kicker: 'Company Content',
      columns: [['about_id', 'ID'], ['hero_title', 'Hero Title'], ['show_flag', 'Visible'], ['updated_at', 'Updated']],
      detailFields: ['about_id', 'show_flag', 'hero_title', 'hero_subtitle', 'hero_image_path', 'company_story_title', 'company_story_body', 'mission_title', 'mission_body', 'vision_title', 'vision_body', 'why_choose_title', 'why_choose_body', 'why_choose_bullet_01', 'why_choose_bullet_02', 'why_choose_bullet_03', 'why_choose_bullet_04', 'why_choose_bullet_05', 'why_choose_bullet_06', 'meta_title', 'meta_description', 'created_at', 'updated_at']
    },
    'project-gallery': {
      endpoint: '/admin/project-gallery',
      publicEndpoint: '/project-gallery',
      writeEndpoint: '/admin/project-gallery',
      idField: 'project_id',
      title: 'Project Gallery',
      singular: 'Project Item',
      kicker: 'Gallery Content',
      columns: [['project_id', 'ID'], ['project_title', 'Project'], ['image_path', 'Image'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible']],
      detailFields: ['project_id', 'show_flag', 'display_seq', 'project_title', 'project_description', 'image_path', 'alt_text', 'created_at', 'updated_at']
    },
    services: {
      endpoint: '/admin/services',
      publicEndpoint: '/services',
      writeEndpoint: '/admin/services',
      idField: 'service_id',
      title: 'Services',
      singular: 'Service',
      kicker: 'Service Content',
      columns: [['service_id', 'ID'], ['service_title', 'Service'], ['service_slug', 'Slug'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible']],
      detailFields: ['service_id', 'show_flag', 'display_seq', 'service_title', 'service_slug', 'short_description', 'service_description', 'image_path', 'icon_path', 'cta_label', 'cta_url', 'meta_title', 'meta_description', 'created_at', 'updated_at']
    },
    'contact-us': {
      endpoint: '/admin/contact-us',
      publicEndpoint: '/contact',
      writeEndpoint: '/admin/contact-us',
      idField: 'contact_us_id',
      title: 'Contact Us',
      singular: 'Contact Record',
      kicker: 'Contact Content',
      columns: [['contact_us_id', 'ID'], ['contact_type', 'Type'], ['display_seq', 'Display Seq'], ['show_flag', 'Visible'], ['company_email', 'Company Email'], ['person_name', 'Person'], ['platform_name', 'Platform']],
      detailFields: ['contact_us_id', 'show_flag', 'contact_type', 'display_seq', 'primary_contact_number', 'secondary_contact_number', 'company_email', 'company_address', 'showroom_address', 'whatsapp_number', 'viber_number', 'business_hours', 'person_image_path', 'person_name', 'position_title', 'department', 'phone_number', 'email_address', 'platform_name', 'platform_key', 'profile_url', 'icon_code', 'created_at', 'updated_at']
    }
  };

  const config = configs[page];

  function esc(value) { return String(value ?? '').replace(/[&<>\"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char])); }
  function label(value) { return value === null || value === undefined || value === '' ? '—' : String(value); }
  function fmt(field, value) { return label(value); }
  function flag(value) { const yes = value === 'Y'; return `<span class="flag-pill ${yes ? 'is-y' : 'is-n'}">${yes ? 'Visible' : 'Hidden'}</span>`; }

  function setStatus(type, title, message) {
    const banner = document.querySelector('[data-status-banner]');
    if (!banner) return;
    banner.className = 'status-banner';
    if (type) banner.classList.add(type);
    banner.innerHTML = `<strong>${esc(title)}</strong><span>${esc(message)}</span>`;
  }

  function text(record) { return Object.values(record || {}).map(value => String(value ?? '')).join(' ').toLowerCase(); }
  function searchValue() { return String(document.querySelector('[data-cms-search]')?.value || document.querySelector('[data-admin-search]')?.value || '').trim().toLowerCase(); }
  function slugify(value) { return String(value || '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'item'; }
  function sortValue() { return String(document.querySelector('[data-sort-filter]')?.value || 'recent'); }
  function recordDateValue(record) { const parsed = Date.parse(record.created_at || record.updated_at || ''); return Number.isFinite(parsed) ? parsed : 0; }
  function displayName(record) { return String(record.hero_title || record.project_title || record.service_title || record.person_name || record.platform_name || record.contact_us_id || '').toLowerCase(); }
  function sortRecords(records) { const mode = sortValue(); return records.slice().sort((a,b)=>{ if(mode==='display_seq') return Number(a.display_seq || 0)-Number(b.display_seq || 0); if(mode==='oldest') return recordDateValue(a)-recordDateValue(b); if(mode==='az') return displayName(a).localeCompare(displayName(b)); if(mode==='za') return displayName(b).localeCompare(displayName(a)); return recordDateValue(b)-recordDateValue(a); }); }

  function applyFilters() {
    const query = searchValue();
    const contactType = document.querySelector('[data-contact-type-filter]')?.value || '';
    state.filtered = sortRecords(state.records.filter(record =>
      (!query || text(record).includes(query)) &&
      (!contactType || record.contact_type === contactType)
    ));
    renderTable();
  }

  function setCount(message) { const el = document.querySelector('[data-record-count]'); if (el) el.textContent = message; }

  function renderHead() {
    const head = document.querySelector('[data-table-head]');
    if (!head || !config) return;
    head.innerHTML = `<tr>${config.columns.map(([, labelText]) => `<th>${esc(labelText)}</th>`).join('')}<th>Action</th></tr>`;
  }

  function renderTable() {
    const body = document.querySelector('[data-table-body]');
    if (!body || !config) return;
    setCount(`${state.filtered.length} ${config.title} records found`);
    if (!state.filtered.length) {
      body.innerHTML = `<tr><td colspan="${config.columns.length + 1}" class="empty-cell">No matching ${esc(config.title)} records found.</td></tr>`;
      return;
    }
    body.innerHTML = state.filtered.map((record, index) => {
      const cells = config.columns.map(([field]) => {
        if (field === 'show_flag') return `<td>${flag(record[field])}</td>`;
        const value = fmt(field, record[field]);
        if (field.endsWith('_id')) return `<td><strong>${esc(value)}</strong></td>`;
        return `<td>${esc(value)}</td>`;
      }).join('');
      return `<tr data-row-index="${index}">${cells}<td><button class="table-action-link" type="button" data-view-index="${index}">View / Edit</button></td></tr>`;
    }).join('');
  }

  function detailRows(record) {
    return config.detailFields.map(field => `<div class="detail-row"><span>${esc(field.replace(/_/g, ' '))}</span><span>${esc(fmt(field, record[field]))}</span></div>`).join('');
  }

  function requiredLabel(labelText, attrs = '') { return String(attrs || '').includes('required') ? `${labelText} <span class="required-star" aria-hidden="true">*</span>` : labelText; }
  function input(name, labelText, value = '', type = 'text', attrs = '') {
    const ro = String(attrs || '').includes('readonly');
    const mediaNames = new Set(['image_path', 'brand_logo_path', 'hero_image_path', 'company_story_image_path', 'service_image_path', 'project_image_path', 'logo_path', 'icon_path', 'person_image_path']);
    const isMedia = mediaNames.has(String(name || '')) || String(name || '').endsWith('_image_path') || String(name || '').endsWith('_logo_path');
    const labelClasses = [ro ? 'is-readonly-field' : '', isMedia ? 'media-field-label span-2' : ''].filter(Boolean).join(' ');
    return `<label${labelClasses ? ` class="${labelClasses}"` : ''}><span>${requiredLabel(esc(labelText), attrs)}</span><input class="${ro ? 'is-readonly-field' : ''}" name="${esc(name)}" type="${esc(type)}" value="${esc(value ?? '')}" ${attrs} /></label>`;
  }

  function select(name, labelText, value, options) {
    return `<label><span>${esc(labelText)}</span><select name="${esc(name)}">${options.map(opt => `<option value="${esc(opt.value)}" ${String(opt.value) === String(value ?? '') ? 'selected' : ''}>${esc(opt.label)}</option>`).join('')}</select></label>`;
  }

  function textarea(name, labelText, value = '', rows = 4, cls = 'span-2') {
    return `<label class="${cls}"><span>${esc(labelText)}</span><textarea name="${esc(name)}" rows="${rows}">${esc(value ?? '')}</textarea></label>`;
  }

  function aboutForm(record) {
    const isCreate = !record.about_id;
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <div class="catalog-form-grid">
        ${input('about_id', 'About ID', record.about_id || 'Auto-generated on save', 'text', 'readonly')}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }])}
        ${input('hero_title', 'Hero Title', record.hero_title || '', 'text', 'required')}
        ${input('hero_image_path', 'Hero Image', record.hero_image_path || '')}
        ${textarea('hero_subtitle', 'Hero Subtitle', record.hero_subtitle || '')}
        ${input('company_story_title', 'Company Story Title', record.company_story_title || '')}
        ${input('company_story_image_path', 'Company Story Image', record.company_story_image_path || '')}
        ${textarea('company_story_body', 'Company Story Body', record.company_story_body || '')}
        ${input('mission_title', 'Mission Title', record.mission_title || '')}
        ${textarea('mission_body', 'Mission Body', record.mission_body || '')}
        ${input('vision_title', 'Vision Title', record.vision_title || '')}
        ${textarea('vision_body', 'Vision Body', record.vision_body || '')}
        ${input('why_choose_title', 'Why Choose Title', record.why_choose_title || '')}
        ${textarea('why_choose_body', 'Why Choose Body', record.why_choose_body || '')}
        ${input('why_choose_bullet_01', 'Why Choose Bullet 01', record.why_choose_bullet_01 || '')}
        ${input('why_choose_bullet_02', 'Why Choose Bullet 02', record.why_choose_bullet_02 || '')}
        ${input('why_choose_bullet_03', 'Why Choose Bullet 03', record.why_choose_bullet_03 || '')}
        ${input('why_choose_bullet_04', 'Why Choose Bullet 04', record.why_choose_bullet_04 || '')}
        ${input('why_choose_bullet_05', 'Why Choose Bullet 05', record.why_choose_bullet_05 || '')}
        ${input('why_choose_bullet_06', 'Why Choose Bullet 06', record.why_choose_bullet_06 || '')}
        ${input('meta_title', 'Meta Title', record.meta_title || '')}
        ${textarea('meta_description', 'Meta Description', record.meta_description || '')}
      </div>${drawerActions(isCreate)}`;
  }

  function projectForm(record) {
    const isCreate = !record.project_id;
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <div class="catalog-form-grid">
        ${input('project_id', 'Project ID', record.project_id || 'Auto-generated on save', 'text', 'readonly')}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }])}
        ${input('project_title', 'Project Title', record.project_title || '', 'text', 'required')}
        ${input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number')}
        ${input('image_path', 'Image', record.image_path || '', 'text', 'required')}
        ${input('alt_text', 'Alt Text', record.alt_text || '')}
        ${textarea('project_description', 'Project Description', record.project_description || '')}
      </div>${drawerActions(isCreate)}`;
  }

  function serviceForm(record) {
    const isCreate = !record.service_id;
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <div class="catalog-form-grid">
        ${input('service_id', 'Service ID', record.service_id || 'Auto-generated on save', 'text', 'readonly')}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }])}
        ${input('service_title', 'Service Title', record.service_title || '', 'text', 'required')}
        ${input('service_slug', 'Service Slug', record.service_slug || '', 'text', 'readonly data-system-key="true"')}
        ${input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number')}
        ${input('image_path', 'Image', record.image_path || '')}
        ${input('icon_path', 'Icon Image', record.icon_path || '')}
        ${input('cta_label', 'CTA Label', record.cta_label || '')}
        ${input('cta_url', 'CTA URL', record.cta_url || '')}
        ${textarea('short_description', 'Short Description', record.short_description || '', 3)}
        ${textarea('service_description', 'Service Description', record.service_description || '')}
        ${input('meta_title', 'Meta Title', record.meta_title || '')}
        ${textarea('meta_description', 'Meta Description', record.meta_description || '')}
      </div>${drawerActions(isCreate)}`;
  }

  function contactForm(record) {
    const isCreate = !record.contact_us_id;
    return `<input type="hidden" name="_mode" value="${isCreate ? 'create' : 'update'}" />
      <div class="catalog-form-grid">
        ${input('contact_us_id', 'Contact ID', record.contact_us_id || 'Auto-generated by contact type', 'text', 'readonly')}
        ${select('contact_type', 'Contact Type', record.contact_type || 'Contact Person', [{ value: 'Company Contact', label: 'Company Contact' }, { value: 'Contact Person', label: 'Contact Person' }, { value: 'Social Media', label: 'Social Media' }])}
        ${select('show_flag', 'Public Visibility', record.show_flag || 'Y', [{ value: 'Y', label: 'Y - Visible' }, { value: 'N', label: 'N - Hidden' }])}
        ${input('display_seq', 'Display Seq', record.display_seq ?? 10, 'number')}
        ${input('primary_contact_number', 'Primary Contact Number', record.primary_contact_number || '')}
        ${input('secondary_contact_number', 'Secondary Contact Number', record.secondary_contact_number || '')}
        ${input('company_email', 'Company Email', record.company_email || '', 'email')}
        ${textarea('company_address', 'Company Address', record.company_address || '')}
        ${textarea('showroom_address', 'Showroom Address', record.showroom_address || '')}
        ${input('whatsapp_number', 'WhatsApp Number', record.whatsapp_number || '')}
        ${input('viber_number', 'Viber Number', record.viber_number || '')}
        ${input('business_hours', 'Business Hours', record.business_hours || '')}
        ${input('person_image_path', 'Contact Person Photo', record.person_image_path || '')}
        ${input('person_name', 'Person Name', record.person_name || '')}
        ${input('position_title', 'Position Title', record.position_title || '')}
        ${input('department', 'Department', record.department || '')}
        ${input('phone_number', 'Phone Number', record.phone_number || '')}
        ${input('email_address', 'Email Address', record.email_address || '', 'email')}
        ${input('platform_name', 'Platform Name', record.platform_name || '')}
        ${input('platform_key', 'Platform Key', record.platform_key || '', 'text', 'readonly data-system-key="true"')}
        ${input('profile_url', 'Profile URL', record.profile_url || '')}
        ${input('icon_code', 'Icon Code', record.icon_code || '')}
      </div>${drawerActions(isCreate)}`;
  }

  function drawerActions(isCreate) {
    return `<div class="drawer-actions"><button class="admin-button" type="submit" data-save-button>${isCreate ? `Create ${config.singular}` : 'Save Changes'}</button><button class="admin-button secondary" type="button" data-close-drawer>Close</button></div>`;
  }

  function formHtml(record) {
    if (page === 'about') return aboutForm(record);
    if (page === 'project-gallery') return projectForm(record);
    if (page === 'services') return serviceForm(record);
    if (page === 'contact-us') return contactForm(record);
    return '';
  }


  function bindSystemGeneratedKeys(form) {
    if (!form || form.dataset.boundSystemKeys === 'true') return;
    form.dataset.boundSystemKeys = 'true';
    const pairs = [
      ['service_title', 'service_slug'],
      ['platform_name', 'platform_key']
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

  function snapshotForm(form) { return JSON.stringify(collectFormPayload(form)); }
  function setSaveDirtyState(form, changed = false) {
    const button = form.querySelector('[data-save-button]');
    if (!button) return;
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    button.disabled = mode !== 'create' && !changed;
  }
  function bindDirtyTracking(form) {
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    window.setTimeout(() => { form.dataset.initialPayload = snapshotForm(form); setSaveDirtyState(form, mode === 'create'); }, 0);
    if (form.dataset.boundDirtyTracking === 'true') return;
    form.dataset.boundDirtyTracking = 'true';
    form.addEventListener('input', () => setSaveDirtyState(form, snapshotForm(form) !== form.dataset.initialPayload));
    form.addEventListener('change', () => setSaveDirtyState(form, snapshotForm(form) !== form.dataset.initialPayload));
  }

  function openDrawer(record = {}, mode = 'view') {
    const drawer = document.querySelector('[data-detail-drawer]');
    const title = document.querySelector('[data-drawer-title]');
    const kicker = document.querySelector('[data-drawer-kicker]');
    const body = document.querySelector('[data-drawer-body]');
    const form = document.querySelector('[data-cms-form]');
    if (!drawer || !title || !body || !form) return;
    title.textContent = mode === 'create' ? `Add ${config.singular}` : (record[config.idField] || 'CMS Detail');
    if (kicker) kicker.textContent = config.kicker;
    body.innerHTML = '';
    form.hidden = false;
    form.dataset.recordId = record[config.idField] || '';
    form.innerHTML = formHtml(record);
    bindSystemGeneratedKeys(form);
    bindDirtyTracking(form);
    if (window.RSAAdminMedia && typeof window.RSAAdminMedia.enhanceAll === 'function') window.RSAAdminMedia.enhanceAll(form);
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
  }

  function closeDrawer() {
    const drawer = document.querySelector('[data-detail-drawer]');
    if (drawer) { drawer.classList.remove('is-open'); drawer.setAttribute('aria-hidden', 'true'); }
  }

  function convertValue(key, value) {
    if (value === '') return null;
    if (['display_seq'].includes(key)) return Number.parseInt(value, 10) || 0;
    return value;
  }

  function collectFormPayload(form) {
    const formData = new FormData(form);
    const payload = {};
    for (const [key, rawValue] of formData.entries()) {
      if (key.startsWith('_') || key.endsWith('_id')) continue;
      const value = convertValue(key, String(rawValue).trim());
      payload[key] = value;
    }
    payload.updated_by = 'local-admin';
    return payload;
  }

  async function saveCmsRecord(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const mode = form.querySelector('[name="_mode"]')?.value || 'update';
    const recordId = form.dataset.recordId;
    const payload = collectFormPayload(form);
    const path = mode === 'create' ? config.writeEndpoint : `${config.writeEndpoint}/${encodeURIComponent(recordId)}`;
    const save = mode === 'create' ? api.postJson : api.putJson;
    try {
      setStatus('', 'Saving CMS record…', `${mode === 'create' ? 'Creating' : 'Updating'} ${config.singular.toLowerCase()}.`);
      const saved = await save(path, payload);
      setStatus('is-success', `${config.singular} saved.`, `${saved[config.idField] || 'Record'} was saved successfully.`);
      await loadRecords();
      closeDrawer();
    } catch (error) {
      console.error(error);
      setStatus('is-warning', `Unable to save ${config.singular.toLowerCase()}.`, error.message || 'Check backend validation details.');
    }
  }

  async function loadRecords() {
    if (!api || !config) {
      setStatus('is-warning', 'CMS page could not start.', 'Missing admin API client or page configuration.');
      return;
    }
    setStatus('', `Loading ${config.title.toLowerCase()}…`, 'Please wait while records are loaded.');
    try {
      let payload;
      try { payload = await api.request(config.endpoint); }
      catch (adminError) {
        if (page === 'about') payload = { items: [await api.request(config.publicEndpoint)], total: 1 };
        else payload = await api.request(config.publicEndpoint);
      }
      if (page === 'contact-us' && payload && !Array.isArray(payload.items) && (payload.company_contact || payload.contact_persons || payload.social_media)) {
        payload = { items: [payload.company_contact, ...(payload.contact_persons || []), ...(payload.social_media || [])].filter(Boolean) };
      }
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
    ['[data-cms-search]', '[data-admin-search]', '[data-sort-filter]', '[data-contact-type-filter]'].forEach(selector => {
      const element = document.querySelector(selector);
      if (element) element.addEventListener(element.tagName === 'INPUT' ? 'input' : 'change', applyFilters);
    });
    document.querySelector('[data-clear-filters]')?.addEventListener('click', () => {
      document.querySelectorAll('[data-cms-search],[data-admin-search]').forEach(element => { element.value = ''; });
      document.querySelectorAll('[data-contact-type-filter]').forEach(element => { element.value = ''; });
      document.querySelectorAll('[data-sort-filter]').forEach(element => { element.value = 'recent'; });
      applyFilters();
    });
    document.querySelector('[data-refresh-list]')?.addEventListener('click', loadRecords);
    document.querySelector('[data-open-create]')?.addEventListener('click', () => openDrawer({}, 'create'));
    document.querySelector('[data-cms-form]')?.addEventListener('submit', saveCmsRecord);
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
