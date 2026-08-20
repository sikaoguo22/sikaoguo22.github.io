#!/usr/bin/env python3
"""Build the portfolio as a dependency-free static site.

Edit the JSON files in content/, then run:
    python scripts/build.py

The generated site is written to site/ and can be served or deployed directly.
"""
from __future__ import annotations

import html
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "site"
SITE_URL = os.environ.get("SITE_URL", "https://sikaoguo22.github.io").rstrip("/")

site_data = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
projects: list[dict[str, Any]] = json.loads((CONTENT / "projects.json").read_text(encoding="utf-8"))
publications: list[dict[str, Any]] = json.loads((CONTENT / "publications.json").read_text(encoding="utf-8"))
site = site_data["site"]
navigation = site_data["navigation"]
capabilities = site_data["capabilities"]
impact_stats = site_data["impactStats"]
experience = site_data["experience"]
education = site_data["education"]
skill_groups = site_data["skillGroups"]
open_source_software = site_data["openSourceSoftware"]


def e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def rel(depth: int, path: str) -> str:
    if path.startswith(("http://", "https://", "mailto:", "#")):
        return path
    return ("../" * depth) + path.lstrip("/")


def icon(name: str, size: int = 20) -> str:
    p = {
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "external": '<path d="M14 5h5v5M19 5l-8 8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M18 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" stroke="currentColor" stroke-width="1.7"/>',
        "download": '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 19h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "mail": '<rect x="3.5" y="5.5" width="17" height="13" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="m5 7 7 5.2L19 7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
        "sun": '<circle cx="12" cy="12" r="3.5" stroke="currentColor" stroke-width="1.6"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
        "moon": '<path d="M20 15.3A8.3 8.3 0 0 1 8.7 4a8.3 8.3 0 1 0 11.3 11.3Z" stroke="currentColor" stroke-width="1.7"/>',
        "menu": '<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "close": '<path d="m6 6 12 12M18 6 6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
        "github": '<path fill="currentColor" d="M12 2.7a9.5 9.5 0 0 0-3 18.5c.5.1.7-.2.7-.5v-1.9c-2.8.6-3.4-1.2-3.4-1.2-.5-1.2-1.1-1.5-1.1-1.5-.9-.7.1-.7.1-.7 1 .1 1.6 1.1 1.6 1.1.9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.7-1.4-2.3-.3-4.7-1.1-4.7-5a3.9 3.9 0 0 1 1-2.7c-.1-.3-.4-1.3.1-2.7 0 0 .9-.3 2.8 1a9.7 9.7 0 0 1 5.1 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7a3.9 3.9 0 0 1 1 2.7c0 3.8-2.3 4.7-4.7 5 .4.3.7 1 .7 1.9v2.8c0 .3.2.6.7.5A9.5 9.5 0 0 0 12 2.7Z"/>',
        "linkedin": '<path fill="currentColor" d="M6.2 8.2H3.1V21h3.1V8.2ZM4.6 3A1.8 1.8 0 1 0 4.6 6.6 1.8 1.8 0 0 0 4.6 3ZM20.9 13.7c0-3.9-2.1-5.8-4.9-5.8-2.3 0-3.3 1.3-3.9 2.1V8.2H9V21h3.1v-6.3c0-1.7.3-3.3 2.4-3.3 2 0 2.1 1.9 2.1 3.4V21h3.1l1.2-7.3Z"/>',
        "scholar": '<path fill="currentColor" d="M12 3 1.8 8.5 12 14l8.2-4.4V16h2V8.5L12 3Zm-6.3 9v5.2c0 1.4 2.8 3.3 6.3 3.3s6.3-1.9 6.3-3.3V12L12 15.4 5.7 12Z"/>',
        "orcid": '<circle cx="12" cy="12" r="9" fill="currentColor"/><path d="M8.1 7.2v9.6M10.9 7.2h2.4c3.2 0 5 1.7 5 4.8s-1.8 4.8-5 4.8h-2.4V7.2Z" stroke="var(--paper,white)" stroke-width="1.5"/><circle cx="8.1" cy="5.5" r="1" fill="var(--paper,white)"/>',
    }[name]
    return f'<svg class="icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" aria-hidden="true">{p}</svg>'


def tags(items: list[str], compact: bool = False) -> str:
    cls = "tag-list compact" if compact else "tag-list"
    return f'<ul class="{cls}">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"


def publication_item(pub: dict[str, Any], contribution: bool = False) -> str:
    citation = f" · {e(pub['citation'])}" if pub.get("citation") else ""
    contribution_html = ""
    if contribution and pub.get("contribution"):
        contribution_html = f'<p class="publication-contribution"><strong>Contribution:</strong> {e(pub["contribution"])}</p>'
    doi = f'<a class="doi-link" href="{e(pub["url"])}" target="_blank" rel="noreferrer">doi:{e(pub["doi"])}</a>' if pub.get("doi") else ""
    return f'''<article class="publication-item" data-publication data-year="{pub['year']}">
<div class="publication-year">{pub['year']}</div><div class="publication-main"><div class="publication-type">{e(pub['type'])} · {e(pub['venue'])}{citation}</div>
<h3><a href="{e(pub['url'])}" target="_blank" rel="noreferrer">{e(pub['title'])}{icon('external',16)}</a></h3><p class="publication-authors">{e(pub['authors'])}</p>{contribution_html}
<div class="publication-footer">{tags(pub['topics'])}{doi}</div></div></article>'''


def project_card(project: dict[str, Any], depth: int, index: int) -> str:
    href = rel(depth, f"projects/{project['slug']}/")
    status_cls = project["status"].lower().replace(" ", "-")
    return f'''<article class="project-card reveal" style="--delay:{index*80}ms"><a class="project-card-visual" href="{href}"><img src="{rel(depth,project['visual'])}" alt="{e(project['visualAlt'])}" loading="lazy"><span class="status-chip status-{status_cls}">{e(project['status'])}</span></a><div class="project-card-content"><div class="project-card-meta"><span>{e(project['category'])}</span><span>{e(project['period'])}</span></div><h3><a href="{href}">{e(project['shortTitle'])}</a></h3><p>{e(project['summary'])}</p>{tags(project['tags'][:4],True)}<a class="text-link" href="{href}">Read case study {icon('arrow',18)}</a></div></article>'''


def section_header(eyebrow: str, title: str, description: str) -> str:
    return f'<div class="section-header"><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2><p class="section-description">{e(description)}</p></div>'


def header(depth: int, active: str) -> str:
    desktop = "".join(f'<a class="{"active" if x["label"].lower()==active else ""}" href="{rel(depth,x["href"])}">{e(x["label"])}</a>' for x in navigation)
    mobile = "".join(f'<a class="{"active" if x["label"].lower()==active else ""}" href="{rel(depth,x["href"])}"><span>{e(x["label"])}</span>{icon("arrow")}</a>' for x in navigation)
    return f'''<header class="site-header" data-header><div class="header-inner container-wide"><a class="brand" href="{rel(depth,'/')}"><span class="brand-mark">SG</span><span class="brand-name">Sikao Guo</span></a><nav class="desktop-nav" aria-label="Primary navigation">{desktop}</nav><div class="header-actions"><button class="icon-button theme-toggle" type="button" aria-label="Switch color theme" data-theme-toggle><span class="theme-icon theme-icon-sun">{icon('sun',18)}</span><span class="theme-icon theme-icon-moon">{icon('moon',18)}</span></button><a class="button button-small button-primary header-contact" href="mailto:{e(site['email'])}">Contact</a><button class="icon-button menu-toggle" type="button" aria-label="Open navigation menu" aria-expanded="false" data-menu-toggle><span class="menu-open-icon">{icon('menu')}</span><span class="menu-close-icon">{icon('close')}</span></button></div></div><nav class="mobile-nav" aria-label="Mobile navigation" data-mobile-nav><div class="container-wide mobile-nav-inner">{mobile}<a href="mailto:{e(site['email'])}"><span>Contact</span>{icon('mail')}</a></div></nav></header>'''


def footer(depth: int) -> str:
    s = site["social"]
    return f'''<footer class="site-footer"><div class="container-wide footer-grid"><div class="footer-intro"><a class="footer-brand" href="{rel(depth,'/')}">Sikao Guo</a><p>Computational biophysics, molecular modeling, and reusable scientific software.</p></div><div class="footer-contact"><p class="footer-label">Contact</p><a href="mailto:{e(site['email'])}">{e(site['email'])}</a><span>{e(site['location'])}</span></div><div class="footer-social"><p class="footer-label">Profiles</p><div class="social-links"><a href="{e(s['github'])}" target="_blank" rel="noreferrer" aria-label="GitHub">{icon('github')}</a><a href="{e(s['linkedin'])}" target="_blank" rel="noreferrer" aria-label="LinkedIn">{icon('linkedin')}</a><a href="{e(s['scholar'])}" target="_blank" rel="noreferrer" aria-label="Google Scholar">{icon('scholar')}</a><a href="{e(s['orcid'])}" target="_blank" rel="noreferrer" aria-label="ORCID">{icon('orcid')}</a></div></div></div><div class="container-wide footer-bottom"><span>© {datetime.now().year} Sikao Guo</span><span>Built for clarity, reproducibility, and scientific impact.</span></div></footer>'''


GENERAL_SCRIPT = r'''<script>(()=>{const r=document.documentElement,t=document.querySelector('[data-theme-toggle]'),m=document.querySelector('[data-menu-toggle]'),n=document.querySelector('[data-mobile-nav]'),h=document.querySelector('[data-header]');t?.addEventListener('click',()=>{const x=r.dataset.theme==='dark'?'light':'dark';r.dataset.theme=x;localStorage.setItem('theme',x)});m?.addEventListener('click',()=>{const x=h?.classList.toggle('menu-open')??false;m.setAttribute('aria-expanded',String(x));document.body.classList.toggle('nav-open',x)});n?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{h?.classList.remove('menu-open');m?.setAttribute('aria-expanded','false');document.body.classList.remove('nav-open')}));const o='IntersectionObserver'in window?new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting){en.target.classList.add('is-visible');o.unobserve(en.target)}}),{threshold:.12}):null;document.querySelectorAll('.reveal').forEach(x=>o?o.observe(x):x.classList.add('is-visible'));const u=()=>h?.classList.toggle('scrolled',scrollY>12);u();addEventListener('scroll',u,{passive:true})})();</script>'''


def layout(title: str, description: str, body: str, depth: int, active: str = "", path: str = "", image: str = "/images/og-image.svg", extra_script: str = "", noindex: bool = False) -> str:
    full = f"{title} | Sikao Guo" if title else f"Sikao Guo | {site['title']}"
    canonical = f"{SITE_URL}/{path.lstrip('/')}"
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f'''<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(description)}"><meta name="author" content="Sikao Guo"><meta name="theme-color" content="#f4f2eb">{robots}<link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="{rel(depth,'images/favicon.svg')}"><link rel="stylesheet" href="{rel(depth,'assets/styles.css')}"><meta property="og:type" content="website"><meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE_URL}/{image.lstrip('/')}"><meta name="twitter:card" content="summary_large_image"><title>{e(full)}</title><script>(()=>{{const s=localStorage.getItem('theme');const p=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';document.documentElement.dataset.theme=s||p}})()</script></head><body><a class="skip-link" href="#main-content">Skip to content</a>{header(depth,active)}<main id="main-content">{body}</main>{footer(depth)}{extra_script}{GENERAL_SCRIPT}</body></html>'''


def home() -> str:
    ps = "".join(project_card(p,0,i) for i,p in enumerate(projects))
    pubs = "".join(publication_item(p) for p in [p for p in publications if p["featured"]][:5])
    caps = "".join(f'<article class="capability-card reveal" style="--delay:{i*90}ms"><span class="capability-number">{e(x["number"])}</span><h3>{e(x["title"])}</h3><p>{e(x["description"])}</p></article>' for i,x in enumerate(capabilities))
    stats = "".join(f'<div class="impact-item"><div class="impact-value">{e(x["value"])}<span>{e(x["suffix"])}</span></div><p class="impact-label">{e(x["label"])}</p></div>' for x in impact_stats)
    body = f'''<section class="home-hero"><div class="container-wide hero-grid"><div class="hero-copy reveal is-visible"><p class="hero-kicker">Computational biophysics × scientific software</p><h1>I build reusable tools for <span class="hero-accent">molecular structure</span> and <span class="hero-accent">dynamic</span> research.</h1><p class="hero-lead">C++ and Python systems for protein conformational sampling, biomolecular self-assembly, structural bioinformatics, and high-performance scientific computing.</p><div class="hero-actions"><a class="button button-primary" href="projects/">View selected work {icon('arrow')}</a><a class="button button-secondary" href="documents/Sikao_Guo_PhD_resume.pdf" target="_blank">Download résumé {icon('download')}</a></div><div class="hero-meta"><span>{e(site['affiliation'])}</span><span>{e(site['availability'])}</span><span>{e(site['location'])}</span></div></div><div class="hero-graphic"><img src="images/hero-visual.svg" alt="Abstract diagram connecting molecular structure, simulation, and scientist-facing software"><div class="hero-graphic-caption hero-caption-top"><span class="caption-dot"></span><span>structure → dynamic</span></div><div class="hero-graphic-caption hero-caption-bottom"><span class="caption-dot"></span><span>method → software</span></div></div></div></section>
<section class="section section-muted"><div class="container">{section_header('What I work on','Methods that survive contact with real scientific workflows.','My work spans algorithm design, scientific validation, scalable implementation, and the interfaces researchers use to for research.')}<div class="capability-grid">{caps}</div></div></section>
<section class="section section-dark grid-noise"><div class="container"><div class="impact-strip reveal">{stats}</div></div></section>
<section class="section"><div class="container">{section_header('Selected work','Research methods developed as reusable infrastructure.','Each case study separates the scientific problem, the algorithm or architecture, my contribution, and the evidence used to validate the result.')}<div class="projects-grid">{ps}</div><div class="projects-footer"><a class="button button-secondary" href="projects/">Explore all case studies {icon('arrow')}</a></div></div></section>
<section class="section section-muted"><div class="container">{section_header('Selected publications','Mechanistic modeling, molecular structure and dynamic, and scientific computing.','A focused selection of work in protein assembly, structural workflows, high-performance simulation, and research software.')}<div class="publication-list reveal">{pubs}</div><div class="projects-footer"><a class="button button-secondary" href="publications/">View publication list {icon('arrow')}</a></div></div></section>
<section class="section"><div class="container about-grid"><div class="about-statement"><p class="eyebrow">Background</p><h2>Physics training, biological questions, engineering execution.</h2><p>I work where molecular modeling and software engineering meet: turning research algorithms into maintainable systems that scientists can validate, scale, and reuse.</p></div><div class="about-details"><div class="about-block reveal"><div class="about-block-label">Current</div><div><h3>Research Engineer · Inria</h3><p>Developing inverse-kinematics protein-backbone samplers and a cross-platform framework for automatically generating VMD, PyMOL, and web applications.</p></div></div><div class="about-block reveal"><div class="about-block-label">Previously</div><div><h3>Johns Hopkins University · Biophysics</h3><p>Built NERDSS and ioNERDSS infrastructure and led computational studies of clathrin, retroviral Gag, and membrane-associated assembly.</p></div></div><div class="about-block reveal"><div class="about-block-label">Training</div><div><h3>Ph.D. in Condensed Matter Physics</h3><p>Developed quantitative models connecting molecular conformational changes and chemical transitions to the emergent mechanics of kinesin motors.</p></div></div><div class="about-block reveal"><div class="about-block-label">Interests</div><div><h3>Reusable research infrastructure</h3><p>Scientific software, protein conformational search, hybrid physics/ML workflows, simulation platforms, and agent-usable tools for molecular discovery.</p></div></div></div></div></section>
<section class="section-compact"><div class="container"><div class="contact-panel reveal"><div class="contact-panel-copy"><p class="eyebrow">Contact</p><h2>Building a molecular-modeling method or scientific platform?</h2><p>I am interested in research and engineering roles that connect computational methods to reliable, scalable software used by scientists.</p></div><a class="button button-primary" href="mailto:{e(site['email'])}">Email me {icon('mail')}</a></div></div></section>'''
    return layout("",site["description"],body,0)


def projects_index() -> str:
    items=[]
    for i,p in enumerate(projects):
        status=p["status"].lower().replace(" ","-")
        items.append(f'''<article class="project-index-item reveal" style="--delay:{i*70}ms"><a class="project-index-visual" href="{p['slug']}/"><img src="../{p['visual'].lstrip('/')}" alt="{e(p['visualAlt'])}"><span class="status-chip status-{status}">{e(p['status'])}</span></a><div class="project-index-copy"><div class="project-index-meta"><span>{e(p['category'])}</span><span>{e(p['period'])}</span></div><h2><a href="{p['slug']}/">{e(p['title'])}</a></h2><p>{e(p['summary'])}</p>{tags(p['tags'][:6],True)}<a class="text-link" href="{p['slug']}/">Read case study {icon('arrow',18)}</a></div></article>''')
    body=f'''<section class="page-hero"><div class="container page-hero-inner"><p class="eyebrow">Projects</p><h1>Scientific questions translated into algorithms and software.</h1><p class="page-hero-lead">These case studies show the complete path from problem definition and method design to implementation, validation, and reusable research infrastructure.</p></div></section><section class="section"><div class="container project-index-grid">{''.join(items)}</div></section>'''
    return layout("Projects","Case studies in protein conformational sampling, scientific GUI generation, reaction-diffusion infrastructure, and mechanistic biomolecular modeling.",body,1,"projects","projects/")


def project_page(p: dict[str,Any], index: int) -> str:
    related=[x for x in publications if x["id"] in p["relatedPublications"]]
    nxt=projects[(index+1)%len(projects)]
    metric="".join(f'<div class="project-metric"><div class="project-metric-value">{e(x["value"])}</div><div class="project-metric-label">{e(x["label"])}</div></div>' for x in p["metrics"])
    steps="".join(f'<article class="process-card reveal" style="--delay:{i*60}ms"><span class="process-index">{i+1:02d}</span><h3>{e(x["title"])}</h3><p>{e(x["text"])}</p></article>' for i,x in enumerate(p["steps"]))
    contributions="".join(f"<li>{e(x)}</li>" for x in p["contributions"])
    outcomes="".join(f'<div class="outcome-card reveal"><span class="outcome-check">✓</span><p>{e(x)}</p></div>' for x in p["outcomes"])
    note=f'<p class="project-note">{e(p["note"])}</p>' if p.get("note") else ""
    resource_nav='<a href="#resources">Resources</a>' if p["links"] else ""
    pub_nav='<a href="#publications">Publications</a>' if related else ""
    resources=""
    if p["links"]:
        links="".join(f'<a class="project-link-card" href="{e(x["href"])}" target="_blank" rel="noreferrer"><span>{e(x["label"])}</span>{icon("external")}</a>' for x in p["links"])
        resources=f'<section class="case-section" id="resources"><p class="eyebrow">Resources</p><h2>Papers, code, and documentation</h2><div class="project-links-grid">{links}</div></section>'
    related_html=f'<section class="case-section" id="publications"><p class="eyebrow">Related work</p><h2>Publications</h2><div class="publication-list">{"".join(publication_item(x,True) for x in related)}</div></section>' if related else ""
    body=f'''<section class="project-hero"><div class="container-wide"><a class="project-breadcrumb" href="../">{icon('arrow',16)} All projects</a><div class="project-hero-grid"><div class="project-hero-copy"><p class="eyebrow">{e(p['category'])}</p><h1>{e(p['title'])}</h1><p class="project-subtitle">{e(p['subtitle'])}</p><div class="project-hero-meta"><span>{e(p['status'])}</span><span>{e(p['period'])}</span></div>{tags(p['tags'])}</div><div class="project-hero-visual reveal is-visible"><img src="../../{p['visual'].lstrip('/')}" alt="{e(p['visualAlt'])}"></div></div></div></section><div class="project-summary-strip"><div class="container-wide project-summary-inner">{metric}</div></div><section class="section"><div class="container case-study-grid"><aside class="case-study-nav"><p>On this page</p><a href="#context">Context</a><a href="#approach">Approach</a><a href="#contribution">My contribution</a><a href="#outcomes">Outcomes</a>{resource_nav}{pub_nav}</aside><div class="case-study-content"><section class="case-section" id="context"><p class="eyebrow">Context</p><h2>The problem</h2><div class="case-section-text">{''.join(f'<p>{e(x)}</p>' for x in p['context'])}</div></section><section class="case-section" id="approach"><p class="eyebrow">Method</p><h2>How the system works</h2><div class="process-grid">{steps}</div></section><section class="case-section" id="contribution"><p class="eyebrow">Role</p><h2>My contribution</h2><ul class="detail-list">{contributions}</ul></section><section class="case-section" id="outcomes"><p class="eyebrow">Result</p><h2>Outcomes and scientific value</h2><div class="outcome-grid">{outcomes}</div>{note}</section>{resources}{related_html}</div></div></section><section class="section-compact"><div class="container"><a class="next-project" href="../{e(nxt['slug'])}/"><div><p>Next case study</p><h2>{e(nxt['title'])}</h2></div>{icon('arrow',34)}</a></div></section>'''
    return layout(p["shortTitle"],p["summary"],body,2,"projects",f"projects/{p['slug']}/",p["visual"])


def publications_page() -> str:
    years=sorted({x["year"] for x in publications},reverse=True)
    buttons='<button class="filter-button active" type="button" data-filter="all">All</button>'+"".join(f'<button class="filter-button" type="button" data-filter="{y}">{y}</button>' for y in years)
    script=r'''<script>const bs=[...document.querySelectorAll('[data-filter]')],is=[...document.querySelectorAll('[data-publication]')],c=document.querySelector('[data-publication-count]');bs.forEach(b=>b.addEventListener('click',()=>{const f=b.dataset.filter;bs.forEach(x=>x.classList.toggle('active',x===b));let n=0;is.forEach(x=>{const s=f==='all'||x.dataset.year===f;x.hidden=!s;if(s)n++});c.textContent=`${n} publication${n===1?'':'s'} shown`}));</script>'''
    body=f'''<section class="page-hero"><div class="container page-hero-inner"><p class="eyebrow">Publications</p><h1>Computational models and software for molecular systems.</h1><p class="page-hero-lead">Selected work spanning protein conformational modeling, biomolecular self-assembly, particle-based reaction-diffusion, and reusable scientific interfaces.</p></div></section><section class="section"><div class="container"><div class="publications-toolbar"><div class="filter-group">{buttons}</div><div class="publication-count" data-publication-count>{len(publications)} publications shown</div></div><div class="publication-list">{"".join(publication_item(x,True) for x in publications)}</div><div class="projects-footer"><a class="button button-secondary" href="{e(site['social']['scholar'])}" target="_blank" rel="noreferrer">Complete profile on Google Scholar {icon('external')}</a></div></div></section>'''
    return layout("Publications","Selected publications by Sikao Guo in computational biophysics, molecular self-assembly, scientific software, and structural bioinformatics.",body,1,"publications","publications/",extra_script=script)


def cv_page() -> str:
    timeline="".join(f'<article class="timeline-item"><div class="timeline-meta"><h3>{e(x["organization"])}</h3><span class="timeline-period">{e(x["period"])}</span></div><div class="timeline-role">{e(x["role"])} · {e(x["location"])}</div><ul class="timeline-highlights">{"".join(f"<li>{e(h)}</li>" for h in x["highlights"])}</ul><div class="timeline-tech">{"".join(f"<span>{e(t)}</span>" for t in x["technologies"])}</div></article>' for x in experience)
    skills="".join(f'<div class="skill-group"><h3>{e(x["title"])}</h3><p>{e(" · ".join(x["skills"]))}</p></div>' for x in skill_groups)
    edu="".join(f'<div class="education-item"><div><h3>{e(x["degree"])}</h3><p>{e(x["institution"])} · {e(x["location"])}</p></div><span>{e(x["period"])}</span></div>' for x in education)
    cvpubs="".join(publication_item(x) for x in sorted((x for x in publications if x.get("cvFeatured")),key=lambda x:x["cvOrder"]))
    software_parts=[]
    for x in open_source_software:
        links="".join(f'<a href="{e(link["href"])}" target="_blank" rel="noreferrer">{e(link["label"])}</a>' for link in x["links"])
        software_parts.append(f'<article class="cv-software-item"><div><h3>{e(x["name"])}</h3><p>{e(x["description"])}</p></div><div class="cv-software-links">{links}</div></article>')
    software="".join(software_parts)
    phone_href="".join(c for c in site["phone"] if c.isdigit() or c == "+")
    body=f'''<section class="page-hero"><div class="container page-hero-inner"><p class="eyebrow">Curriculum vitae</p><h1>Computational biology and molecular simulation.</h1><p class="page-hero-lead">Research engineer developing scalable C++ and Python systems spanning MPI-based high-performance computing, computational geometry, molecular simulation, and scientific workflows—transforming research algorithms into reusable software infrastructure.</p><div class="cv-actions"><a class="button button-primary" href="../documents/Sikao_Guo_PhD_resume.pdf" target="_blank">Download résumé {icon('download')}</a><a class="button button-secondary" href="mailto:{e(site['email'])}">Contact {icon('mail')}</a></div></div></section><section class="section"><div class="container cv-layout"><aside class="cv-sidebar"><div class="cv-profile"><p class="eyebrow">Profile</p><h2>{e(site['name'])}</h2><p>Research engineer building reusable scientific infrastructure for computational biology, molecular simulation, and high-performance computing.</p><div class="cv-contact-list"><a href="mailto:{e(site['email'])}">{e(site['email'])}</a><a href="tel:{e(phone_href)}">{e(site['phone'])}</a><a href="{e(site['social']['linkedin'])}" target="_blank">LinkedIn · sikaoguo</a><a href="{e(site['social']['github'])}" target="_blank">GitHub · sikaoguo22</a><a href="{e(site['social']['orcid'])}" target="_blank">ORCID · 0000-0002-7680-8060</a></div></div></aside><div class="cv-main"><section class="cv-section"><p class="eyebrow">Experience</p><h2>Research and engineering</h2><div class="timeline">{timeline}</div></section><section class="cv-section"><p class="eyebrow">Education</p><h2>Physics training</h2><div class="education-list">{edu}</div></section><section class="cv-section"><p class="eyebrow">Selected publications</p><h2>Research output</h2><div class="publication-list">{cvpubs}</div></section><section class="cv-section"><p class="eyebrow">Selected work</p><h2>Open-source software</h2><div class="cv-software-list">{software}</div></section><section class="cv-section"><p class="eyebrow">Technical strengths</p><h2>Methods and tools</h2><div class="skill-groups">{skills}</div></section></div></div></section>'''
    return layout("CV","Experience, education, publications, open-source software, and technical strengths of computational biology research engineer Sikao Guo.",body,1,"cv","cv/")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding="utf-8")


def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT/"assets").mkdir(parents=True)
    shutil.copy2(ROOT/"src"/"styles.css",OUT/"assets"/"styles.css")
    shutil.copytree(ROOT/"src"/"images",OUT/"images")
    (OUT/"documents").mkdir()
    shutil.copy2(ROOT/"resume"/"Sikao_Guo_PhD_resume.pdf",OUT/"documents"/"Sikao_Guo_PhD_resume.pdf")
    write(OUT/"index.html",home())
    write(OUT/"projects"/"index.html",projects_index())
    for i,p in enumerate(projects): write(OUT/"projects"/p["slug"]/"index.html",project_page(p,i))
    write(OUT/"publications"/"index.html",publications_page())
    write(OUT/"cv"/"index.html",cv_page())
    notfound=f'<section class="not-found"><div class="container"><p class="not-found-code">404</p><h1>This page is outside the sampled conformational space.</h1><p>The requested path does not exist.</p><a class="button button-primary" href="./">Return home {icon("arrow")}</a></div></section>'
    write(OUT/"404.html",layout("Page not found","Page not found",notfound,0,path="404.html",noindex=True))
    write(OUT/".nojekyll","")
    write(OUT/"robots.txt",f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    paths=["","projects/","publications/","cv/"]+[f"projects/{p['slug']}/" for p in projects]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{SITE_URL}/{p}</loc></url>\n' for p in paths)+'</urlset>\n'
    write(OUT/"sitemap.xml",sitemap)
    print(f"Built {len(paths)} pages in {OUT}")

if __name__ == "__main__": main()
