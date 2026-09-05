#!/usr/bin/env python3
"""Create a single-file, interactive preview without changing production output.

Usage: python3 scripts/make_preview.py [output.html]
Build the site first. The preview can be opened directly in a browser.
"""
from __future__ import annotations
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tests'))
from preview_utils import inline_page, SITE


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT/'website-preview.html'
    pages = {}
    for file in SITE.rglob('*.html'):
        relative = file.relative_to(SITE).as_posix()
        route = '/'+(relative[:-10] if relative.endswith('index.html') else relative)
        text = inline_page(file)
        def embed_download(match: re.Match) -> str:
            path = SITE/match[1].lstrip('/')
            mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            uri = 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
            return 'href="'+uri+'"'
        text = re.sub(r'href="(/(?:assets|citations)/[^\"]+\.(?:pdf|bib))"', embed_download, text)
        bridge = '''<script>
(() => {
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href]');
    if (!anchor || anchor.hasAttribute('download') || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const href = anchor.getAttribute('href');
    if (href.startsWith('/') || href.startsWith('#')) {
      event.preventDefault();
      parent.postMessage({type:'sikao-preview-navigate', href}, '*');
    }
  });
  document.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    parent.postMessage({type:'sikao-preview-theme', theme:document.documentElement.dataset.theme}, '*');
  });
})();
</script>'''
        pages[route] = text.replace('</body>', bridge+'</body>')
    data = json.dumps(pages, ensure_ascii=False).replace('<', '\\u003c')
    shell = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sikao Guo — interactive website preview</title>
<style>*{box-sizing:border-box}body{margin:0;background:#e7eeeb;font:14px Arial,sans-serif;color:#173540}.preview-bar{height:56px;background:#fff;border-bottom:1px solid #cddad5;display:flex;align-items:center;gap:16px;padding:0 20px}.preview-bar strong{font-size:14px}.preview-status{font-size:12px;color:#51676e}.preview-controls{display:flex;align-items:center;gap:8px;margin-left:auto}.preview-controls select,.preview-controls button{font:inherit;border:1px solid #cddad5;background:#fff;color:#173540;border-radius:5px;padding:6px 9px;cursor:pointer}.stage{height:calc(100vh - 56px);height:calc(100dvh - 56px);display:flex;justify-content:center}iframe{display:block;width:100%;height:100%;border:0;background:#fbfcfa;max-width:100%}@media(max-width:560px){.preview-status{display:none}.preview-bar{padding:0 10px;gap:8px}.preview-controls label{display:none}.preview-controls button{font-size:12px}}
</style></head><body><header class="preview-bar"><strong>Sikao Guo / website preview</strong><span class="preview-status">Not published</span><div class="preview-controls"><button type="button" id="home">Home</button><label for="width">View</label><select id="width"><option value="100%">Full width</option><option value="390px">Mobile · 390 px</option><option value="768px">Tablet · 768 px</option></select></div></header><div class="stage"><iframe id="preview" title="Sikao Guo website preview"></iframe></div><script type="application/json" id="pages-data">__PAGES__</script>
<script>
(() => {
  const pages = JSON.parse(document.getElementById('pages-data').textContent);
  const frame = document.getElementById('preview');
  let current = '/', theme = null;
  const render = () => {
    const requested = location.hash.slice(1) || '/';
    const split = requested.indexOf('#');
    const route = split < 0 ? requested : requested.slice(0, split);
    const anchor = split < 0 ? '' : requested.slice(split+1);
    current = Object.prototype.hasOwnProperty.call(pages, route) ? route : '/404.html';
    frame.onload = () => {
      const doc = frame.contentDocument;
      if (theme) {
        doc.documentElement.dataset.theme = theme;
        const button = doc.querySelector('[data-theme-toggle]');
        button?.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
        button?.setAttribute('aria-pressed', String(theme === 'dark'));
      }
      if (anchor) doc.getElementById(decodeURIComponent(anchor))?.scrollIntoView();
    };
    frame.srcdoc = pages[current];
  };
  const navigate = href => {
    const destination = href.startsWith('#') ? current+href : href;
    if (location.hash.slice(1) === destination) render();
    else location.hash = destination;
  };
  window.addEventListener('message', event => {
    if (event.source !== frame.contentWindow || !event.data) return;
    if (event.data.type === 'sikao-preview-navigate' && typeof event.data.href === 'string') navigate(event.data.href);
    if (event.data.type === 'sikao-preview-theme' && ['light','dark'].includes(event.data.theme)) theme = event.data.theme;
  });
  window.addEventListener('hashchange', render);
  document.getElementById('width').addEventListener('change', event => frame.style.width = event.target.value);
  document.getElementById('home').addEventListener('click', () => navigate('/'));
  render();
})();
</script></body></html>'''
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(shell.replace('__PAGES__',data),encoding='utf-8')
    print(f'Created {destination} ({destination.stat().st_size:,} bytes; {len(pages)} pages)')


if __name__ == '__main__': main()
