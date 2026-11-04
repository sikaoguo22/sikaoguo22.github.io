# Sikao Guo — research and scientific software website

The personal website at `sikaoguo22.github.io`, with the September 2026 redesign.
The design connects the existing research portfolio, career background, and updated
profile photo.

## Preview

The optional `Sikao_Guo_Website_Preview.html` can be generated locally using the
command below. Open it in a browser. Its navigation, mobile-width selector, publication
filters, and embedded citation downloads work without a server. External links still
require an internet connection. The preview toolbar is not part of the website.

For the actual production pages, use a local server rather than double-clicking
`site/index.html`:

```bash
python3 scripts/build.py
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`. Python 3.10+ is sufficient; the build uses the Python
standard library. No npm, frontend framework, or runtime CDN is required.

## Included

- A light "warm paper terminal" design: one monospace (IBM Plex Mono 400) at
  10–15px, hierarchy from size and colour only, `~/` prompt wordmark, numbered
  sections divided by 1px rules, steel-blue links and copper structure (section
  numbers, years, venues), and a faint drifting-speck background with a pause control.
- Three pages: Home, Publications, and CV.
- Homepage: research-focus strip, short bio with portrait, selected publications,
  and contact.
- A publications page with the full record from the CV (18 peer-reviewed, 2 preprints),
  grouped by year, with search, a type filter, and inline BibTeX toggles.
- A web CV drawn from the PDF CV: research focus, appointments, education,
  publications, and presentations.
- Responsive layout, keyboard focus states, reduced-motion support (the background
  stays still), and core content/navigation that work without JavaScript.
- Search/social metadata, a portrait-based social card, sitemap, robots file, and 404.
- Local assets only. No tracking scripts, analytics, cookies, or third-party font
  requests; IBM Plex Mono is self-hosted from `src/assets/fonts/` (SIL OFL 1.1).

## Structure and editing

```text
content/site.json          Identity, bio, research focus, CV sections
content/publications.json  The full publication record (CV-style author lists)
src/templates/base.html    Shared page structure and metadata
src/styles.css             Design tokens and responsive layouts
src/site.js                Publication filtering, background animation
src/init.js                Before-paint `js` class
src/assets/                Optimized portrait, favicon, social card, self-hosted font
scripts/build.py           Standard-library static generator
scripts/make_preview.py    Optional single-file review preview generator
tests/                     Standard-library and optional browser regression checks
site/                      Generated production output, not source
```

Edit the JSON and rebuild. Page-specific layout functions live in `scripts/build.py`.
The visual system is a light warm-mono style: paper `--bg`, ink `--ink`, rules
`--line`, steel-blue `--accent` for things you click and copper `--warm` for
structure. Adjust the variables at the beginning of `src/styles.css`; the tests
check that text tokens keep 4.5:1 contrast and that only weight 400 is used.

### Content safeguards

Keep publication status and authorship accurate. Two entries are explicitly
preprints in the supplied source; the ioNERDSS paper is not marked first-author.
The list mirrors the publications section of the CV (`academic_cv/main.pdf`). Statuses were preserved from supplied materials, not independently
rechecked with publishers during this update.

Review the public wording before publishing ongoing research. This package adds
no unpublished manuscript or private research data. Its public assets include the
profile photo; career details are presented in the web CV.

## Verification

Run the standard-library regression suite after building:

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
```

Optional browser tests require Playwright, but the site does not:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/browser_smoke.py
```

An existing Chromium installation can be selected with `CHROMIUM_EXECUTABLE`.
Browser tests inline local assets into pages to support offline checks; production
output still uses ordinary separate files. The browser suite reads the base path
from the built homepage, so it can also check a subpath build:

```bash
SITE_URL=https://example.org/preview python3 scripts/build.py
SITE_URL=https://example.org/preview python3 -m unittest discover -s tests -v
python3 tests/browser_smoke.py
```

The browser report defaults to the ignored `browser-results.json`; set
`BROWSER_REPORT` to save it elsewhere. Generated `site/`, caches, browser reports,
and single-file previews are not committed.

Generate a fresh single-file preview after content edits:

```bash
python3 scripts/make_preview.py Sikao_Guo_Website_Preview.html
```

This preview generator expects a build using the default root domain. For a
project-subpath deployment, test production output via a local server instead.

## Redesign integration

The redesign was applied from `Sikao_Guo_Website_Enhanced.zip` at the repository
root, based on `main` commit `4b08151b60acbe93d539c8b9425c6097301e38de`.

The generator and JSON schema are updated together; do not replace only the JSON
or only the generator. In November 2026 the Research, Software, About, and
project case-study pages were removed; their content and artwork remain in git
history (`content/projects.json`, `content/software.json`, `src/images/`).

The workflow retains the action versions already present in the repository. It
adds a standard-library test step before upload, plus a pull-request check that
builds and tests both URL configurations without deploying. The deployment
workflow runs only on pushes to `main` or an explicit manual dispatch.

### Custom domain or repository path

```bash
SITE_URL=https://example.org python3 scripts/build.py
SITE_URL=https://username.github.io/repository python3 scripts/build.py
```

Set the `SITE_URL` repository variable to the public base URL for deployment.
The default remains `https://sikaoguo22.github.io`. Deploy only `site/`, not the
single-file preview or the source directory.
