"""Optional browser regression checks: pip install playwright; playwright install chromium.

The site itself and the standard regression suite have no third-party dependencies.
Set CHROMIUM_EXECUTABLE to use an existing Chromium installation.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from preview_utils import SITE, inline_page
from test_site import Document


def main() -> None:
    results = {'page_layout_checks': [], 'interactions': []}
    home = Document((SITE/'index.html').read_text(encoding='utf-8'))
    base_prefix = urlsplit(home.canonicals[0]).path.rstrip('/')
    with sync_playwright() as p:
        launch = {'headless': True}
        executable = os.environ.get('CHROMIUM_EXECUTABLE')
        if executable:
            launch['executable_path'] = executable
        browser = p.chromium.launch(**launch)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, color_scheme='light')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for width in (320, 390, 768, 1024, 1440):
            page.set_viewport_size({'width': width, 'height': 1000})
            for path in sorted(SITE.rglob('*.html')):
                page.set_content(inline_page(path, base_prefix), wait_until='load')
                layout = page.evaluate('''() => ({width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
                  brokenImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).length})''')
                assert layout['scrollWidth'] <= width + 1, (str(path), layout)
                assert layout['brokenImages'] == 0, (str(path), 'broken images')
                results['page_layout_checks'].append({'page': str(path.relative_to(SITE)), 'width': width, 'passed': True})
        assert not errors, errors

        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.set_content(inline_page(SITE/'index.html', base_prefix), wait_until='load')
        toggle = page.locator('[data-drift-toggle]')
        toggle.click()
        assert toggle.get_attribute('aria-pressed') == 'true'
        results['interactions'].append('Background animation can be paused.')

        nojs = browser.new_page(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        nojs.set_content(inline_page(SITE/'index.html', base_prefix), wait_until='load')
        assert nojs.locator('.cv-item:visible').count() == 5
        assert nojs.locator('#primary-navigation').is_visible()
        results['interactions'].append('Core content and navigation remain available without JavaScript.')
        reduced = browser.new_page(reduced_motion='reduce')
        reduced.set_content(inline_page(SITE/'index.html', base_prefix), wait_until='load')
        assert reduced.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
        assert reduced.locator('html').evaluate('(el) => getComputedStyle(el).scrollBehavior') == 'auto'
        results['interactions'].append('Reduced-motion preference disables smooth scrolling.')
        assert not errors, errors
        browser.close()
    results['javascript_errors'] = errors
    output = Path(os.environ.get('BROWSER_REPORT', 'browser-results.json'))
    output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f"PASS: {len(results['page_layout_checks'])} page/viewport checks; {len(results['interactions'])} interaction checks; no JavaScript errors.")


if __name__ == '__main__':
    main()
