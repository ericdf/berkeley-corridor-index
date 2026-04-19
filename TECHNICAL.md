# Berkeley Interim Housing Site Analysis — Technical Specification

## Project Goal

Build a public-facing GitHub Pages website presenting a Berkeley policy analysis of four University Avenue converted motel / interim housing sites.

The site must be:

- Static
- Fast
- Credible
- Neutral in tone
- Easy for journalists and residents to navigate
- Reproducible from source data and pipeline outputs

The site should communicate findings using charts, maps, downloadable CSVs, and clear methodology notes.

---

## Core Subject Matter

Study locations:

- 1461 University Ave
- 1512 University Ave
- 1619 University Ave
- 1761 University Ave

Primary analytical focus:

- Non-traffic police calls for service
- 12-month pre / post comparisons by site opening date
- Adjacent-block spillover effects
- Wider nearby area comparisons
- Rolling 3-month year-over-year trends
- Rough corridor controls:
  - North Shattuck
  - South Telegraph

The project evaluates association and timing patterns, not proof of causation.

---

## Required Technology Stack

### Frontend / Site

- Eleventy (11ty)
- Nunjucks templates
- Markdown content pages
- Plain CSS (custom design system)
- Observable Plot for charts
- Leaflet for maps

### Data / Analysis

- Python 3.x
- pandas
- geopandas
- shapely
- pyyaml

### Deployment

- GitHub Actions
- GitHub Pages

---

## Local Python Environment

A virtualenv already exists at:

`~/.virtualenvs/motel_conversions`

Create a project-local symlink:

```bash
ln -s ~/.virtualenvs/motel_conversions .venv
```

Use:

```bash
source .venv/bin/activate
```

Do not recreate another virtualenv unless explicitly instructed.

---

## Repository Structure

```text
motel-conversions-site/
├─ README.md
├─ package.json
├─ requirements.txt
├─ eleventy.config.js
├─ .gitignore
├─ .venv -> ~/.virtualenvs/motel_conversions
├─ analysis/
│  ├─ config/
│  │  ├─ study_parameters.yml
│  │  ├─ data_sources.yml
│  │  └─ sites.yml
│  ├─ src/
│  │  ├─ fetch_portal_data.py
│  │  ├─ stage_inputs.py
│  │  ├─ validate_inputs.py
│  │  ├─ build_zones.py
│  │  ├─ compute_pre_post.py
│  │  ├─ compute_spillover.py
│  │  ├─ compute_rolling_yoy.py
│  │  ├─ compute_controls.py
│  │  ├─ export_site_data.py
│  │  └─ utils.py
│  └─ run_pipeline.py
├─ data/
│  ├─ raw/
│  │  ├─ current/
│  │  ├─ source_snapshots/
│  │  └─ metadata/
│  ├─ interim/
│  └─ processed/
│     ├─ charts/
│     ├─ maps/
│     ├─ downloads/
│     └─ metadata/
├─ site/
│  ├─ src/
│  │  ├─ index.md
│  │  ├─ findings.md
│  │  ├─ methodology.md
│  │  ├─ maps.md
│  │  ├─ data-sources.md
│  │  ├─ site-profiles/
│  │  ├─ _data/
│  │  ├─ _includes/
│  │  └─ assets/
│  └─ public/
└─ .github/
   └─ workflows/
      ├─ ci.yml
      └─ deploy-pages.yml
```

---

## Design Requirements

Style should resemble restrained data journalism.

Use:

- strong typography
- high readability
- muted palette
- minimal ornament
- generous whitespace
- charts with low visual clutter
- clear legends
- source notes
- mobile responsive layout

Avoid:

- splashy marketing visuals
- animated counters
- opinionated rhetoric
- excessive JS frameworks

---

## Required Pages

### 1. Home

Purpose:

- Explain project scope
- Summarize major findings
- Route users quickly

Include:

- Intro summary
- Key charts preview
- Site cards
- Navigation to methodology and data downloads

### 2. Findings

Main evidence page.

Include:

- Pre/post results by site
- Spillover findings
- Control corridor comparisons
- Rolling trend context
- Limits of interpretation

### 3. Methodology

Use the provided methodology document as source material.

Include:

- Why non-traffic calls were used
- Opening-date based pre/post windows
- Zone definitions
- Control corridors
- Rolling YoY method
- Limits of study

### 4. Site Profiles

One page per site:

- Address
- Program type if available
- Opening date
- Map
- Charts
- Downloads

Pages:

- /site-profiles/1461-university/
- /site-profiles/1512-university/
- /site-profiles/1619-university/
- /site-profiles/1761-university/

### 5. Maps

Include:

- Site markers
- Council districts
- Zone overlays
- Optional layer toggles

### 6. Data Sources

Include:

- Source portal links
- Fetch dates
- Processing notes
- Downloadable derived files

---

## Required Data Pipeline Behavior

Main command:

```bash
python analysis/run_pipeline.py
```

Pipeline must:

1. Load staged raw files
2. Validate schemas
3. Normalize fields
4. Build study zones
5. Assign incidents to zones
6. Compute pre/post metrics
7. Compute spillover metrics
8. Compute rolling YoY metrics
9. Compute control corridor metrics
10. Export chart CSVs
11. Export map GeoJSON
12. Export downloadable tables
13. Write build metadata

---

## Optional Source Refresh

```bash
python analysis/src/fetch_portal_data.py
python analysis/src/stage_inputs.py
```

Site builds must not depend on live portal availability.

---

## Required Processed Outputs

### Charts

```text
data/processed/charts/pre_post_site_nontraffic_calls.csv
data/processed/charts/zone_comparison_nontraffic_calls.csv
data/processed/charts/rolling_3mo_yoy_nontraffic_calls.csv
data/processed/charts/corridor_controls.csv
```

### Maps

```text
data/processed/maps/sites.geojson
data/processed/maps/site_block_zones.geojson
data/processed/maps/adjacent_block_zones.geojson
data/processed/maps/wider_nearby_zones.geojson
data/processed/maps/council_districts_simplified.geojson
```

### Downloads

```text
data/processed/downloads/site_summary.csv
data/processed/downloads/site_level_results.csv
data/processed/downloads/opening_dates.csv
data/processed/downloads/methodology_inputs.csv
```

---

## Required Charts

### A. Pre/Post Comparison

For each site:

- 12 months before
- 12 months after

Use:

- dot plot or grouped bar chart

### B. Zone Spillover

Compare:

- Site block
- Adjacent blocks
- Wider nearby area

### C. Rolling 3-Month YoY

Example:

- Feb-Apr 2025 vs Feb-Apr 2026

Use line chart with site opening marker.

### D. Control Corridors

Compare trends for:

- North Shattuck
- South Telegraph

---

## Mapping Rules

Use Leaflet.

Maps should be lightweight.

Use simplified GeoJSON.

Show:

- site point
- zone polygons
- district boundaries

---

## Content Tone Rules

Use:

- factual language
- neutral phrasing
- evidence-focused summaries
- explicit limitations

Do not use:

- advocacy language
- emotionally loaded framing
- causal overclaiming

Use phrases like:

- increased after opening
- associated with higher call volume
- patterns varied by site
- results do not establish causation

---

## NPM Scripts

```json
{
  "scripts": {
    "dev": "eleventy --serve",
    "build": "eleventy",
    "analyze": "python analysis/run_pipeline.py",
    "refresh-data": "python analysis/src/fetch_portal_data.py && python analysis/src/stage_inputs.py",
    "full-build": "npm run analyze && npm run build",
    "refresh-and-build": "npm run refresh-data && npm run analyze && npm run build"
  }
}
```

---

## GitHub Actions Requirements

### ci.yml

On push / PR:

- setup Python
- install requirements
- setup Node
- install npm packages
- run pipeline
- run site build

### deploy-pages.yml

On push to main:

- run pipeline
- build Eleventy site
- deploy to GitHub Pages

---

## Build Metadata

Generate:

```text
data/processed/metadata/build.json
```

Include:

- build timestamp
- git commit SHA
- data refresh date
- study period
- source versions

Expose this in site footer and Data Sources page.

---

## Acceptance Criteria

1. `npm run full-build` succeeds locally
2. GitHub Actions deploys automatically
3. All required pages exist
4. Charts render correctly
5. Maps render correctly
6. CSV downloads work
7. Site is mobile responsive
8. Tone is neutral
9. Claims align with exported data
10. Build is reproducible

---

## Build Order

1. scaffold repo
2. Eleventy base layout
3. Python pipeline skeleton
4. chart CSV exports
5. Findings page
6. Site profile pages
7. Maps page
8. Data downloads
9. CI/CD
10. polish

---

## Important Constraints

- Prefer precomputed outputs over browser computation
- Keep JavaScript light
- Keep code readable
- Favor larger fonts for older readers
- Document commands in README
- Use semantic HTML
- Optimize for public credibility
