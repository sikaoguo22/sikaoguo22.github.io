'use strict';
(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('[data-theme-toggle]');
  const updateThemeLabel = () => {
    const dark = root.dataset.theme === 'dark';
    if (themeButton) {
      themeButton.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
      themeButton.setAttribute('aria-pressed', String(dark));
    }
  };
  updateThemeLabel();
  themeButton?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('sikao-theme', root.dataset.theme); } catch (_) { /* Theme still works for this page. */ }
    updateThemeLabel();
  });
  const menuButton = document.querySelector('[data-menu-toggle]');
  const nav = document.getElementById('primary-navigation');
  const closeMenu = () => {
    nav?.classList.remove('is-open');
    menuButton?.setAttribute('aria-expanded', 'false');
    menuButton?.setAttribute('aria-label', 'Open navigation');
  };
  menuButton?.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    nav?.classList.toggle('is-open', open);
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
      closeMenu(); menuButton.focus();
    }
  });
  const widthQuery = window.matchMedia('(min-width: 781px)');
  widthQuery.addEventListener('change', event => { if (event.matches) closeMenu(); });

  const search = document.querySelector('[data-publication-search]');
  const filters = document.querySelectorAll('[data-publication-filter]');
  const publications = [...document.querySelectorAll('[data-publication]')];
  const resultCount = document.querySelector('[data-result-count]');
  const empty = document.querySelector('[data-empty-state]');
  let filter = 'all';
  const applyFilter = () => {
    const term = (search?.value || '').trim().toLocaleLowerCase();
    let count = 0;
    for (const item of publications) {
      const matchesType = filter === 'all' || item.dataset.type === filter;
      const matchesSearch = item.dataset.search.toLocaleLowerCase().includes(term);
      item.hidden = !(matchesType && matchesSearch);
      if (!item.hidden) count += 1;
    }
    if (resultCount) resultCount.textContent = `${count} of ${publications.length} selected publications`;
    if (empty) empty.hidden = count !== 0;
  };
  filters.forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.publicationFilter;
    filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    applyFilter();
  }));
  search?.addEventListener('input', applyFilter);
  if (search) applyFilter();

  document.querySelectorAll('[data-copy-citation]').forEach(button => {
    button.addEventListener('click', async () => {
      const citation = button.dataset.copyCitation;
      const original = button.textContent;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(citation);
        button.textContent = 'Copied';
        const status = document.querySelector('[data-copy-status]');
        if (status) status.textContent = 'Citation copied to clipboard.';
      } catch (_) {
        // A read-only field provides an accessible fallback without deprecated execCommand.
        const parent = button.closest('[data-publication]');
        let field = parent?.querySelector('[data-citation-fallback]');
        if (!field && parent) {
          field = document.createElement('textarea');
          field.dataset.citationFallback = '';
          field.setAttribute('aria-label', 'Citation. Select and copy this text.');
          field.setAttribute('readonly', '');
          field.rows = 4;
          field.style.width = '100%';
          field.value = citation;
          parent.querySelector('.publication-body').appendChild(field);
        }
        field?.focus(); field?.select();
        button.textContent = 'Select text to copy';
      }
      window.setTimeout(() => { button.textContent = original; }, 2200);
    });
  });
})();
