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
projects = load_json('projects')
publications = load_json('publications')
software = load_json('software')
by_slug = {p['slug']: p for p in projects}
by_pub = {p['id']: p for p in publications}
if len(by_slug) != len(projects) or len(by_pub) != len(publications):
    raise SystemExit('Project slugs and publication IDs must be unique.')
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


def arrow(diagonal: bool = False) -> str:
    return f'<span class="arrow" aria-hidden="true">{"↗" if diagonal else "→"}</span>'


def external(href: str, label: str, cls: str = '') -> str:
    return f'<a class="{e(cls)}" href="{e(href)}" target="_blank" rel="noopener noreferrer">{e(label)} {arrow(True)}</a>'


def icon(name: str) -> str:
    shapes = {
        'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
        'theme': '<circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 1 0 16Z" fill="currentColor"/>',
        'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
        'email': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    }
    return f'<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{shapes[name]}</svg>'


def button(href: str, label: str, primary: bool = False) -> str:
    cls = 'button button-primary' if primary else 'button'
    return f'<a class="{cls}" href="{e(link(href))}">{e(label)}{arrow()}</a>'


def text_link(href: str, label: str) -> str:
    return f'<a class="text-link" href="{e(link(href))}">{e(label)}{arrow()}</a>'


def header(active: str) -> str:
    items = [('Research', '/research/'), ('Software', '/software/'), ('Publications', '/publications/'), ('About', '/about/'), ('CV', '/cv/')]
    nav = ''.join(f'<a href="{e(link(href))}"' + (' aria-current="page"' if active == label else '') + f'>{label}</a>' for label, href in items)
    return f'''<header class="site-header"><div class="container header-inner">
<a class="brand" href="{link('/')}" aria-label="Sikao Guo, home"><span class="brand-mark" aria-hidden="true">SG</span><span>Sikao Guo</span></a>
<nav class="primary-nav" id="primary-navigation" aria-label="Main navigation">{nav}</nav>
<div class="header-actions"><a class="button button-small header-contact" href="mailto:{e(site['email'])}">Get in touch</a>
<button class="icon-button js-only" type="button" data-theme-toggle aria-label="Switch color theme" aria-pressed="false">{icon('theme')}</button>
<button class="icon-button menu-toggle" type="button" data-menu-toggle aria-controls="primary-navigation" aria-expanded="false" aria-label="Open navigation">{icon('menu')}</button></div></div></header>'''


def footer() -> str:
    social_links = ''.join(external(site['social'][name], label) for name, label in [('github','GitHub'),('scholar','Scholar'),('linkedin','LinkedIn'),('orcid','ORCID')])
    return f'''<footer class="site-footer"><div class="container footer-inner"><div class="footer-identity"><strong>Sikao Guo, Ph.D.</strong>Computational biophysics &amp; scientific software · © 2026</div><div class="footer-links">{social_links}<a href="mailto:{e(site['email'])}">Email</a></div></div></footer>'''


def contact() -> str:
    return f'''<section class="contact-section" aria-labelledby="contact-title"><div class="container contact-inner"><div><p class="eyebrow">Research &amp; collaboration</p><h2 id="contact-title">Let’s talk about the next question.</h2><p>I’m interested in molecular-modeling methods, biomolecular simulation, and reusable scientific software.</p></div><a class="button" href="mailto:{e(site['email'])}">{icon('email')}{e(site['email'])}</a></div></section>'''


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


def portrait(cls: str = 'portrait-card', eager: bool = False) -> str:
    return f'''<figure class="{cls}"><img src="{link('/assets/sikao-guo-480.webp')}" srcset="{link('/assets/sikao-guo-480.webp')} 480w, {link('/assets/sikao-guo-800.webp')} 800w" sizes="(max-width: 600px) 310px, 360px" alt="Sikao Guo, wearing a blue checked shirt, outdoors" width="800" height="800" loading="{'eager' if eager else 'lazy'}" decoding="async" {'fetchpriority="high"' if eager else ''}><figcaption class="portrait-caption"><div><strong>Sikao Guo, Ph.D.</strong><p>Research Engineer · Inria</p></div><span class="initials" aria-hidden="true">SG</span></figcaption></figure>'''


def diagram(kind: str) -> str:
    """UI schematics. They intentionally do not imply measured or sampled data."""
    if kind == 'autoclip':
        body = '<div class="diagram-label">Application definition</div><div class="specification">Validated JSON</div><div class="diagram-stem"></div><div class="targets"><span>PyMOL</span><span>VMD</span><span>Web</span></div>'
        label = 'One specification to three interfaces'
    elif kind == 'mpi':
        domain = '<div class="mpi-domain" aria-hidden="true">' + '<i></i>'*4 + '</div>'
        body = '<div class="diagram-label">Spatial domain decomposition</div><div class="mpi-grid">' + domain*4 + '</div>'
        label = 'Communicating simulation domains'
    elif kind == 'pipeline':
        body = '<div class="diagram-label">Structure-to-simulation workflow</div><div class="pipeline"><div class="pipeline-step"><strong>PDB / mmCIF</strong>Structures</div>'+arrow()+'<div class="pipeline-step"><strong>CG model</strong>Reactions</div>'+arrow()+'<div class="pipeline-step"><strong>NERDSS</strong>Simulation</div></div>'
        label = 'Model construction and simulation'
    elif kind == 'sampling':
        body = '''<div class="diagram-label">Flexible-endpoint sampling</div><svg class="sampling-svg" viewBox="0 0 340 130" fill="none" aria-hidden="true"><path d="M22 101C57 37 85 112 116 56S176 96 210 38 261 89 316 33" stroke="currentColor" stroke-width="3"/><path d="M22 101C78 68 63 6 116 56S181 121 210 38 281 21 315 61" stroke="currentColor" opacity=".27" stroke-width="2.5"/><path d="M22 101C63 122 66 59 116 56S187 17 210 38 283 123 309 89" stroke="currentColor" opacity=".15" stroke-width="2.5"/><g fill="var(--surface)" stroke="currentColor" stroke-width="2"><circle cx="22" cy="101" r="5"/><circle cx="116" cy="56" r="5"/><circle cx="210" cy="38" r="5"/><circle cx="316" cy="33" r="5"/></g></svg>'''
        label = 'Conceptual paths · not sampled structures'
    elif kind == 'assembly':
        cluster = '<i></i>'*6
        body = f'<div class="diagram-label">Interactions → assembly → remodeling</div><div class="assembly-flow" aria-hidden="true"><div class="assembly-cluster loose">{cluster}</div><span class="arrow">⇄</span><div class="assembly-cluster">{cluster}</div></div>'
        label = 'Conceptual assembly · not simulation output'
    else:
        raise ValueError(f'Unknown diagram type: {kind}')
    return f'<figure class="diagram">{body}<figcaption>{e(label)} · schematic</figcaption></figure>'


def section_heading(eyebrow: str, title: str, more: tuple[str,str] | None = None, intro: str = '') -> str:
    return f'<div class="section-title-row"><div><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2>' + (f'<p class="section-intro">{e(intro)}</p>' if intro else '') + '</div>' + (text_link(*more) if more else '') + '</div>'


def tags(values: list[str]) -> str:
    return '<ul class="tags" aria-label="Methods and technologies">' + ''.join(f'<li>{e(x)}</li>' for x in values) + '</ul>'


def software_card(item: dict[str, Any]) -> str:
    resources = external(item['code'],'Code') + external(item['docs'],'Docs') + f'<a href="{link("/projects/"+item["slug"]+"/")}">Case study {arrow()}</a>'
    return f'''<article class="software-card">{diagram(item['visual'])}<div class="software-card-body"><h3>{e(item['name'])}</h3><div class="language-line">{e(item['language'])}</div><p>{e(item['description'])}</p><p class="evidence">{e(item['evidence'])}</p><div class="card-links">{resources}</div></div></article>'''


def publication(pub: dict[str,Any], full: bool = False) -> str:
    kind = 'preprint' if pub['type'] == 'Preprint' else 'journal'
    first = '<span class="badge">First author</span>' if pub.get('firstAuthor') else ''
    type_badge = f'<span class="badge {"badge-preprint" if kind=="preprint" else ""}">{e(pub["type"])}</span>'
    author = e(pub['authors']).replace('Sikao Guo','<strong>Sikao Guo</strong>').replace('Si-Kao Guo','<strong>Si-Kao Guo</strong>')
    citation = f'{pub["authors"]} ({pub["year"]}). {pub["title"]}. {pub["venue"]}, {pub["citation"]}. {pub["url"]}'
    search = ' '.join([pub['title'],pub['authors'],pub['venue'],str(pub['year']),*pub['topics']])
    extra = f'<p class="publication-contribution"><strong>My contribution:</strong> {e(pub["contribution"])}</p>' if full and pub.get('contribution') else ''
    resources = external(pub['url'], 'Read preprint' if kind=='preprint' else 'Read paper')
    if full:
        resources += f'<a href="{link("/citations/"+pub["id"]+".bib")}" download>BibTeX ↓</a><button class="link-button js-only" type="button" data-copy-citation="{e(citation)}">Copy citation</button>'
    return f'''<article class="publication" id="{e(pub['id'])}" data-publication data-type="{kind}" data-search="{e(search)}"><div class="publication-year">{pub['year']}</div><div class="publication-body"><div class="publication-meta"><span>{e(pub['venue'])}</span>{type_badge}{first}</div><h3><a href="{e(pub['url'])}" target="_blank" rel="noopener noreferrer">{e(pub['title'])}</a></h3><p class="publication-authors">{author}</p>{extra}<div class="publication-actions">{resources}</div></div></article>'''


def page_intro(eyebrow: str, title: str, text: str, extra: str = '') -> str:
    return f'<section class="container page-intro"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1><p class="lede">{e(text)}</p>{extra}</section>'


def home() -> str:
    hero = site['hero']
    socials = ''.join(external(site['social'][key],label) for key,label in [('github','GitHub'),('scholar','Scholar'),('linkedin','LinkedIn')])
    stats = ''.join(f'<a class="stat" href="{link(x["href"])}"><span class="stat-value">{e(x["value"])}</span><span class="stat-label">{e(x["label"])}</span><span class="stat-detail">{e(x["detail"])}</span></a>' for x in site['stats'])
    themes = ''.join(f'<article class="theme-card"><div class="theme-top"><span class="theme-number">0{i+1}</span><span class="theme-tag">{e(x["tag"])}</span></div><h3>{e(x["question"])}</h3><p>{e(x["text"])}</p>{text_link(x["href"],x["title"])}</article>' for i,x in enumerate(site['researchThemes']))
    selected = ''.join(publication(by_pub[key]) for key in ['gui-framework-2026','parallel-nerdss-2025','hiv-2023'])
    return f'''<div class="container"><section class="hero" aria-labelledby="hero-title"><div><p class="hero-name">{e(site['name'])}</p><p class="eyebrow">{e(hero['eyebrow'])}</p><h1 id="hero-title"><span>{e(hero['title'][0])}</span><span>{e(hero['title'][1])}</span></h1><p class="hero-description">{e(hero['text'])}</p><div class="button-row">{button('/research/','Explore research',True)}{button('/software/','View software')}</div><p class="hero-tech">Protein modeling · C++ / Python · High-performance computing</p><div class="hero-socials">{socials}</div></div>{portrait(eager=True)}</section><section class="stats" aria-label="Selected, benchmark-specific results">{stats}</section>
<section class="section" aria-label="Research directions">{section_heading('Research directions','Questions that drive my work.',('/research/','Research overview'))}<div class="theme-grid">{themes}</div></section></div>
<section class="soft-section"><div class="container">{section_heading('Open-source software','Methods you can build on.',('/software/','All software'))}<div class="software-grid">{''.join(software_card(x) for x in software)}</div></div></section>
<div class="container"><section class="section">{section_heading('Selected publications','From methods to mechanisms.',('/publications/','Papers & preprints'))}<div class="publication-list">{selected}</div></section>
<section class="section"><div class="about-strip"><div><p class="eyebrow">About me</p><h2>Physics, biological questions, and the software in between.</h2></div><div><p>My work has grown from mechanochemical models of molecular motors to biomolecular self-assembly, parallel simulation, and protein conformational sampling. Across these problems, I connect method development with numerical validation and reusable software.</p>{text_link('/about/','More about my background')}</div></div></section></div>{contact()}'''


def project_card(p: dict[str,Any]) -> str:
    fragment = {'inverse-kinematics-backbone-sampling':'current-research',
                'mechanistic-assembly-models':'biomolecular-assembly',
                'nerdss-ionerdss-infrastructure':'research-infrastructure',
                'cross-platform-gui-generation':'research-software'}[p['slug']]
    return f'''<article class="project-card" id="{fragment}">{diagram(p['visual'])}<div class="project-card-body"><p class="eyebrow">{e(p['category'])} · {e(p['status'])}</p><h2><a href="{link('/projects/'+p['slug']+'/')}">{e(p['shortTitle'])}</a></h2><p>{e(p['summary'])}</p>{tags(p['tags'])}{text_link('/projects/'+p['slug']+'/','Explore the work')}</div></article>'''


def research_page(all_projects: bool = False) -> str:
    intro = page_intro('Research portfolio' if all_projects else 'Research', 'Methods, mechanisms, and reusable tools.' if all_projects else 'Understanding proteins through computation.', 'Selected projects in protein conformational sampling, biomolecular self-assembly, and scientific software.' if all_projects else 'I connect molecular models, stochastic simulation, and structural data to study how proteins explore conformations and organize into functional assemblies.')
    chosen = projects if all_projects else [by_slug['inverse-kinematics-backbone-sampling'],by_slug['mechanistic-assembly-models']]
    infrastructure = '' if all_projects else f'''<section class="section"><div class="about-strip"><div><p class="eyebrow">Methods that support the science</p><h2>Models need reliable computational tools.</h2></div><div><p>NERDSS-MPI, ioNERDSS, and AutoCLIP connect simulation, automated model construction, and scientist-facing interfaces. Validation, testing, and documentation are part of the method—not an afterthought.</p>{text_link('/software/','Explore the software')}</div></div></section>'''
    return intro + f'<div class="container"><section class="section"><div class="project-grid">{"".join(project_card(p) for p in chosen)}</div></section>{infrastructure}</div>' + contact()


def software_page() -> str:
    rows=[]
    for item in software:
        resources = external(item['code'],'Source code') + external(item['docs'],'Documentation') + external(item['paper'],'Paper / preprint')
        rows.append(f'''<article class="software-detail" id="{e(item['name'].lower())}">{diagram(item['visual'])}<div><p class="eyebrow">{e(item['language'])}</p><h2>{e(item['name'])}</h2><p class="description">{e(item['description'])}</p><p class="evidence">{e(item['evidence'])}</p><div class="card-links">{resources}<a href="{link('/projects/'+item['slug']+'/')}">Case study {arrow()}</a></div></div></article>''')
    return page_intro('Software','Research methods. Usable implementations.','Open-source tools spanning molecular structures, parallel simulation, and consistent scientific interfaces. Each project links to its code, documentation, and underlying work.') + f'<div class="container"><section class="section" id="research-software">{"".join(rows)}</section><section class="section"><div class="about-strip"><div><p class="eyebrow">Engineering approach</p><h2>Correctness first. Reuse by design.</h2></div><div><p>I work across algorithm development, numerical validation, APIs, tests, packaging, documentation, and deployment. My aim is to make a research method useful outside the codebase and context in which it was developed.</p>{text_link("/projects/","Read the project case studies")}</div></div></section></div>' + contact()


def publications_page() -> str:
    extra = '<div class="button-row">'+external(site['social']['scholar'],'Full publication list on Scholar','button')+button('/citations/selected-publications.bib','Selected BibTeX')+'</div>'
    filters = f'''<div class="js-only"><div class="filters"><div class="filter-buttons" role="group" aria-label="Filter publications by publication type"><button class="filter-button" type="button" data-publication-filter="all" aria-pressed="true">All selected work</button><button class="filter-button" type="button" data-publication-filter="journal" aria-pressed="false">Journal articles</button><button class="filter-button" type="button" data-publication-filter="preprint" aria-pressed="false">Preprints</button></div><label class="search-field">{icon('search')}<span class="sr-only">Search selected publications</span><input type="search" data-publication-search placeholder="Title, author, topic, or year…" autocomplete="off"></label></div><p class="result-count" data-result-count role="status" aria-live="polite">{len(publications)} selected publications</p></div>'''
    return page_intro('Publications','The science behind the software.','Selected journal articles and preprints. First-author contributions are identified explicitly; the complete publication record is available on Google Scholar.',extra) + f'<div class="container"><section class="section">{filters}<div class="publication-list">{"".join(publication(p,True) for p in publications)}</div><p class="empty-state" data-empty-state hidden>No publications match this search. Try a different term or select all work.</p><p class="sr-only" data-copy-status role="status" aria-live="polite"></p></section></div>'


def timeline(full: bool = False) -> str:
    parts=[]
    for item in site['experience']:
        details = '<ul class="prose-list">' + ''.join(f'<li>{e(x)}</li>' for x in item['highlights']) + '</ul>' if full else f'<p class="timeline-summary">{e(item["summary"])}</p>'
        parts.append(f'<article class="timeline-item"><div class="timeline-date">{e(item["period"])}</div><div><h3>{e(item["organization"])}</h3><p class="timeline-role">{e(item["role"])}</p><p class="timeline-location">{e(item["location"])}</p>{details}</div></article>')
    return '<div class="timeline">' + ''.join(parts) + '</div>'


def education() -> str:
    return ''.join(f'<article class="school"><div><h3>{e(item["degree"])}</h3><p>{e(item["institution"])}</p></div><span class="period">{e(item["period"])}</span></article>' for item in site['education'])


def about_page() -> str:
    return page_intro('About','A physicist working on biological questions.','I’m Sikao Guo, a computational biophysicist and research software engineer. I develop methods to study molecular systems and the software that makes those methods usable.') + f'''<div class="container"><section class="section about-layout"><div class="about-copy"><p>At <strong>Inria</strong>, I work on protein conformational sampling and structural-validation workflows. I also created AutoCLIP, a framework for generating consistent scientific applications for PyMOL, VMD, and the web.</p><p>Previously, at <strong>Johns Hopkins University</strong>, I studied clathrin and HIV lattice assembly, developed MPI-based reaction-diffusion simulation, and built automated structure-to-simulation workflows.</p><p>My Ph.D. research at the <strong>Institute of Physics, Chinese Academy of Sciences</strong> focused on mechanochemical models of kinesin. That background in physics continues to shape how I connect molecular interactions with observable biological behavior.</p><p>Across these projects, I work from the scientific question through the algorithm, numerical validation, software interfaces, tests, and documentation.</p><div class="button-row">{button('/cv/','CV',True)}{button('mailto:'+site['email'],'Get in touch')}</div></div>{portrait('portrait-card', True)}</section><section class="section">{section_heading('Background','Research experience.')}{timeline()}</section><section class="section">{section_heading('Education','Foundations in physics.')}{education()}</section></div>{contact()}'''


def cv_page() -> str:
    intro=page_intro('CV',site['name'],'Computational biophysicist and research software engineer with 6+ years developing methods and reusable software for molecular modeling and high-performance scientific computing.',f'<p class="hero-tech">{e(site["workAuthorization"])}</p>')
    skills=''.join(f'<article class="skill-group"><h3>{e(x["title"])}</h3><p>{e(" · ".join(x["items"]))}</p></article>' for x in site['skills'])
    pubs=''.join(publication(by_pub[k]) for k in ['parallel-nerdss-2025','hiv-2023','clathrin-2022'])
    return intro + f'<div class="container cv-content"><section class="section">{section_heading("Experience","Research & software development.")}{timeline(True)}</section><section class="section">{section_heading("Education","Academic training.")}{education()}</section><section class="section">{section_heading("Methods & tools","Technical strengths.")}<div class="skill-grid">{skills}</div></section><section class="section">{section_heading("Selected first-author publications","Research contributions.",("/publications/","More publications"))}<div class="publication-list">{pubs}</div></section></div>'


def case_page(p: dict[str, Any]) -> str:
    resources=''.join(external(x['href'],x['label']) for x in p['links'])
    if not resources:
        resources='<p class="muted">Ongoing research; no public release linked.</p>'
    intro=f'''<section class="container page-intro case-header"><p class="breadcrumb"><a href="{link('/projects/')}">Projects</a> <span aria-hidden="true">/</span> {e(p['shortTitle'])}</p><p class="eyebrow">{e(p['category'])}</p><h1>{e(p['title'])}</h1><p class="lede">{e(p['summary'])}</p><div class="case-meta"><span class="badge">{e(p['status'])}</span><span>{e(p['period'])}</span></div></section>'''
    side=f'''<aside class="case-sidebar" aria-label="Project context"><h2>My contribution</h2><p>{e(p['role'])}</p><nav aria-label="On this page"><a href="#context">The question</a><a href="#approach">The approach</a><a href="#contribution">Implementation</a><a href="#outcomes">Results & validation</a></nav><h2>Resources</h2><div class="resource-links" id="resources">{resources}</div></aside>'''
    steps=''.join(f'<li class="step"><span class="step-number">0{i+1}</span><div><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></div></li>' for i,x in enumerate(p['steps']))
    contexts=''.join(f'<p>{e(x)}</p>' for x in p['context'])
    contributions='<ul class="prose-list">'+''.join(f'<li>{e(x)}</li>' for x in p['contributions'])+'</ul>'
    outcomes='<ul class="prose-list">'+''.join(f'<li>{e(x)}</li>' for x in p['validation'])+'</ul>'
    note='<p class="notice">This project is ongoing. Comparisons are limited to the evaluated systems; no general superiority claim is implied.</p>' if p['status']=='Ongoing research' else ''
    related=''
    if p['relatedPublications']:
        related='<section class="case-section" id="publications"><h2>Related publications</h2><div class="publication-list">'+''.join(publication(by_pub[k]) for k in p['relatedPublications'])+'</div></section>'
    article=f'''<div><section class="case-section" id="context"><p class="eyebrow">The question</p><h2>{e(p['question'])}</h2>{contexts}</section><section class="case-section" id="approach"><h2>The approach</h2>{diagram(p['visual'])}<ol class="steps">{steps}</ol></section><section class="case-section" id="contribution"><h2>What I developed</h2>{contributions}{tags(p['tags'])}</section><section class="case-section" id="outcomes"><h2>Results &amp; validation</h2>{outcomes}{note}</section>{related}<a class="to-top" href="#main">Back to top ↑</a></div>'''
    return intro + f'<div class="container case-layout">{side}{article}</div>' + contact()


def bibtex(pub: dict[str,Any]) -> str:
    """Generate minimal citations from supplied metadata without inventing fields."""
    authors = pub['authors'].replace(', and ', ', ').replace(' and ', ', ')
    names = [x.strip() for x in authors.split(',')]
    names = ['others' if name == 'et al.' else name for name in names]
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
    for filename in ('styles.css','site.js','theme-init.js'):
        shutil.copyfile(SRC/filename,STAGING/'assets'/filename)
    # Existing research artwork is retained when this update is applied to the repository.
    if (SRC/'images').is_dir(): shutil.copytree(SRC/'images',STAGING/'images')
    write_page('',site['title'],home(),body_class='home')
    write_page('research/','Research',research_page(),active='Research')
    write_page('projects/','Project case studies',research_page(True),active='Research')
    write_page('software/','Open-source software',software_page(),active='Software')
    write_page('publications/','Selected publications & preprints',publications_page(),active='Publications')
    write_page('about/','About',about_page(),active='About')
    write_page('cv/','CV',cv_page(),active='CV',body_class='cv-page')
    for p in projects:
        write_page('projects/'+p['slug']+'/',p['shortTitle'],case_page(p),active='Software' if p['status']=='Open source' else 'Research',description=p['summary'])
    write_page('404.html','Page not found',page_intro('404','This page has moved or does not exist.','Explore the research, software, and publications from the main navigation.', '<div class="button-row">'+button('/','Back to the homepage',True)+'</div>'),extra_head='<meta name="robots" content="noindex">')
    citations=STAGING/'citations'; citations.mkdir()
    for pub in publications: (citations/(pub['id']+'.bib')).write_text(bibtex(pub),encoding='utf-8')
    (citations/'selected-publications.bib').write_text('\n'.join(bibtex(p) for p in publications),encoding='utf-8')
    urls=''.join(f'<url><loc>{xml_escape(SITE_URL+"/"+route)}</loc></url>' for route in pages)
    (STAGING/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
    (STAGING/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    (STAGING/'.nojekyll').write_text('')
    if OUT.exists(): shutil.rmtree(OUT)
    STAGING.rename(OUT)
    print(f'Built {len(pages)} pages + 404, {len(publications)} citations, and local assets in {OUT}')


if __name__=='__main__':
    main()
