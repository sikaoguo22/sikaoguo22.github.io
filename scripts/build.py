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
import re
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
publications = load_json('publications')
by_pub = {p['id']: p for p in publications}
if len(by_pub) != len(publications):
    raise SystemExit('Publication IDs must be unique.')
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


NAV = [('Home', '/'), ('Publications', '/publications/'), ('CV', '/cv/')]


def header(active: str) -> str:
    nav = ''.join(f'<a href="{e(link(href))}"' + (' aria-current="page"' if active == label else '') + f'>{label}</a>' for label, href in NAV)
    return f'''<header class="site-header"><div class="shell header-inner">
<a class="wordmark" href="{link('/')}" aria-label="Sikao Guo, home">Sikao Guo</a>
<nav class="primary-nav" id="primary-navigation" aria-label="Main navigation">{nav}</nav></div></header>'''


def social_links(keys=(('scholar', 'Scholar'), ('github', 'GitHub'), ('linkedin', 'LinkedIn'), ('orcid', 'ORCID'))) -> str:
    return ''.join(external(site['social'][k], label) for k, label in keys)


def footer() -> str:
    return f'''<footer class="site-footer"><div class="shell footer-inner"><span>© 2026 Sikao Guo · Computational biophysics &amp; scientific software</span><div class="footer-links"><a href="mailto:{e(site['email'])}">{e(site['email'])}</a>{social_links()}<button class="text-button js-only" type="button" data-drift-toggle aria-pressed="false">Pause background</button></div></div></footer>'''


def person_schema() -> dict[str, Any]:
    return {'@context':'https://schema.org', '@type':'Person', 'name':site['shortName'],
            'url':f'{SITE_URL}/', 'image':f'{SITE_URL}/assets/sikao-guo-800.webp',
            'description':site['description'], 'jobTitle':'Research Engineer',
            'worksFor':{'@type':'Organization','name':'Inria'},
            'sameAs':list(site['social'].values()),
            'knowsAbout':['Computational biophysics','Protein conformational sampling','Biomolecular self-assembly','Scientific software','High-performance computing']}


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
    return f'<div class="intro-strip"><h1 class="sr-only">{e(site["name"])}, {e(site["title"])}</h1><ul class="topics" aria-label="Research focus">{topics}</ul><div class="link-row">{social_links()}<a href="mailto:{e(site["email"])}">Email</a></div></div>'


ME = ('Guo, S.-K.', 'Guo, S.')


def mark_me(authors: str) -> str:
    out = e(authors)
    for name in ME:
        if name in authors:
            return out.replace(e(name), f'<span class="me">{e(name)}</span>', 1)
    return out


def publication(pub: dict[str,Any], full: bool = False) -> str:
    kind = 'preprint' if pub['type'] == 'Preprint' else 'journal'
    flags = []
    if kind == 'preprint': flags.append('preprint')
    if pub.get('firstAuthor'): flags.append('first author')
    flag_html = (' <span class="flag">· ' + ' · '.join(flags) + '</span>') if flags else ''
    search = ' '.join([pub['title'],pub['authors'],pub['venue'],str(pub['year']),*pub['topics']])
    extra = f'<p class="publication-contribution">Contribution: {e(pub["contribution"])}</p>' if full and pub.get('contribution') else ''
    doi = pub.get('doi')
    links = external(pub['url'], 'arXiv' if 'arxiv' in pub['url'] else 'DOI') if doi else external(pub['url'], 'Link')
    if full:
        links += f'<details class="bibtex"><summary>BibTeX</summary><pre>{e(bibtex(pub))}</pre></details>'
    return f'''<article class="publication" id="{e(pub['id'])}" data-publication data-type="{kind}" data-year="{pub['year']}" data-search="{e(search)}"><h3 class="publication-title"><a href="{e(pub['url'])}" target="_blank" rel="noopener noreferrer">{e(pub['title'])}</a></h3><p class="publication-authors">{mark_me(pub['authors'])}</p><p class="publication-venue">{e(pub['venue'])} {e(pub['citation'])}, {pub['year']}{flag_html}</p>{extra}<div class="publication-links">{links}</div></article>'''


def home() -> str:
    s = Sections()
    bio = ''.join(f'<p>{para}</p>' for para in site['bio'])
    selected = ''.join(publication(by_pub[key]) for key in ['gui-framework-2026','parallel-nerdss-2025','hiv-2023','clathrin-2022'])
    pub_links = text_link('/publications/', f'all {len(publications)} publications') + external(site['social']['scholar'], 'Google Scholar')
    return f'''<div class="shell">{topics_strip()}
{s('Short Bio', f'<div class="bio-grid">{portrait(eager=True)}<div class="prose">{bio}<p>{text_link("/cv/","View CV")}</p></div></div>')}
{s('Selected Publications', f'<div class="publication-list">{selected}</div>', links=pub_links)}
{s('Contact', f'<div class="prose"><p>I am interested in molecular-modeling methods, biomolecular simulation, and reusable scientific software. Reach me at <a href="mailto:{e(site["email"])}">{e(site["email"])}</a>.</p></div>')}</div>'''


def publications_page() -> str:
    s = Sections()
    years = sorted({p['year'] for p in publications}, reverse=True)
    groups = []
    for y in years:
        items = [p for p in publications if p['year'] == y]
        groups.append(f'<details class="year-group" open data-year-group><summary>{y} <span class="year-count" data-year-count>{len(items)} publication{"s" if len(items)!=1 else ""}</span></summary>{"".join(publication(p, True) for p in items)}</details>')
    journals = sum(p['type'] != 'Preprint' for p in publications)
    tools = f'<div class="pub-tools"><span data-result-count role="status" aria-live="polite">{len(publications)} publications · {journals} peer-reviewed, {len(publications)-journals} preprints</span><a href="{link("/citations/publications.bib")}">Download BibTeX</a></div>'
    filters = '''<div class="filters js-only"><label class="field field-search">Search<input type="search" data-publication-search placeholder="Titles, authors, venues" autocomplete="off"></label><label class="field field-select">Type<select data-publication-filter><option value="all">All</option><option value="journal">Peer-reviewed</option><option value="preprint">Preprints</option></select></label></div>'''
    links = external(site['social']['scholar'], 'Google Scholar') + external(site['social']['orcid'], 'ORCID')
    body = tools + filters + ''.join(groups) + '<p class="empty-state" data-empty-state hidden>No publications match this search.</p>'
    return f'<div class="shell">{intro_strip("Publications")}{s("Publications", body, links=links)}</div>'


def cv_items(rows: list[tuple[str,str,str,list[str]]]) -> str:
    out = []
    for date, title, sub, bullets in rows:
        ul = ('<ul class="cv-list">' + ''.join(f'<li>{e(b)}</li>' for b in bullets) + '</ul>') if bullets else ''
        out.append(f'<article class="cv-item"><div class="cv-date">{e(date)}</div><div><h3 class="cv-title">{e(title)}</h3>{sub}{ul}</div></article>')
    return ''.join(out)


def experience() -> str:
    rows = []
    for x in site['experience']:
        sub = f'<p class="cv-sub">{e(x["role"])}</p><p class="cv-sub">{e(x["location"])}</p>' + (f'<p class="cv-sub">{e(x["supervisor"])}</p>' if x.get('supervisor') else '')
        rows.append((x['period'], x['organization'], sub, x['highlights']))
    return cv_items(rows)


def education() -> str:
    return cv_items([(x['period'], x['degree'], f'<p class="cv-sub">{e(x["institution"])}</p>' + (f'<p class="cv-sub">{e(x["detail"])}</p>' if x.get('detail') else ''), []) for x in site['education']])


def ref(n: str, pub: dict[str, Any]) -> str:
    return f'<li><span>{e(n)}</span><span>{mark_me(pub["authors"])} ({pub["year"]}). <a class="ref-title" href="{e(pub["url"])}" target="_blank" rel="noopener noreferrer">{e(pub["title"])}</a>. <span class="ref-venue">{e(pub["venue"])}</span> {e(pub["citation"])}.</span></li>'


def cv_page() -> str:
    s = Sections()
    journals = [p for p in publications if p['type'] != 'Preprint']
    preprints = [p for p in publications if p['type'] == 'Preprint']
    pubs = (f'<h3 class="cv-subhead">Peer-reviewed publications</h3><ol class="ref-list">{"".join(ref(str(i+1), p) for i, p in enumerate(journals))}</ol>'
            f'<h3 class="cv-subhead">Preprints</h3><ol class="ref-list">{"".join(ref("P"+str(i+1), p) for i, p in enumerate(preprints))}</ol>'
            f'<h3 class="cv-subhead">Manuscript in preparation</h3><ol class="ref-list"><li><span>M1</span><span>{mark_me(site["inPreparation"])}</span></li></ol>')
    talks = ''.join(f'<h3 class="cv-subhead">{e(kind)}</h3>' + cv_items([(y, t, f'<p class="cv-sub">{e(v)}</p>', []) for y, t, v in rows]) for kind, rows in site['presentations'].items())
    contact = f'<div class="link-row"><a href="mailto:{e(site["email"])}">{e(site["email"])}</a>{social_links()}</div>'
    return f'''<div class="shell cv-content">{intro_strip(site['name'], 'Curriculum vitae', contact)}{s('Research Focus', f'<div class="prose"><p>{e(site["focusText"])}</p></div>')}{s('Research Appointments', experience())}{s('Education', education())}{s('Publications', pubs, links=text_link('/publications/','with BibTeX'))}{s('Presentations', talks)}</div>'''


def bibtex(pub: dict[str,Any]) -> str:
    """Generate minimal citations from supplied metadata without inventing fields."""
    # Authors are stored CV-style ("Guo, S., Sodt, A. J., and Johnson, M. E."): each name ends with an initial.
    authors = pub['authors'].replace(', and ', ', ').replace(' and ', ', ')
    names = [x.strip() for x in re.split(r'(?<=\.),\s+', authors)]
    author_text = ' and '.join(names)
    kind='misc' if pub['type']=='Preprint' else 'article'
    fields={'title':'{'+pub['title']+'}', 'author':author_text, 'year':str(pub['year']), 'url':pub['url']}
    if kind=='article': fields['journal']=pub['venue']
    else: fields['note']='Preprint, '+pub['venue']
    if pub.get('doi'): fields['doi']=pub['doi']
    rows=',\n'.join(f'  {key} = {{{value}}}' for key,value in fields.items())
    return f'@{kind}{{{pub["id"]},\n{rows}\n}}\n'


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
    write_page('publications/','Publications',publications_page(),active='Publications')
    write_page('cv/','CV',cv_page(),active='CV',body_class='cv-page')
    write_page('404.html','Page not found','<div class="shell">'+intro_strip('404: not found','This page has moved or does not exist.','<div class="link-row">'+text_link('/','home')+'</div>')+'</div>',extra_head='<meta name="robots" content="noindex">')
    citations=STAGING/'citations'; citations.mkdir()
    for pub in publications: (citations/(pub['id']+'.bib')).write_text(bibtex(pub),encoding='utf-8')
    (citations/'publications.bib').write_text('\n'.join(bibtex(p) for p in publications),encoding='utf-8')
    urls=''.join(f'<url><loc>{xml_escape(SITE_URL+"/"+route)}</loc></url>' for route in pages)
    (STAGING/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
    (STAGING/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    (STAGING/'.nojekyll').write_text('')
    if OUT.exists(): shutil.rmtree(OUT)
    STAGING.rename(OUT)
    print(f'Built {len(pages)} pages + 404, {len(publications)} citations, and local assets in {OUT}')


if __name__=='__main__':
    main()
