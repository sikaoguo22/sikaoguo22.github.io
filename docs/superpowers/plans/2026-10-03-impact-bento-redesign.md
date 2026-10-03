# Impact Bento Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the homepage an industry-facing, scannable "impact bento" and show Problem → Built → Result on every project card and case study.

**Architecture:** Content lives in `content/*.json`; `scripts/build.py` (stdlib only, f-string templates) renders `site/`; `src/styles.css` holds all styling. We add one JSON field (`impact`), two render helpers (`impact_block`, `bento_card`) plus `theme_cards`, and CSS for the new components. Tests are stdlib `unittest` over the built HTML.

**Tech Stack:** Python 3.10+ stdlib, hand-written HTML/CSS, no JS changes.

**Spec:** `docs/superpowers/specs/2026-10-03-impact-bento-redesign-design.md`

## Global Constraints

- No new dependencies, web fonts, CDNs, or analytics; system font stack stays.
- Every existing route and anchor (`current-research`, `biomolecular-assembly`, `research-infrastructure`, `research-software`, `context`, `approach`, `contribution`, `outcomes`, `resources`, `publications`) must still exist.
- Benchmark caveats stay visible: `96 CPUs` and `20,000-particle benchmark` on the homepage; ongoing sampler keeps "Ongoing research" and "evaluated systems".
- Impact copy must use exactly the text in the spec table (no new facts).
- All internal hrefs go through `link()` so `SITE_URL` subpath builds work.
- Match the existing code style: compact one-line f-string templates, `e()` for every content string.
- Build + test command (used in every task): `python3 scripts/build.py && python3 -m unittest discover -s tests -v`

## Review Focus

1. **375px phone width** — bento collapses to one column, impact label column stacks above text, no horizontal scroll. (Task 3 Step 6 visual check + `scrollWidth` assertion.)
2. **Dark theme** — Result row accent/ink text and status chips remain readable on `--surface`. (Task 3 Step 6.)
3. **Subpath build (`SITE_URL=https://example.org/preview`)** — `#work`, `/cv/`, and case-study links resolve. (Task 4 Step 2 runs the suite under a subpath build; `test_local_links_and_fragments` checks fragments.)
4. **Reduced motion** — hover lift on `.work-card` disabled under `prefers-reduced-motion`. (Task 3 CSS; verified by reading the rule.)
5. **Missing/empty impact field** in future JSON edits — build should fail loudly rather than render blanks. (Task 1 test asserts non-empty; `impact_block` indexes keys directly so a missing key raises `KeyError` at build time.)

---

### Task 1: Impact content

**Files:**
- Modify: `content/projects.json` (add `impact` to each of the 4 objects, after `"role"`)
- Test: `tests/test_site.py`

**Interfaces:**
- Produces: every project dict has `p['impact'] == {'problem': str, 'built': str, 'result': str}`.

- [ ] **Step 1: Write the failing test** — add to `WebsiteTests` in `tests/test_site.py` (before `if __name__`):

```python
    def test_projects_have_impact_summaries(self):
        projects=json.loads((ROOT/'content/projects.json').read_text())
        self.assertEqual(len(projects),4)
        for project in projects:
            with self.subTest(project=project['slug']):
                for key in ('problem','built','result'):
                    self.assertTrue(project['impact'][key].strip(),key)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 scripts/build.py && python3 -m unittest tests.test_site.WebsiteTests.test_projects_have_impact_summaries -v`
Expected: FAIL/ERROR with `KeyError: 'impact'`.

- [ ] **Step 3: Add the content** — insert after each project's `"role": ...,` line:

`inverse-kinematics-backbone-sampling`:
```json
    "impact": {
      "problem": "Loop-closure methods assume fixed endpoints, limiting exploration of fragments and disordered regions.",
      "built": "A C++ sampler with released-endpoint moves, spatial-hash clash detection, and an OpenMM all-atom validation workflow.",
      "result": "Broader exploration than tested generative samplers on the evaluated systems (ongoing work)."
    },
```
`nerdss-ionerdss-infrastructure`:
```json
    "impact": {
      "problem": "Turning molecular structures into simulation models was manual, and particle-based simulation needed to scale beyond a single process.",
      "built": "C++/MPI spatial domain decomposition for NERDSS and an automated structure-to-model Python pipeline (ioNERDSS).",
      "result": "≈90× speedup on 96 CPUs (20,000-particle benchmark) · 44,000+ structures processed · validated across 7 benchmark models."
    },
```
`cross-platform-gui-generation`:
```json
    "impact": {
      "problem": "Each scientific tool needed a separate implementation for PyMOL, VMD, and the web.",
      "built": "A specification-driven Python framework with JSON Schema validation, platform generators, and Linux/macOS CI.",
      "result": "9 structural-biology tools deployed across 3 platforms, one specification each."
    },
```
`mechanistic-assembly-models`:
```json
    "impact": {
      "problem": "Why do some molecular lattices stabilize while others fall apart or remodel?",
      "built": "Stochastic reaction-diffusion models of clathrin and HIV Gag lattices.",
      "result": "Reproduced experimental clathrin kinetics · identified an HIV binding-affinity range for stability and remodeling · published in eLife, PLOS Comp Biol, and Nature Communications."
    },
```

- [ ] **Step 4: Run full suite** — Run the build + test command. Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add content/projects.json tests/test_site.py
git commit -m "content: add problem/built/result impact summaries to projects"
```

---

### Task 2: Impact block on project cards and case studies

**Files:**
- Modify: `scripts/build.py` (add `impact_block` after `tags()`; edit `project_card()` and `case_page()`)
- Modify: `src/styles.css` (append impact + glance rules before the `@media(min-width:1600px)` line; add one rule inside `@media(max-width:600px)`)
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: `p['impact']` from Task 1.
- Produces: `impact_block(p: dict[str, Any]) -> str` returning `<dl class="impact">…</dl>` with three `<div>` rows; the result row is `<div class="impact-result">`.

- [ ] **Step 1: Write the failing test**

```python
    def test_impact_blocks_on_cards_and_case_studies(self):
        projects=json.loads((ROOT/'content/projects.json').read_text())
        self.assertEqual((SITE/'projects/index.html').read_text().count('class="impact"'),4)
        for project in projects:
            with self.subTest(project=project['slug']):
                page=(SITE/'projects'/project['slug']/'index.html').read_text()
                self.assertIn('At a glance',page)
                self.assertEqual(page.count('class="impact-result"'),1)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 scripts/build.py && python3 -m unittest tests.test_site.WebsiteTests.test_impact_blocks_on_cards_and_case_studies -v`
Expected: FAIL (`0 != 4`).

- [ ] **Step 3: Implement** — in `scripts/build.py`, after `def tags(...)`:

```python
def impact_block(p: dict[str, Any]) -> str:
    rows = [('Problem','problem',''),('Built','built',''),('Result','result',' class="impact-result"')]
    return '<dl class="impact">' + ''.join(f'<div{cls}><dt>{label}</dt><dd>{e(p["impact"][key])}</dd></div>' for label,key,cls in rows) + '</dl>'
```

In `project_card()`, replace `<p>{e(p['summary'])}</p>` with `{impact_block(p)}`.

In `case_page()`, change the final `return` to:

```python
    glance=f'<section class="container glance" aria-label="At a glance"><p class="eyebrow">At a glance</p>{impact_block(p)}</section>'
    return intro + glance + f'<div class="container case-layout">{side}{article}</div>' + contact()
```

Append to `src/styles.css` immediately before `@media(min-width:1600px)`:

```css
/* Impact-first summaries: problem, what was built, measured result. */
.impact{margin:18px 0 0;display:grid;gap:11px;font-size:.88rem}
.impact>div{display:grid;grid-template-columns:4.6rem 1fr;gap:14px;align-items:baseline}
.impact dt{font-size:.64rem;letter-spacing:.12em;text-transform:uppercase;font-weight:650;color:var(--muted)}
.impact dd{margin:0;color:var(--muted);line-height:1.55}
.impact .impact-result dt{color:var(--accent)}
.impact .impact-result dd{color:var(--ink);font-weight:600}
.glance{padding-bottom:10px}
.glance .impact{max-width:880px;margin-top:12px;padding:22px 26px;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:12px;background:var(--surface);font-size:.95rem}
```

Inside the existing `@media(max-width:600px){ ... }` block, add:

```css
 .impact>div{grid-template-columns:1fr;gap:2px}.glance .impact{padding:18px}
```

- [ ] **Step 4: Run full suite** — build + test command. Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/build.py src/styles.css tests/test_site.py
git commit -m "feat: show problem/built/result on project cards and case studies"
```

---

### Task 3: Homepage bento, compact hero, metrics, research themes move

**Files:**
- Modify: `scripts/build.py` (`home()`, `research_page()`; add `theme_cards()` and `bento_card()`)
- Modify: `src/styles.css` (hero/stat tweaks, bento rules, media queries, reduced motion)
- Test: `tests/test_site.py`

**Interfaces:**
- Consumes: `impact_block(p)` (Task 2), `by_slug`, `diagram()`, `text_link()`, `button()`, `section_heading()`.
- Produces: `theme_cards() -> str`; `bento_card(p: dict[str, Any], cls: str) -> str` where `cls` ∈ `{'work-card-wide','work-card-narrow','work-card-half'}`.

- [ ] **Step 1: Write the failing test**

```python
    def test_homepage_bento_and_research_themes(self):
        home=(SITE/'index.html').read_text()
        self.assertIn('work',self.docs[SITE/'index.html'].ids)
        self.assertEqual(home.count('<article class="work-card'),4)
        self.assertEqual(home.count('class="impact"'),4)
        self.assertIn('View CV',home)
        self.assertNotIn('theme-card',home)
        self.assertEqual((SITE/'research/index.html').read_text().count('class="theme-card"'),3)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 scripts/build.py && python3 -m unittest tests.test_site.WebsiteTests.test_homepage_bento_and_research_themes -v`
Expected: FAIL (`'work' not found`).

- [ ] **Step 3: Implement Python** — in `scripts/build.py`, add before `def home()`:

```python
def theme_cards() -> str:
    return '<div class="theme-grid">' + ''.join(f'<article class="theme-card"><div class="theme-top"><span class="theme-number">0{i+1}</span><span class="theme-tag">{e(x["tag"])}</span></div><h3>{e(x["question"])}</h3><p>{e(x["text"])}</p>{text_link(x["href"],x["title"])}</article>' for i,x in enumerate(site['researchThemes'])) + '</div>'


def bento_card(p: dict[str, Any], cls: str) -> str:
    chip = 'status-chip status-ongoing' if p['status'] == 'Ongoing research' else 'status-chip'
    visual = diagram(p['visual']) if cls == 'work-card-wide' else ''
    return f'''<article class="work-card {cls}"><div class="work-card-body"><div class="work-card-top"><p class="eyebrow">{e(p['category'])}</p><span class="{chip}">{e(p['status'])}</span></div><h3><a href="{link('/projects/'+p['slug']+'/')}">{e(p['shortTitle'])}</a></h3>{impact_block(p)}{text_link('/projects/'+p['slug']+'/','Read case study')}</div>{visual}</article>'''
```

In `home()`:
- delete the `themes = ...` line;
- add `work = ''.join(bento_card(by_slug[slug],cls) for slug,cls in [('nerdss-ionerdss-infrastructure','work-card-wide'),('cross-platform-gui-generation','work-card-narrow'),('inverse-kinematics-backbone-sampling','work-card-half'),('mechanistic-assembly-models','work-card-half')])`;
- replace `{button('/research/','Explore research',True)}{button('/software/','View software')}` with `{button('#work','See my work',True)}{button('/cv/','View CV')}`;
- replace the whole `<section class="section" aria-label="Research directions">…</section>` line with:

```python
<section class="section" id="work" aria-label="Selected work">{section_heading('Selected work','What I built, and what it achieved.',('/projects/','All projects'))}<div class="bento">{work}</div></section></div>
```

(The `</div>` closes the container opened at the hero, as the deleted line did.)

In `research_page()`, compute `themes = '' if all_projects else f'<section class="section" aria-label="Research directions">{section_heading("Research directions","Questions that drive my work.")}{theme_cards()}</section>'` and change the return to insert `{themes}` right after `<div class="container">`.

- [ ] **Step 4: Implement CSS** — in `src/styles.css`:

Change `.hero{padding:72px 0 62px;` → `.hero{padding:56px 0 48px;` and `.hero h1{margin:23px 0 23px;` → `.hero h1{margin:20px 0 20px;`.

Replace the `.stat-value{...}` rule with:
```css
.stat::before{content:"";display:block;width:28px;height:3px;border-radius:2px;background:var(--accent);margin-bottom:14px}
.stat-value{display:block;font-size:2.55rem;line-height:1.15;font-weight:650;letter-spacing:-.045em;margin-bottom:8px;font-variant-numeric:tabular-nums}
```

Append before `@media(min-width:1600px)` (after the Task 2 block):
```css
/* Homepage bento of selected work. */
.bento{display:grid;grid-template-columns:repeat(12,1fr);gap:22px}
.work-card{grid-column:span 6;display:flex;flex-direction:column;min-width:0;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);overflow:hidden;transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease}
.work-card:hover{transform:translateY(-3px);border-color:var(--accent);box-shadow:var(--shadow)}
.work-card-wide{grid-column:span 8;display:grid;grid-template-columns:1fr 1fr}
.work-card-narrow{grid-column:span 4}
.work-card-wide .diagram{border-bottom:0;border-left:1px solid var(--line);display:flex;flex-direction:column;justify-content:center}
.work-card-body{padding:26px;display:flex;flex-direction:column;flex:1}
.work-card-top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.work-card h3{font-size:1.38rem;margin-top:10px}
.work-card .text-link{margin-top:auto;padding-top:22px;font-size:.83rem}
.status-chip{font-size:.66rem;font-weight:650;letter-spacing:.04em;padding:3px 10px;border-radius:999px;background:var(--wash);color:var(--accent);white-space:nowrap}
.status-ongoing{background:var(--wash-blue);color:var(--muted)}
```

Inside `@media(max-width:1050px){`: add ` .work-card-wide{grid-column:span 12}.work-card-narrow,.work-card-half{grid-column:span 6}`

Inside `@media(max-width:780px){`: add ` .bento{gap:18px}.work-card,.work-card-wide,.work-card-narrow,.work-card-half{grid-column:span 12}.work-card-wide{display:flex;flex-direction:column-reverse}.work-card-wide .diagram{border-left:0;border-bottom:1px solid var(--line)}`

Inside `@media(prefers-reduced-motion:reduce){`: add `.work-card:hover{transform:none}`.

- [ ] **Step 5: Run full suite** — build + test command. Expected: all PASS (incl. `test_ongoing_work_and_benchmark_scope`, since stat details and the NERDSS result keep `96 CPUs`).

- [ ] **Step 6: Visual check** — `preview_start` with `.claude/launch.json` entry `site` (serves `site/` on :8000). Screenshot `/` at desktop width, at `resize_window` preset `mobile`, and with `colorScheme: dark`. In mobile, run JS `document.documentElement.scrollWidth <= innerWidth` → expect `true`. Also screenshot `/research/` and one case study. Fix any overflow/contrast issue before committing; reset with preset `desktop`.

- [ ] **Step 7: Commit**

```bash
git add scripts/build.py src/styles.css tests/test_site.py
git commit -m "feat: impact bento homepage with compact hero and metric tiles"
```

---

### Task 4: Docs and full verification

**Files:**
- Modify: `README.md` (the "Included" bullet describing the homepage)

- [ ] **Step 1: Update README** — replace the bullet beginning `- A personal homepage with portrait, research questions, scoped results, software,` (and its continuation line) with:

```markdown
- A personal homepage with portrait, scoped results, an impact-first "selected work"
  bento (problem → built → result), selected papers, and a contact section.
- Research questions on the Research page; "At a glance" impact summaries on every
  project card and case study (`impact` field in `content/projects.json`).
```

- [ ] **Step 2: Verify both URL configurations**

```bash
python3 scripts/build.py && python3 -m unittest discover -s tests -v
SITE_URL=https://example.org/preview python3 scripts/build.py && SITE_URL=https://example.org/preview python3 -m unittest discover -s tests -v
python3 scripts/build.py
```
Expected: all tests PASS in both runs. If Playwright is installed (`python3 -c "import playwright"`), also run `python3 tests/browser_smoke.py` and expect it to pass.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: describe impact bento homepage"
```
