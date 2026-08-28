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
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "site"
SITE_URL = os.environ.get("SITE_URL", "https://sikaoguo22.github.io").rstrip("/")
SITE_PATH_PREFIX = urlparse(SITE_URL).path.rstrip("/")

site_data = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
projects: list[dict[str, Any]] = json.loads((CONTENT / "projects.json").read_text(encoding="utf-8"))
publications: list[dict[str, Any]] = json.loads((CONTENT / "publications.json").read_text(encoding="utf-8"))
site = site_data["site"]
navigation = site_data["navigation"]
hiring_snapshot = site_data["hiringSnapshot"]
impact_stats = site_data["impactStats"]
resumes = site_data["resumes"]
experience = site_data["experience"]
education = site_data["education"]
skill_groups = site_data["skillGroups"]
open_source_software = site_data["openSourceSoftware"]


def e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def rel(_depth: int, path: str) -> str:
    if path.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return path
    return f"{SITE_PATH_PREFIX}/{path.lstrip('/')}"


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


def project_image(
    project: dict[str, Any],
    depth: int,
    *,
    loading: str,
    sizes: str,
    fetch_priority: bool = False,
) -> str:
    priority = ' fetchpriority="high"' if fetch_priority else ""
    return (
        f'<img src="{rel(depth, project["visual"])}" '
        f'srcset="{rel(depth, project["visualSmall"])} 800w, {rel(depth, project["visual"])} 1600w" '
        f'sizes="{e(sizes)}" alt="{e(project["visualAlt"])}" width="1600" height="1000" '
        f'loading="{loading}" decoding="async"{priority}>'
    )


def proof_links(items: list[dict[str, str]], class_name: str, limit: int | None = None) -> str:
    selected = items[:limit] if limit else items
    if not selected:
        return ""
    links = "".join(
        f'<a href="{e(item["href"])}" target="_blank" rel="noreferrer" '
        f'aria-label="{e(item["kind"])}: {e(item["label"])}">'
        f'<span class="proof-kind">{e(item["kind"])}</span>'
        f'<span class="proof-detail">{e(item["label"])}</span>{icon("external",13)}</a>'
        for item in selected
    )
    return f'<div class="{class_name}">{links}</div>'


def publication_item(pub: dict[str, Any], contribution: bool = False) -> str:
    citation = f" · {e(pub['citation'])}" if pub.get("citation") else ""
    contribution_html = ""
    if contribution and pub.get("contribution"):
        contribution_html = f'<p class="publication-contribution"><strong>Contribution:</strong> {e(pub["contribution"])}</p>'
    badge = '<span class="publication-badge">First author</span>' if pub.get("firstAuthor") else ""
    resources = [{"kind": "Paper", "label": pub["venue"], "href": pub["url"]}, *pub.get("resources", [])]
    resources_html = proof_links(resources, "publication-proof-links")
    return f'''<article class="publication-item" data-publication data-year="{pub['year']}">
<div class="publication-year">{pub['year']}</div><div class="publication-main"><div class="publication-type">{e(pub['type'])} · {e(pub['venue'])}{citation}{badge}</div>
<h3><a href="{e(pub['url'])}" target="_blank" rel="noreferrer">{e(pub['title'])}{icon('external',16)}</a></h3><p class="publication-authors">{e(pub['authors'])}</p>{contribution_html}
<div class="publication-footer">{tags(pub['topics'])}{resources_html}</div></div></article>'''


def scholarly_article_schema(pub: dict[str, Any]) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "@type": "ScholarlyArticle",
        "headline": pub["title"],
        "datePublished": str(pub["year"]),
        "url": pub["url"],
        "author": {"@type": "Person", "name": site["name"], "url": f"{SITE_URL}/"},
        "isPartOf": {"@type": "Periodical", "name": pub["venue"]},
        "about": pub["topics"],
    }
    if pub.get("doi"):
        schema["identifier"] = f"https://doi.org/{pub['doi']}"
    return schema


def project_card(project: dict[str, Any], depth: int, index: int) -> str:
    href = rel(depth, f"projects/{project['slug']}/")
    status_cls = project["status"].lower().replace(" ", "-")
    image = project_image(
        project,
        depth,
        loading="lazy",
        sizes="(max-width: 840px) calc(100vw - 34px), 560px",
    )
    resources = proof_links(project["links"], "project-card-links", 3)
    return f'''<article class="project-card reveal" style="--delay:{index*80}ms" data-project-card data-scientist-order="{project['roleOrder']['scientist']}" data-engineer-order="{project['roleOrder']['engineer']}"><a class="project-card-visual" href="{href}">{image}<span class="status-chip status-{status_cls}">{e(project['status'])}</span></a><div class="project-card-content"><div class="project-card-meta"><span>{e(project['category'])}</span><span>{e(project['period'])}</span></div><h3><a href="{href}">{e(project['shortTitle'])}</a></h3>{resources}<p>{e(project['summary'])}</p><p class="project-card-role"><strong>My role</strong>{e(project['roleSummary'])}</p>{tags(project['tags'][:4],True)}<a class="text-link" href="{href}">Read case study {icon('arrow',18)}</a></div></article>'''


def section_header(eyebrow: str, title: str, description: str) -> str:
    return f'<div class="section-header"><p class="eyebrow">{e(eyebrow)}</p><h2>{e(title)}</h2><p class="section-description">{e(description)}</p></div>'


def header(depth: int, active: str) -> str:
    def nav_link(item: dict[str, str], mobile: bool = False) -> str:
        current = item["label"].lower() == active
        cls = ' class="active"' if current else ""
        aria = ' aria-current="page"' if current else ""
        content = f'<span>{e(item["label"])}</span>{icon("arrow")}' if mobile else e(item["label"])
        return f'<a{cls}{aria} href="{rel(depth, item["href"])}">{content}</a>'

    desktop = "".join(nav_link(x) for x in navigation)
    mobile = "".join(nav_link(x, True) for x in navigation)
    return f'''<header class="site-header" data-header><div class="header-inner container-wide"><a class="brand" href="{rel(depth,'/')}" aria-label="Sikao Guo, home"><span class="brand-mark">SG</span><span class="brand-name">Sikao Guo</span></a><nav class="desktop-nav" aria-label="Primary navigation">{desktop}</nav><div class="header-actions"><button class="icon-button theme-toggle" type="button" aria-label="Switch color theme" data-theme-toggle><span class="theme-icon theme-icon-sun">{icon('sun',18)}</span><span class="theme-icon theme-icon-moon">{icon('moon',18)}</span></button><a class="button button-small button-primary header-contact" href="mailto:{e(site['email'])}">Contact</a><button class="icon-button menu-toggle" type="button" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobile-navigation" data-menu-toggle><span class="menu-open-icon">{icon('menu')}</span><span class="menu-close-icon">{icon('close')}</span></button></div></div><nav class="mobile-nav" id="mobile-navigation" aria-label="Mobile navigation" data-mobile-nav><div class="container-wide mobile-nav-inner">{mobile}<a href="mailto:{e(site['email'])}"><span>Contact</span>{icon('mail')}</a></div></nav></header>'''


def footer(depth: int) -> str:
    s = site["social"]
    location = f'<span>{e(site["location"])}</span>' if site["location"] else ""
    return f'''<footer class="site-footer"><div class="container-wide footer-grid"><div class="footer-intro"><a class="footer-brand" href="{rel(depth,'/')}">Sikao Guo</a><p>Computational biophysics, molecular modeling, and reusable scientific software.</p></div><div class="footer-contact"><p class="footer-label">Contact</p><a href="mailto:{e(site['email'])}">{e(site['email'])}</a>{location}</div><div class="footer-social"><p class="footer-label">Profiles</p><div class="social-links"><a href="{e(s['github'])}" target="_blank" rel="noreferrer" aria-label="GitHub">{icon('github')}</a><a href="{e(s['linkedin'])}" target="_blank" rel="noreferrer" aria-label="LinkedIn">{icon('linkedin')}</a><a href="{e(s['scholar'])}" target="_blank" rel="noreferrer" aria-label="Google Scholar">{icon('scholar')}</a><a href="{e(s['orcid'])}" target="_blank" rel="noreferrer" aria-label="ORCID">{icon('orcid')}</a></div></div></div><div class="container-wide footer-bottom"><span>© {datetime.now().year} Sikao Guo</span><span>Built for clarity, reproducibility, and scientific impact.</span></div></footer>'''


GENERAL_SCRIPT = r'''<script>
(() => {
  const root = document.documentElement;
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const mobileNav = document.querySelector('[data-mobile-nav]');
  const header = document.querySelector('[data-header]');

  const updateThemeLabel = () => {
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    themeToggle?.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
  };
  updateThemeLabel();
  themeToggle?.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = nextTheme;
    try { localStorage.setItem('theme', nextTheme); } catch {}
    updateThemeLabel();
  });

  const closeMenu = (restoreFocus = false) => {
    header?.classList.remove('menu-open');
    menuToggle?.setAttribute('aria-expanded', 'false');
    menuToggle?.setAttribute('aria-label', 'Open navigation menu');
    document.body.classList.remove('nav-open');
    if (restoreFocus) menuToggle?.focus();
  };
  menuToggle?.addEventListener('click', () => {
    const isOpen = header?.classList.toggle('menu-open') ?? false;
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    menuToggle.setAttribute('aria-label', `${isOpen ? 'Close' : 'Open'} navigation menu`);
    document.body.classList.toggle('nav-open', isOpen);
    if (isOpen) mobileNav?.querySelector('a')?.focus();
  });
  mobileNav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && header?.classList.contains('menu-open')) closeMenu(true);
    if (event.key !== 'Tab' || !header?.classList.contains('menu-open')) return;
    const focusable = [menuToggle, ...(mobileNav?.querySelectorAll('a') ?? [])].filter(Boolean);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  });
  matchMedia('(min-width: 841px)').addEventListener?.('change', event => {
    if (event.matches) closeMenu();
  });

  const observer = 'IntersectionObserver' in window
    ? new IntersectionObserver(entries => entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      }), { threshold: .12 })
    : null;
  document.querySelectorAll('.reveal').forEach(element =>
    observer ? observer.observe(element) : element.classList.add('is-visible')
  );

  const updateHeader = () => header?.classList.toggle('scrolled', scrollY > 12);
  updateHeader();
  addEventListener('scroll', updateHeader, { passive: true });
})();
</script>'''


def layout(
    title: str,
    description: str,
    body: str,
    depth: int,
    active: str = "",
    path: str = "",
    image: str = "/images/og-image.png",
    image_alt: str = "Sikao Guo — computational biophysics and scientific software",
    extra_script: str = "",
    noindex: bool = False,
    structured_data: dict[str, Any] | None = None,
) -> str:
    full = f"{title} | Sikao Guo" if title else f"Sikao Guo | {site['title']}"
    canonical = f"{SITE_URL}/{path.lstrip('/')}"
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    schema = ""
    if structured_data:
        payload = json.dumps(structured_data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        schema = f'<script type="application/ld+json">{payload}</script>'
    image_url = f"{SITE_URL}/{image.lstrip('/')}"
    return f'''<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{e(description)}"><meta name="author" content="Sikao Guo"><meta name="theme-color" content="#f4f2eb">{robots}<link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="{rel(depth,'images/favicon.svg')}"><script>(()=>{{try{{const s=localStorage.getItem('theme');const p=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';document.documentElement.dataset.theme=s||p}}catch{{}}}})()</script><link rel="stylesheet" href="{rel(depth,'assets/styles.css')}"><meta property="og:type" content="website"><meta property="og:site_name" content="Sikao Guo"><meta property="og:locale" content="en_US"><meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{image_url}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{e(image_alt)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(full)}"><meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="{e(image_alt)}"><title>{e(full)}</title>{schema}<noscript><style>.reveal{{opacity:1;transform:none}}</style></noscript></head><body><a class="skip-link" href="#main-content">Skip to content</a>{header(depth,active)}<main id="main-content" tabindex="-1">{body}</main>{footer(depth)}{extra_script}{GENERAL_SCRIPT}</body></html>'''


def home() -> str:
    ordered_projects = sorted(projects, key=lambda p: p["roleOrder"]["scientist"])
    project_cards = [project_card(p,0,i) for i,p in enumerate(ordered_projects)]
    featured_projects = "".join(project_cards[:3])
    more_work = project_cards[3]
    home_publications = sorted((p for p in publications if p.get("homeOrder")), key=lambda p: p["homeOrder"])
    pubs = "".join(publication_item(p) for p in home_publications)
    snapshot = "".join(f'<article class="snapshot-card reveal" style="--delay:{i*70}ms"><p>{e(x["label"])}</p><h3>{e(x["title"])}</h3><span>{e(x["description"])}</span></article>' for i,x in enumerate(hiring_snapshot))
    stats = "".join(f'<div class="impact-item"><div class="impact-value">{e(x["value"])}<span>{e(x["suffix"])}</span></div><p class="impact-label">{e(x["label"])}</p></div>' for x in impact_stats)
    by_slug = {p["slug"]: p for p in projects}
    evidence_specs = [
        ("inverse-kinematics-backbone-sampling", "Protein conformations", "hero-evidence-main"),
        ("cross-platform-gui-generation", "Scientific interfaces", ""),
        ("mechanistic-assembly-models", "Mechanistic assembly", ""),
    ]
    evidence_cards = []
    for index, (slug, label, class_name) in enumerate(evidence_specs):
        project = by_slug[slug]
        image = project_image(
            project,
            0,
            loading="eager",
            sizes="(max-width: 1050px) calc(100vw - 34px), 520px" if class_name else "(max-width: 1050px) calc((100vw - 46px) / 2), 250px",
            fetch_priority=index == 0,
        )
        evidence_cards.append(f'<a class="hero-evidence-card {class_name}" href="{rel(0, f"projects/{slug}/")}">{image}<span class="hero-evidence-label"><small>0{index + 1}</small>{e(label)}</span></a>')
    scientist_resume = resumes["scientist"]
    engineer_resume = resumes["engineer"]
    role_script = f'''<script>
(() => {{
  const roles = {{
    scientist: {{
      label: 'Research Scientist',
      context: 'Mechanistic modeling, method development, and scientific validation appear first.',
      resumeLabel: '{e(scientist_resume["label"])}',
      resumePath: '{rel(0, scientist_resume["path"])}'
    }},
    engineer: {{
      label: 'Research Software Engineer',
      context: 'Software architecture, HPC, testing, and researcher-facing systems appear first.',
      resumeLabel: '{e(engineer_resume["label"])}',
      resumePath: '{rel(0, engineer_resume["path"])}'
    }}
  }};
  const buttons = [...document.querySelectorAll('[data-career-role]')];
  const cards = [...document.querySelectorAll('[data-project-card]')];
  const featured = document.querySelector('[data-featured-projects]');
  const more = document.querySelector('[data-more-work]');
  const context = document.querySelector('[data-role-context]');
  const resume = document.querySelector('[data-role-resume]');
  const roleLabel = document.querySelector('[data-role-label]');

  const setRole = role => {{
    const selected = roles[role] ? role : 'scientist';
    const config = roles[selected];
    document.documentElement.dataset.careerRole = selected;
    buttons.forEach(button => {{
      const active = button.dataset.careerRole === selected;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    }});
    context.textContent = config.context;
    roleLabel.textContent = config.label;
    resume.href = config.resumePath;
    resume.querySelector('[data-role-resume-label]').textContent = config.resumeLabel;
    const orderKey = `${{selected}}Order`;
    const ordered = cards.sort((a, b) => Number(a.dataset[orderKey]) - Number(b.dataset[orderKey]));
    ordered.forEach(card => card.classList.remove('project-card-secondary'));
    featured.replaceChildren(...ordered.slice(0, 3));
    const secondary = ordered[3];
    secondary.classList.add('project-card-secondary');
    more.replaceChildren(secondary);
    try {{ localStorage.setItem('careerRole', selected); }} catch {{}}
  }};

  buttons.forEach(button => button.addEventListener('click', () => setRole(button.dataset.careerRole)));
  let initialRole = 'scientist';
  try {{ initialRole = localStorage.getItem('careerRole') || initialRole; }} catch {{}}
  setRole(initialRole);
}})();
</script>'''
    body = f'''<section class="home-hero"><div class="container-wide hero-grid"><div class="hero-copy reveal is-visible"><p class="hero-kicker">Computational biophysics × scientific computing</p><h1>I build validated molecular-modeling methods and the software that makes them <span class="hero-accent">usable at scale.</span></h1><p class="hero-lead">Research scientist and software engineer working across protein conformational sampling, biomolecular self-assembly, structural bioinformatics, and high-performance simulation.</p><div class="hero-actions"><a class="button button-primary" href="#selected-work">View case studies {icon('arrow')}</a><a class="button button-secondary" href="{rel(0, scientist_resume['path'])}" download>{e(scientist_resume['label'])} {icon('download',18)}</a><a class="button button-secondary" href="{rel(0, engineer_resume['path'])}" download>{e(engineer_resume['label'])} {icon('download',18)}</a></div><div class="hero-trust"><span>{e(site['availability'])}</span><span>{e(site['workAuthorization'])}</span></div></div><div class="hero-evidence" role="group" aria-label="Selected project evidence">{''.join(evidence_cards)}</div></div></section>
<section class="section section-muted hiring-section"><div class="container-wide"><div class="hiring-heading"><div>{section_header('Hiring snapshot','Two role paths. One scientific-computing profile.','Choose the lens most relevant to your team; the evidence is the same, while project priority and the recommended resume adapt.')}</div><div class="role-panel"><div class="role-toggle" role="group" aria-label="Choose a hiring perspective"><button class="role-button active" type="button" data-career-role="scientist" aria-pressed="true">View as Research Scientist</button><button class="role-button" type="button" data-career-role="engineer" aria-pressed="false">View as Research Software Engineer</button></div><p class="role-context" data-role-context aria-live="polite">Mechanistic modeling, method development, and scientific validation appear first.</p><a class="role-resume-link" href="{rel(0, scientist_resume['path'])}" download data-role-resume><span>Best-fit download</span><strong data-role-resume-label>{e(scientist_resume['label'])}</strong>{icon('download',18)}</a></div></div><div class="snapshot-grid">{snapshot}</div></div></section>
<section class="section section-dark grid-noise"><div class="container"><div class="impact-strip reveal">{stats}</div></div></section>
<section class="section" id="selected-work"><div class="container-wide">{section_header('Selected work','Research methods developed as reusable infrastructure.','The three strongest case studies for the selected role appear first. Change the hiring perspective above without changing the underlying evidence.')}<p class="selected-role-label">Priority for <strong data-role-label>Research Scientist</strong></p><div class="projects-grid featured-projects" data-featured-projects>{featured_projects}</div><div class="more-work"><p class="eyebrow">More work</p><div class="more-work-grid" data-more-work>{more_work}</div></div><div class="projects-footer"><a class="button button-secondary" href="projects/">Explore all case studies {icon('arrow')}</a></div></div></section>
<section class="section section-muted"><div class="container">{section_header('Selected publications','Mechanistic modeling, molecular structure and dynamics, and scientific computing.','A focused selection of work in protein assembly, structural workflows, high-performance simulation, and research software.')}<div class="publication-list reveal">{pubs}</div><div class="projects-footer"><a class="button button-secondary" href="publications/">View publication list {icon('arrow')}</a></div></div></section>
<section class="section"><div class="container about-grid"><div class="about-statement"><p class="eyebrow">Collaboration</p><h2>Physics training, biological questions, engineering execution.</h2><p>I work with experimental scientists, modelers, and software teams to turn research questions into testable methods—and those methods into maintainable systems others can validate, scale, and reuse.</p></div><div class="about-details"><div class="about-block reveal"><div class="about-block-label">2025–now</div><div><h3>Research Engineer · Inria</h3><p>Developing inverse-kinematics protein-backbone samplers and a cross-platform framework for automatically generating VMD, PyMOL, and web applications.</p></div></div><div class="about-block reveal"><div class="about-block-label">2020–2025</div><div><h3>Johns Hopkins University · Biophysics</h3><p>Built NERDSS and ioNERDSS infrastructure and led computational studies of clathrin, retroviral Gag, and membrane-associated assembly.</p></div></div><div class="about-block reveal"><div class="about-block-label">Ph.D.</div><div><h3>Institute of Physics, Chinese Academy of Sciences</h3><p>Developed quantitative models connecting molecular conformational changes and chemical transitions to the emergent mechanics of kinesin motors.</p></div></div></div></div></section>
<section class="section-compact"><div class="container-wide"><div class="contact-panel reveal"><div class="contact-panel-copy"><p class="eyebrow">Contact</p><h2>Building a molecular-modeling method or scientific platform?</h2><p>I am open to U.S.-based Research Scientist and Research Software Engineer roles. No sponsorship required.</p></div><div class="contact-actions"><a class="button button-primary" href="mailto:{e(site['email'])}">Email me {icon('mail')}</a><a class="button button-secondary" href="{rel(0, scientist_resume['path'])}" download>Scientist resume {icon('download',18)}</a><a class="button button-secondary" href="{rel(0, engineer_resume['path'])}" download>Engineer resume {icon('download',18)}</a></div></div></div></section>'''
    profile_schema = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": f"{SITE_URL}/",
        "mainEntity": {
            "@type": "Person",
            "name": site["name"],
            "url": f"{SITE_URL}/",
            "jobTitle": ["Research Scientist", "Research Software Engineer"],
            "description": site["description"],
            "email": f"mailto:{site['email']}",
            "knowsAbout": ["Computational biophysics", "Molecular modeling", "Structural bioinformatics", "Scientific computing", "High-performance computing"],
            "sameAs": list(site["social"].values()),
        },
    }
    return layout("",site["description"],body,0,structured_data=profile_schema,extra_script=role_script)


def projects_index() -> str:
    items=[]
    for i,p in enumerate(projects):
        status=p["status"].lower().replace(" ","-")
        image = project_image(
            p,
            1,
            loading="eager" if i == 0 else "lazy",
            sizes="(max-width: 840px) calc(100vw - 34px), 520px",
            fetch_priority=i == 0,
        )
        resources = proof_links(p["links"], "project-card-links", 4)
        items.append(f'''<article class="project-index-item reveal" style="--delay:{i*70}ms"><a class="project-index-visual" href="{p['slug']}/">{image}<span class="status-chip status-{status}">{e(p['status'])}</span></a><div class="project-index-copy"><div class="project-index-meta"><span>{e(p['category'])}</span><span>{e(p['period'])}</span></div><h2><a href="{p['slug']}/">{e(p['title'])}</a></h2>{resources}<p>{e(p['summary'])}</p><p class="project-index-role"><strong>My role</strong>{e(p['roleSummary'])}</p>{tags(p['tags'][:6],True)}<a class="text-link" href="{p['slug']}/">Read case study {icon('arrow',18)}</a></div></article>''')
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
        links="".join(f'<a class="project-link-card" href="{e(x["href"])}" target="_blank" rel="noreferrer"><span><small>{e(x["kind"])}</small>{e(x["label"])}</span>{icon("external")}</a>' for x in p["links"])
        resources=f'<section class="case-section" id="resources"><p class="eyebrow">Resources</p><h2>Papers, code, and documentation</h2><div class="project-links-grid">{links}</div></section>'
    related_html=f'<section class="case-section" id="publications"><p class="eyebrow">Related work</p><h2>Publications</h2><div class="publication-list">{"".join(publication_item(x,True) for x in related)}</div></section>' if related else ""
    hero_links = ""
    if p["links"]:
        hero_links = proof_links(p["links"], "project-hero-links")
    hero_image = project_image(
        p,
        2,
        loading="eager",
        sizes="(max-width: 1050px) calc(100vw - 48px), 620px",
        fetch_priority=True,
    )
    body=f'''<section class="project-hero"><div class="container-wide"><a class="project-breadcrumb" href="../">{icon('arrow',16)} All projects</a><div class="project-hero-grid"><div class="project-hero-copy"><p class="eyebrow">{e(p['category'])}</p><h1>{e(p['title'])}</h1><p class="project-subtitle">{e(p['subtitle'])}</p><p class="project-hero-result"><strong>Outcome</strong>{e(p['heroResult'])}</p><div class="project-role-summary"><span>My role</span><p>{e(p['roleSummary'])}</p></div><div class="project-hero-meta"><span>{e(p['status'])}</span><span>{e(p['period'])}</span></div>{tags(p['tags'])}{hero_links}</div><div class="project-hero-visual reveal is-visible">{hero_image}</div></div></div></section><div class="project-summary-strip"><div class="container-wide project-summary-inner">{metric}</div></div><section class="section"><div class="container case-study-grid"><aside class="case-study-nav"><p>On this page</p><a href="#context">Context</a><a href="#approach">Approach</a><a href="#contribution">My contribution</a><a href="#outcomes">Outcomes</a>{resource_nav}{pub_nav}</aside><div class="case-study-content"><section class="case-section" id="context"><p class="eyebrow">Context</p><h2>The problem</h2><div class="case-section-text">{''.join(f'<p>{e(x)}</p>' for x in p['context'])}</div></section><section class="case-section" id="approach"><p class="eyebrow">Method</p><h2>How the system works</h2><div class="process-grid">{steps}</div></section><section class="case-section" id="contribution"><p class="eyebrow">Role</p><h2>My contribution</h2><ul class="detail-list">{contributions}</ul></section><section class="case-section" id="outcomes"><p class="eyebrow">Result</p><h2>Outcomes and scientific value</h2><div class="outcome-grid">{outcomes}</div>{note}</section>{resources}{related_html}</div></div></section><section class="section-compact"><div class="container"><a class="next-project" href="../{e(nxt['slug'])}/"><div><p>Next case study</p><h2>{e(nxt['title'])}</h2></div>{icon('arrow',34)}</a></div></section>'''
    schema_entities: list[dict[str, Any]] = []
    code_repositories = [x["href"] for x in p["links"] if x["kind"] == "Code"]
    if code_repositories:
        languages = [x for x in p["tags"] if x in {"C++", "Python"}]
        schema_entities.append({
            "@type": "SoftwareSourceCode",
            "name": p["title"],
            "description": p["summary"],
            "url": f"{SITE_URL}/projects/{p['slug']}/",
            "codeRepository": code_repositories,
            "programmingLanguage": languages,
            "author": {"@type": "Person", "name": site["name"], "url": f"{SITE_URL}/"},
        })
    schema_entities.extend(scholarly_article_schema(x) for x in related)
    project_schema = {"@context": "https://schema.org", "@graph": schema_entities} if schema_entities else None
    return layout(p["shortTitle"],p["summary"],body,2,"projects",f"projects/{p['slug']}/",structured_data=project_schema)


def publications_page() -> str:
    years=sorted({x["year"] for x in publications},reverse=True)
    buttons='<button class="filter-button active" type="button" data-filter="all" aria-pressed="true">All</button>'+"".join(f'<button class="filter-button" type="button" data-filter="{y}" aria-pressed="false">{y}</button>' for y in years)
    script=r'''<script>
const filterButtons = [...document.querySelectorAll('[data-filter]')];
const publicationItems = [...document.querySelectorAll('[data-publication]')];
const publicationCount = document.querySelector('[data-publication-count]');
filterButtons.forEach(button => button.addEventListener('click', () => {
  const filter = button.dataset.filter;
  filterButtons.forEach(candidate => {
    const selected = candidate === button;
    candidate.classList.toggle('active', selected);
    candidate.setAttribute('aria-pressed', String(selected));
  });
  let visibleCount = 0;
  publicationItems.forEach(item => {
    const visible = filter === 'all' || item.dataset.year === filter;
    item.hidden = !visible;
    if (visible) visibleCount += 1;
  });
  publicationCount.textContent = `${visibleCount} publication${visibleCount === 1 ? '' : 's'} shown`;
}));
</script>'''
    body=f'''<section class="page-hero"><div class="container page-hero-inner"><p class="eyebrow">Selected publications</p><h1>Computational models and software for molecular systems.</h1><p class="page-hero-lead">Selected work spanning protein conformational modeling, biomolecular self-assembly, particle-based reaction-diffusion, and reusable scientific interfaces.</p></div></section><section class="section"><div class="container"><div class="publications-toolbar"><div class="filter-group" role="group" aria-label="Filter publications by year">{buttons}</div><div class="publication-count" role="status" aria-live="polite" aria-atomic="true" data-publication-count>{len(publications)} publications shown</div></div><h2 class="visually-hidden">Publication list</h2><div class="publication-list">{"".join(publication_item(x,True) for x in publications)}</div><div class="projects-footer"><a class="button button-secondary" href="{e(site['social']['scholar'])}" target="_blank" rel="noreferrer">Complete profile on Google Scholar {icon('external')}</a></div></div></section>'''
    publications_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Selected Publications by Sikao Guo",
                "url": f"{SITE_URL}/publications/",
            },
            *(scholarly_article_schema(x) for x in publications),
        ],
    }
    return layout("Selected Publications","Selected publications by Sikao Guo in computational biophysics, molecular self-assembly, scientific software, and structural bioinformatics.",body,1,"publications","publications/",extra_script=script,structured_data=publications_schema)


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
    body=f'''<section class="page-hero"><div class="container page-hero-inner"><p class="eyebrow">Curriculum vitae</p><h1>Computational biology and molecular simulation.</h1><p class="page-hero-lead">Research scientist and software engineer developing validated C++ and Python methods across molecular modeling, structural bioinformatics, and high-performance simulation.</p><div class="cv-actions"><a class="button button-primary" href="../documents/{e(Path(resumes['scientist']['path']).name)}" download>Research Scientist resume {icon('download')}</a><a class="button button-secondary" href="../documents/{e(Path(resumes['engineer']['path']).name)}" download>Research Software Engineer resume {icon('download')}</a><a class="button button-secondary" href="mailto:{e(site['email'])}">Contact {icon('mail')}</a></div></div></section><section class="section"><div class="container cv-layout"><aside class="cv-sidebar"><div class="cv-profile"><p class="eyebrow">Profile</p><h2>{e(site['name'])}</h2><p>Research scientist and software engineer building validated methods and reusable scientific infrastructure for computational biology, molecular simulation, and high-performance computing.</p><div class="cv-contact-list"><a href="mailto:{e(site['email'])}">{e(site['email'])}</a><a href="tel:{e(phone_href)}">{e(site['phone'])}</a><span>{e(site['workAuthorization'])}</span><a href="{e(site['social']['linkedin'])}" target="_blank">LinkedIn · sikaoguo</a><a href="{e(site['social']['github'])}" target="_blank">GitHub · sikaoguo22</a><a href="{e(site['social']['orcid'])}" target="_blank">ORCID · 0000-0002-7680-8060</a></div></div></aside><div class="cv-main"><section class="cv-section"><p class="eyebrow">Experience</p><h2>Research and engineering</h2><div class="timeline">{timeline}</div></section><section class="cv-section"><p class="eyebrow">Education</p><h2>Physics training</h2><div class="education-list">{edu}</div></section><section class="cv-section"><p class="eyebrow">Selected publications</p><h2>Research output</h2><div class="publication-list">{cvpubs}</div></section><section class="cv-section"><p class="eyebrow">Selected work</p><h2>Open-source software</h2><div class="cv-software-list">{software}</div></section><section class="cv-section"><p class="eyebrow">Technical strengths</p><h2>Methods and tools</h2><div class="skill-groups">{skills}</div></section></div></div></section>'''
    return layout("CV","Experience, education, publications, open-source software, and technical strengths of computational biology research engineer Sikao Guo.",body,1,"cv","cv/")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding="utf-8")


def main() -> None:
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT/"assets").mkdir(parents=True)
    shutil.copy2(ROOT/"src"/"styles.css",OUT/"assets"/"styles.css")
    (OUT/"images").mkdir()
    runtime_images = {"favicon.svg", "og-image.png"}
    for project in projects:
        runtime_images.add(Path(project["visual"]).name)
        runtime_images.add(Path(project["visualSmall"]).name)
    for image_name in sorted(runtime_images):
        shutil.copy2(ROOT/"src"/"images"/image_name,OUT/"images"/image_name)
    (OUT/"documents").mkdir()
    for resume in resumes.values():
        filename = Path(resume["path"]).name
        shutil.copy2(ROOT/"resume"/filename,OUT/"documents"/filename)
    write(OUT/"index.html",home())
    write(OUT/"projects"/"index.html",projects_index())
    for i,p in enumerate(projects): write(OUT/"projects"/p["slug"]/"index.html",project_page(p,i))
    write(OUT/"publications"/"index.html",publications_page())
    write(OUT/"cv"/"index.html",cv_page())
    notfound=f'<section class="not-found"><div class="container"><p class="not-found-code">404</p><h1>This page is outside the sampled conformational space.</h1><p>The requested path does not exist.</p><a class="button button-primary" href="{rel(0, "/")}">Return home {icon("arrow")}</a></div></section>'
    write(OUT/"404.html",layout("Page not found","Page not found",notfound,0,path="404.html",noindex=True))
    write(OUT/".nojekyll","")
    write(OUT/"robots.txt",f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    paths=["","projects/","publications/","cv/"]+[f"projects/{p['slug']}/" for p in projects]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{SITE_URL}/{p}</loc></url>\n' for p in paths)+'</urlset>\n'
    write(OUT/"sitemap.xml",sitemap)
    print(f"Built {len(paths)} pages in {OUT}")

if __name__ == "__main__": main()
