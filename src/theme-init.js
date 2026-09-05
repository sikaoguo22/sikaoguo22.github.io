/* Run before paint. Storage restrictions must not prevent the page from loading. */
(() => {
  document.documentElement.classList.add('js');
  let theme = null;
  try { theme = localStorage.getItem('sikao-theme'); } catch (_) { /* No persistent storage. */ }
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = ['light', 'dark'].includes(theme) ? theme : (prefersDark ? 'dark' : 'light');
})();
