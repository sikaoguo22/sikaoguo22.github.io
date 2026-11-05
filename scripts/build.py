#!/usr/bin/env python3
"""Build Sikao Guo's static website with Python's standard library.

    python3 scripts/build.py
    python3 -m http.server 8000 --directory site

Content lives in content/*.json. Presentation lives in src/. Set SITE_URL for
custom domains or project subpaths. No network access is needed to build.
"""
from __future__ import annotations

import html
import json
import os
import shutil
import sys
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'
SRC = ROOT / 'src'
OUT = ROOT / 'site'
STAGING = ROOT / '.site-build'
SITE_URL = os.environ.get('SITE_URL', 'https://sikaoguo22.github.io').rstrip('/')
parsed_url = urlparse(SITE_URL)
if parsed_url.scheme not in ('https', 'http') or not parsed_url.netloc or parsed_url.query or parsed_url.fragment:
    raise SystemExit('SITE_URL must be an absolute http(s) URL without a query or fragment.')
PREFIX = parsed_url.path.rstrip('/')


def load_json(name: str) -> Any:
    path = CONTENT / f'{name}.json'
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'Cannot load {path}: {error}') from error


site = load_json('site')
base = Template((SRC / 'templates/base.html').read_text(encoding='utf-8'))
pages: list[str] = []


def e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def link(path: str) -> str:
    """Resolve site-root paths while retaining external and fragment links."""
    if path.startswith(('https://', 'http://', 'mailto:', '#')):
        return path
    if ':' in path.split('/')[0]:
        raise ValueError(f'Unsupported link scheme: {path}')
    return f'{PREFIX}/{path.lstrip("/")}'


def external(href: str, label: str, cls: str = '') -> str:
    classes = ('ext ' + cls).strip()
    return f'<a class="{e(classes)}" href="{e(href)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'


def text_link(href: str, label: str) -> str:
    return f'<a class="arrow" href="{e(link(href))}">{e(label)}</a>'


NAV = [('Summary', '/#summary'), ('Experience', '/#experience'), ('Education', '/#education'), ('Contact', '/#contact')]


def header(active: str) -> str:
    nav = ''.join(f'<a href="{e(link(href))}"' + (' aria-current="page"' if active == label else '') + f'>{label}</a>' for label, href in NAV)
    return f'''<header class="site-header"><div class="shell header-inner">
<a class="wordmark" href="{link('/')}" aria-label="Sikao Guo, home">Sikao Guo</a>
<nav class="primary-nav" id="primary-navigation" aria-label="Main navigation">{nav}</nav></div></header>'''


def social_links(keys=(('linkedin', 'LinkedIn'), ('scholar', 'Google Scholar'))) -> str:
    return ''.join(external(site['social'][k], label) for k, label in keys)


def footer() -> str:
    return f'''<footer class="site-footer"><div class="shell footer-inner"><span>© 2026 Sikao Guo · Computational biophysics · molecular modeling &amp; simulation</span><div class="footer-links"><a href="mailto:{e(site['email'])}">{e(site['email'])}</a>{social_links()}<button class="text-button js-only" type="button" data-drift-toggle aria-pressed="false">Pause background</button></div></div></footer>'''


def person_schema() -> dict[str, Any]:
    return {'@context':'https://schema.org', '@type':'Person', 'name':site['shortName'],
            'url':f'{SITE_URL}/', 'image':f'{SITE_URL}/assets/sikao-guo-800.webp',
            'description':site['description'], 'jobTitle':'Computational Biophysicist',
            'sameAs':list(site['social'].values()),
            'knowsAbout':['Computational biophysics','Molecular modeling','Protein conformational sampling','Molecular dynamics','Biomolecular self-assembly','Scientific software']}


def write_page(route: str, title: str, body: str, active: str = '', description: str | None = None, body_class: str = '', extra_head: str = '') -> None:
    destination = STAGING / ('404.html' if route == '404.html' else route.strip('/') + '/index.html' if route.strip('/') else 'index.html')
    destination.parent.mkdir(parents=True, exist_ok=True)
    canonical = f'{SITE_URL}/{route.lstrip("/")}'
    markup = base.substitute(title=e(f'{title} | Sikao Guo'), description=e(description or site['description']),
                             canonical=e(canonical), social_image=e(f'{SITE_URL}/assets/social-card.png'),
                             asset_prefix=e(link('/assets')), schema=json.dumps(person_schema(), ensure_ascii=False).replace('<','\\u003c'),
                             extra_head=extra_head, header=header(active), body=body, footer=footer(), body_class=e(body_class))
    destination.write_text(markup, encoding='utf-8')
    if route != '404.html':
        pages.append(route)


def portrait(eager: bool = False) -> str:
    return f'''<img class="portrait" src="{link('/assets/sikao-guo-480.webp')}" srcset="{link('/assets/sikao-guo-480.webp')} 480w, {link('/assets/sikao-guo-800.webp')} 800w" sizes="180px" alt="Portrait of Sikao Guo wearing a blue checked shirt" width="800" height="800" loading="{'eager' if eager else 'lazy'}" decoding="async"{' fetchpriority="high"' if eager else ''}>'''


class Sections:
    """Numbered section labels: 01, 02, ... in copper, continuing within a page."""
    def __init__(self) -> None:
        self.n = 0

    def __call__(self, title: str, body: str, id_: str = '', links: str = '', note: str = '', label_tag: str = 'h2') -> str:
        self.n += 1
        anchor = f' id="{e(id_)}"' if id_ else ''
        extra = f'<div class="label-links">{links}</div>' if links else ''
        note_html = f'<p class="section-note">{note}</p>' if note else ''
        return f'<section class="section"{anchor}><div class="section-label"><span class="section-number">{self.n:02d}</span><{label_tag}>{e(title)}</{label_tag}>{extra}</div>{note_html}{body}</section>'


def intro_strip(title: str, lede: str = '', extra: str = '', crumb: str = '') -> str:
    crumb_html = f'<p class="breadcrumb">{crumb}</p>' if crumb else ''
    lede_html = f'<p class="lede">{e(lede)}</p>' if lede else ''
    return f'<div class="intro-strip">{crumb_html}<h1>{e(title)}</h1>{lede_html}{extra}</div>'


def topics_strip() -> str:
    topics = ''.join(f'<li>{e(t)}</li>' for t in site['focus'])
    return f'<div class="intro-strip"><h1>{e(site["name"])}</h1><p class="lede">{e(site["title"])}</p><ul class="topics" aria-label="Research focus">{topics}</ul><div class="link-row"><a href="mailto:{e(site["email"])}">{e(site["email"])}</a>{social_links()}</div></div>'


def home() -> str:
    s = Sections()
    contact = f'<div class="link-row"><a href="mailto:{e(site["email"])}">{e(site["email"])}</a>{social_links()}</div>'
    return f'''<div class="shell">{topics_strip()}
{s('Summary', f'<div class="bio-grid">{portrait(eager=True)}<div class="prose"><p>{e(site["summary"])}</p></div></div>', id_='summary')}
{s('Experience', experience(), id_='experience')}
{s('Education', education(), id_='education')}
{s('Contact', contact, id_='contact')}</div>'''


def cv_items(rows: list[tuple[str,str,str,list[str]]]) -> str:
    out = []
    for date, title, sub, bullets in rows:
        ul = ('<ul class="cv-list">' + ''.join(f'<li>{e(b)}</li>' for b in bullets) + '</ul>') if bullets else ''
        out.append(f'<article class="cv-item"><div class="cv-date">{e(date)}</div><div><h3 class="cv-title">{e(title)}</h3>{sub}{ul}</div></article>')
    return ''.join(out)


def experience() -> str:
    rows = []
    for x in site['experience']:
        roles = x['roles']
        if len(roles) == 1:
            role_html = f'<p class="cv-sub">{e(roles[0][0])}</p>'
        else:
            role_html = ''.join(f'<p class="cv-sub">{e(r)} · {e(d)}</p>' for r, d in roles)
        sub = role_html + f'<p class="cv-sub">{e(x["location"])}</p>'
        rows.append((x['period'], x['organization'], sub, x['highlights']))
    return cv_items(rows)


def education() -> str:
    return cv_items([(x['period'], x['degree'], f'<p class="cv-sub">{e(x["institution"])}</p>', []) for x in site['education']])


def main() -> None:
    for path in (STAGING, OUT):
        if path.is_symlink():
            raise SystemExit(f'Refusing to replace a symlink: {path}')
    if STAGING.exists(): shutil.rmtree(STAGING)
    STAGING.mkdir()
    shutil.copytree(SRC/'assets',STAGING/'assets')
    for filename in ('styles.css','site.js','init.js'):
        shutil.copyfile(SRC/filename,STAGING/'assets'/filename)
    write_page('',site['title'],home(),body_class='home')
    write_page('404.html','Page not found','<div class="shell">'+intro_strip('404: not found','This page has moved or does not exist.','<div class="link-row">'+text_link('/','home')+'</div>')+'</div>',extra_head='<meta name="robots" content="noindex">')
    urls=''.join(f'<url><loc>{xml_escape(SITE_URL+"/"+route)}</loc></url>' for route in pages)
    (STAGING/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
    (STAGING/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    (STAGING/'.nojekyll').write_text('')
    if OUT.exists(): shutil.rmtree(OUT)
    STAGING.rename(OUT)
    print(f'Built {len(pages)} page(s) + 404 and local assets in {OUT}')


if __name__=='__main__':
    main()
