# berkeley-corridor-index

Berkeley public safety data analysis — non-partisan, open source.

**Live site:** https://ericfriedman.github.io/berkeley-corridor-index/

*(Replace `ericfriedman` with your GitHub username if different.)*

---

## Building the site

### Prerequisites

```bash
# Python virtualenv
ln -sfn ~/.virtualenvs/motel_conversions .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node
npm install
```

### Normal working session

```bash
# Run analysis pipeline, then build the site
source .venv/bin/activate
python analysis/run_pipeline.py
npm run build

# Serve locally at http://localhost:8080
npm run dev
```

The pipeline reads staged source data from `data/raw/current/`, runs all analysis scripts, and writes chart CSVs and map GeoJSONs to `data/processed/`. The Eleventy build then copies those into the site output.

### Refreshing source data from the portal

```bash
source .venv/bin/activate
python analysis/src/fetch_portal_data.py   # downloads to data/raw/current/
python analysis/run_pipeline.py
npm run build
```

Portal endpoints are configured in `analysis/config/data_sources.yml`.

---

## Deploying to GitHub Pages

Push to `main`. The GitHub Actions workflow (`.github/workflows/deploy.yml`) builds the site with the correct path prefix and deploys it automatically. No manual steps after initial repo setup.

**One-time GitHub setup:**
1. Create a new repository named `berkeley-corridor-index`
2. Go to **Settings → Pages → Source** and select **GitHub Actions**
3. Push this repo to `main`

The workflow sets `ELEVENTY_PREFIX=/berkeley-corridor-index/` so all asset and navigation paths resolve correctly under the subdirectory.

---

## Repository layout

```
analysis/
  config/
    sites.yml              ← site addresses, coordinates, opening dates
    study_parameters.yml   ← zone radii, pre/post window, call-type keywords
    data_sources.yml       ← portal endpoints
  src/                     ← analysis scripts
  run_pipeline.py          ← orchestrator

data/
  raw/current/             ← staged source files (not committed)
  interim/                 ← normalized parquet files + geocode cache (not committed)
  processed/
    charts/                ← chart CSV outputs (committed)
    maps/                  ← zone and site GeoJSON outputs (committed)
    downloads/             ← public download CSVs (committed)
    metadata/              ← build.json (committed)

site/
  src/                     ← Eleventy source (Markdown + Nunjucks)
    _includes/base.njk     ← shared layout
    assets/                ← CSS and chart JS
    site-profiles/         ← one page per study site
  public/                  ← built output (not committed)

.github/workflows/
  deploy.yml               ← builds and deploys to GitHub Pages on push to main
```

---

## Sites studied

| Site | Program type | Opening date |
|------|-------------|--------------|
| 1461 University Ave | Interim housing | 2021-07-01 |
| 1619 University Ave | Reentry / supportive housing | 2023-07-31 |
| 1761 University Ave | Interim housing | 2026-02-01 |
| 1620 San Pablo Ave (Golden Bear Inn) | Permanent supportive housing | 2023-01-01 |

Opening dates are in `analysis/config/sites.yml`.
