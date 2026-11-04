'use strict';
(() => {
  /* ---------- Publication search and type filter ---------- */
  const search = document.querySelector('[data-publication-search]');
  const typeFilter = document.querySelector('[data-publication-filter]');
  const publications = [...document.querySelectorAll('[data-publication]')];
  const groups = [...document.querySelectorAll('[data-year-group]')];
  const resultCount = document.querySelector('[data-result-count]');
  const empty = document.querySelector('[data-empty-state]');
  const initialCount = resultCount?.textContent;
  const plural = n => `${n} publication${n === 1 ? '' : 's'}`;
  const applyFilter = () => {
    const term = (search?.value || '').trim().toLocaleLowerCase();
    const type = typeFilter?.value || 'all';
    let count = 0;
    for (const item of publications) {
      const show = (type === 'all' || item.dataset.type === type) && item.dataset.search.toLocaleLowerCase().includes(term);
      item.hidden = !show;
      if (show) count += 1;
    }
    for (const group of groups) {
      const visible = group.querySelectorAll('[data-publication]:not([hidden])').length;
      group.hidden = visible === 0;
      const label = group.querySelector('[data-year-count]');
      if (label) label.textContent = plural(visible);
    }
    const filtered = term || type !== 'all';
    if (resultCount) resultCount.textContent = filtered ? `${count} of ${plural(publications.length)}` : initialCount;
    if (empty) empty.hidden = count !== 0;
  };
  search?.addEventListener('input', applyFilter);
  typeFilter?.addEventListener('change', applyFilter);
  if (search) applyFilter();

  /* ---------- Background drift: faint warm specks, paused on request ---------- */
  const canvas = document.querySelector('[data-drift]');
  const toggle = document.querySelector('[data-drift-toggle]');
  const ctx = canvas?.getContext?.('2d');
  if (!canvas || !ctx) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const color = getComputedStyle(document.documentElement).getPropertyValue('--speck').trim() || '#8c8070';
  let specks = [];
  let width = 0, height = 0, frame = 0, last = 0;
  let paused = false;
  try { paused = localStorage.getItem('sikao-drift') === 'paused'; } catch (_) { /* Storage unavailable. */ }

  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth; height = window.innerHeight;
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.round(Math.min(140, (width * height) / 9000));
    specks = Array.from({ length: n }, () => ({
      x: Math.random() * width, y: Math.random() * height,
      r: 0.5 + Math.random() * 1.1, a: 0.12 + Math.random() * 0.28,
      phase: Math.random() * Math.PI * 2, speed: 0.04 + Math.random() * 0.1,
    }));
    draw(0);
  };
  const draw = dt => {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = color;
    for (const s of specks) {
      s.phase += dt * 0.0003;
      s.x += (Math.cos(s.phase) * 0.6 + 0.4) * s.speed * dt * 0.06;
      s.y += Math.sin(s.phase * 1.3) * s.speed * dt * 0.03;
      if (s.x > width + 4) s.x = -4;
      if (s.y < -4) s.y = height + 4; else if (s.y > height + 4) s.y = -4;
      ctx.globalAlpha = s.a;
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  };
  const loop = now => {
    const dt = last ? Math.min(now - last, 64) : 16;
    last = now;
    draw(dt);
    frame = requestAnimationFrame(loop);
  };
  const sync = () => {
    cancelAnimationFrame(frame); last = 0;
    const still = paused || reduced.matches;
    if (!still) frame = requestAnimationFrame(loop);
    if (toggle) {
      toggle.textContent = paused ? 'Resume background' : 'Pause background';
      toggle.setAttribute('aria-pressed', String(paused));
      toggle.hidden = reduced.matches;
    }
  };
  toggle?.addEventListener('click', () => {
    paused = !paused;
    try { localStorage.setItem('sikao-drift', paused ? 'paused' : 'running'); } catch (_) { /* Session-only. */ }
    sync();
  });
  reduced.addEventListener?.('change', sync);
  let resizeTimer = 0;
  window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(resize, 150); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancelAnimationFrame(frame); else sync(); });
  resize();
  sync();
})();
