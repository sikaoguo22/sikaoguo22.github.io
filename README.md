# Sikao Guo — Personal Research & Engineering Website

A dependency-free static portfolio focused on computational biophysics, molecular modeling, and scientific software engineering.

## Included

- Responsive homepage organized around a stable computational-biophysics identity, research vision, selected work, quantified impact, publications, biography, and collaboration CTA.
- Four detailed project case studies:
  - cross-platform scientific GUI generation;
  - inverse-kinematics protein backbone sampling;
  - NERDSS and ioNERDSS infrastructure;
  - mechanistic models of membrane-associated assembly.
- Filterable publications page.
- Dedicated research overview and About page.
- Web CV with experience, education, publications, software, and technical strengths.
- Light and dark themes, mobile navigation, accessible focus states, reduced-motion support, metadata, sitemap, and robots file.
- Machine-readable Person, ScholarlyArticle, and SoftwareSourceCode JSON-LD.
- GitHub Pages deployment workflow.

## Project structure

```text
.
├── content/                 # Site, project, and publication data
├── src/
│   ├── images/              # Editable SVG artwork and optimized runtime exports
│   └── styles.css           # Global responsive design
├── scripts/build.py         # Dependency-free static-site generator
├── site/                    # Built site; deploy this directory
└── .github/workflows/       # GitHub Pages deployment
```

## Edit content

The main content is stored in:

- `content/site.json`
- `content/projects.json`
- `content/publications.json`

The ongoing protein-backbone project is deliberately labeled **Ongoing work** and does not distribute unfinished manuscript figures or unpublished PDFs.

## Build locally

Python 3.10 or newer is sufficient. The website build uses only the Python standard library.

```bash
python3 scripts/build.py
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000`.

To change canonical URLs and sitemap entries:

```bash
SITE_URL=https://example.com python3 scripts/build.py
```

`SITE_URL` may include a repository path, such as `https://username.github.io/repository`.

## Deploy with GitHub Pages

1. Create a repository. For the root profile site, use `sikaoguo22.github.io`; otherwise any repository name works.
2. Push this project to the `main` branch.
3. In **Settings → Pages**, choose **GitHub Actions** as the source.
4. For a project repository or custom domain, add a repository variable named `SITE_URL` containing the full public base URL.
5. Run the included **Deploy personal website** workflow or push to `main`.

The workflow rebuilds the site, uploads the `site/` directory, and deploys it as the Pages artifact.

## Before publishing

- Confirm the current position dates, location, and availability wording.
- Confirm that all ongoing-work descriptions are approved for public use.
- Replace the default GitHub Pages URL with the final custom domain when selected.
- Review email, GitHub, LinkedIn, Google Scholar, ORCID, DOI, and repository links.
- Run the site locally at desktop and mobile widths.

## Design notes

The site uses project-specific scientific artwork rather than stock imagery or third-party fonts. Editable project composites remain as SVG sources; the deployed pages use responsive 800 px and 1600 px lossless WebP exports, plus a 1200 × 630 PNG social card. Research and software coexist as labeled parts of one portfolio. No analytics, cookies, external JavaScript, or runtime dependencies are included.
