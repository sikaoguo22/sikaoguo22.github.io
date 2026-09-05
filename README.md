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

- A personal homepage with portrait, research questions, scoped results, software,
  selected papers, and a research/collaboration contact section.
- Separate Research and Software pages, an all-projects index, and four case studies.
- A publications page with search, publication-type filters, explicit preprint and
  first-author labels, and copyable/downloadable citations.
- About and web CV pages.
- Responsive mobile navigation, light/dark themes, keyboard focus states, reduced
  motion support, and core content/navigation that work without JavaScript.
- Search/social metadata, a portrait-based social card, sitemap, robots file, and 404.
- Local assets only. No tracking scripts, analytics, cookies, or external web fonts.
  A localStorage preference remembers the chosen theme where storage is available.

## Structure and editing

```text
content/site.json          Identity, hero copy, research themes, experience, skills
content/projects.json      Four detailed project case studies
content/software.json      AutoCLIP, NERDSS-MPI, and ioNERDSS
content/publications.json  The selected publication record
src/templates/base.html    Shared page structure and metadata
src/styles.css             Design tokens and responsive layouts
src/site.js                Navigation, theme, publication filtering/copying
src/theme-init.js          Before-paint theme selection
src/assets/                Optimized portrait, favicon, social card
scripts/build.py           Standard-library static generator
scripts/make_preview.py    Optional single-file review preview generator
tests/                     Standard-library and optional browser regression checks
site/                      Generated production output, not source
```

Edit the JSON and rebuild. Page-specific layout functions live in `scripts/build.py`.
The visual system uses navy, muted teal, and light neutral surfaces. Adjust the
variables at the beginning of `src/styles.css` to change the palette.

### Content safeguards

Keep publication status and authorship accurate. Two entries are explicitly
preprints in the supplied source; the ioNERDSS paper is not marked first-author.
The list is selected, not a complete bibliography. Google Scholar links to the
full record. Statuses were preserved from supplied materials, not independently
rechecked with publishers during this update.

The approximately 90× result is scoped to 96 CPUs and a 20,000-particle benchmark.
The sampler remains ongoing work; its generative-sampler comparison is limited
to evaluated systems. The project diagrams are labeled **conceptual schematics**,
not experimental figures, measured curves, or interactive molecular viewers.

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
Existing `src/images/` artwork is retained and copied by the generator.

The generator and JSON schema are updated together; do not replace only the JSON
or only the generator. All four existing project slugs and the legacy
`/projects/#research-software` anchor are retained, along with existing project
resource URLs and case-study section anchors. A distinct `/software/` page has
been added.

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
