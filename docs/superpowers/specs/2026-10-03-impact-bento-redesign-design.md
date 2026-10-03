# Impact bento redesign — design

Date: 2026-10-03 · Branch: `claude/impact-bento-redesign`

## Intent

- **Audience (stated):** industry hiring managers for research scientist / research
  software engineer roles.
- **Goal:** a visitor can see what Sikao built and what it achieved within one
  scroll of the homepage, without reading case studies.
- **Content change (stated):** impact-first project cards — Problem → Built → Result.
- **Out of scope (declined):** availability banner, news feed, homepage skills strip.
- **Constraints (existing, kept):** standard-library Python generator, JSON content,
  system fonts, no runtime CDN/analytics, light/dark themes, works without JS,
  existing URLs/anchors preserved, benchmark caveats and "ongoing" labels kept
  visible, no facts beyond those already in the repo content.

## Content

Add `impact: {problem, built, result}` to every entry in `content/projects.json`,
derived only from existing `context`, `contributions`, and `validation` text:

| Slug | Problem | Built | Result |
|---|---|---|---|
| nerdss-ionerdss-infrastructure | Turning molecular structures into simulation models was manual, and particle-based simulation needed to scale beyond a single process. | C++/MPI spatial domain decomposition for NERDSS and an automated structure-to-model Python pipeline (ioNERDSS). | ≈90× speedup on 96 CPUs (20,000-particle benchmark) · 44,000+ structures processed · validated across 7 benchmark models. |
| cross-platform-gui-generation | Each scientific tool needed a separate implementation for PyMOL, VMD, and the web. | A specification-driven Python framework with JSON Schema validation, platform generators, and Linux/macOS CI. | 9 structural-biology tools deployed across 3 platforms, one specification each. |
| inverse-kinematics-backbone-sampling | Loop-closure methods assume fixed endpoints, limiting exploration of fragments and disordered regions. | A C++ sampler with released-endpoint moves, spatial-hash clash detection, and an OpenMM all-atom validation workflow. | Broader exploration than tested generative samplers on the evaluated systems (ongoing work). |
| mechanistic-assembly-models | Why do some molecular lattices stabilize while others fall apart or remodel? | Stochastic reaction-diffusion models of clathrin and HIV Gag lattices. | Reproduced experimental clathrin kinetics · identified an HIV binding-affinity range for stability and remodeling · published in eLife, PLOS Comp Biol, and Nature Communications. |

The `researchThemes` in `content/site.json` move from the homepage to `/research/`.

## Homepage

1. **Hero (compact):** name, eyebrow, existing two-line headline, description.
   Buttons: **See my work** (`#work`, primary) and **View CV** (`/cv/`).
   Tech line and social links unchanged. Reduced vertical padding.
2. **Metric tiles:** existing three `stats`, larger tabular numerals, accent top bar,
   caveat detail always visible, each still a link.
3. **Selected work bento** (`<section id="work">`): four project cards on a
   12-column grid. NERDSS + ioNERDSS spans 8 columns with its illustration;
   AutoCLIP spans 4; sampler and assembly models span 6 each. Each card: status
   chip, category, title (link to case study), impact block, "Read case study".
   Order: NERDSS, AutoCLIP, sampler, assembly.
4. Selected publications, About strip, contact — unchanged content, tighter spacing.

## Shared component: impact block

`impact_block(p)` renders a `<dl class="impact">` with three rows
(`dt` Problem/Built/Result, `dd` text). The Result row has class `impact-result`
and accent emphasis. Used by the bento cards, `project_card()` (Research, All
projects pages), and `case_page()` as an "At a glance" box under the header.

## Other pages

- `/research/`: research-theme cards section above the project grid.
- `/projects/`, `/research/`: project cards include the impact block.
- `/projects/<slug>/`: "At a glance" impact box after the case header; all
  existing section anchors unchanged.
- `/software/`: unchanged (its cards already lead with evidence lines).

## Visual system (`src/styles.css`)

Keep palette tokens, add: `.bento` grid (12 cols desktop, 1 col ≤ 760px,
2 cols 761–1024px with the wide card spanning both); `.work-card` surface with
1px border, hover lift (disabled under `prefers-reduced-motion`) and accent
border; `.status-chip`; `.impact` grid (label column ~5.5rem, uppercase small
labels); `.stat` upgrades. Dark theme uses existing tokens only.

## Testing

Extend `tests/test_site.py`:
- every project in `projects.json` has non-empty `impact.problem/built/result`;
- homepage has `id="work"` with exactly 4 `work-card` articles, each with an
  impact block, and a link to `/cv/`;
- `/research/` contains the research-theme cards;
- each case study contains an `impact` block.
Existing tests (links, anchors, caveats, ongoing labels) must keep passing.
Visual check in the preview: desktop, 375px mobile, dark mode.
