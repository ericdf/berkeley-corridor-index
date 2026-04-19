# Berkeley Interim Housing Site Analysis

A public-facing data journalism site examining whether four motel and hotel conversions in Berkeley were associated with changes in nearby non-traffic police calls for service.

## Sites

| Site | Program type | Opening date |
|------|-------------|--------------|
| 1461 University Ave | Interim housing / shelter | 2021-07-01 |
| 1619 University Ave | Reentry / supportive housing | 2023-07-31 |
| 1761 University Ave | Interim housing | 2026-02-01 (verify) |
| 1620 San Pablo Ave (Golden Bear Inn) | Permanent supportive housing | 2023-01-01 |

Opening dates are in `analysis/config/sites.yml`. Verify before publication.

---

## Setup (first time)

```bash
# Python virtualenv — symlink to existing env, do not recreate
ln -sfn ~/.virtualenvs/motel_conversions .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node
npm install
```

---

## Typical workflow

### 1. Stage raw data files

Copy source GeoJSON files into `data/raw/current/`:

```
data/raw/current/callsforservice_csv.geojson   ← Berkeley PD calls for service
data/raw/current/council_districts.geojson     ← Berkeley council district boundaries
```

These are not committed to the repo. Obtain from the Berkeley open data portal or local cache.

### 2. Run the analysis pipeline

```bash
source .venv/bin/activate
python analysis/run_pipeline.py
```

Pipeline steps:

| Step | Script | Notes |
|------|--------|-------|
| 1. Stage inputs | `stage_inputs.py` | Reads GeoJSON, normalizes fields |
| 2. Geocode calls | `geocode_calls.py` | Census batch geocoder; results cached in `data/interim/address_coords_cache.parquet` |
| 3. Validate inputs | `validate_inputs.py` | Prints date range and row count |
| 4. Build zones | `build_zones.py` | Creates buffered zone polygons per site |
| 5. Compute pre/post | `compute_pre_post.py` | 12-month before/after counts |
| 6. Compute spillover | `compute_spillover.py` | Counts by zone ring (site block / adjacent / wider) |
| 7. Compute rolling YoY | `compute_rolling_yoy.py` | 3-month windows compared year-over-year |
| 8. Compute controls | `compute_controls.py` | Same rolling YoY for North Shattuck and South Telegraph |
| 9. Export site data | `export_site_data.py` | Downloads, build metadata |

**Geocoding cache:** The first pipeline run submits all unique block addresses (~5,800) to the Census batch geocoder. This takes about 30 seconds. Subsequent runs use the cache and are instant. The cache is at `data/interim/address_coords_cache.parquet` — do not delete it unnecessarily.

**Insufficient post-period data:** Sites where less than 50% (6 months) of the post-window falls within the available data are flagged. The pipeline logs the partial count and an annualized estimate for operator review. The public-facing CSV has `post_count = null` and `post_sufficient = false` for these sites.

### 3. Build the site

```bash
npm run build
```

Output goes to `site/public/`.

### 4. Serve locally

```bash
npm run dev
```

Then open `http://localhost:8080`.

---

## Combined commands

```bash
# Full pipeline + site build (normal working session)
source .venv/bin/activate && python analysis/run_pipeline.py && npm run build

# Serve after building
npm run dev

# Or use the npm shortcuts (requires venv already active for analyze step)
npm run full-build        # analyze + build
npm run refresh-and-build # fetch from portal + analyze + build (portal must be online)
```

---

## Refreshing source data from the portal

When the Berkeley open data portal is available:

```bash
source .venv/bin/activate
python analysis/src/fetch_portal_data.py   # downloads to data/raw/current/
python analysis/src/stage_inputs.py        # normalizes and writes interim files
python analysis/run_pipeline.py            # full analysis
npm run build
```

Portal URLs are in `analysis/config/data_sources.yml`. Verify the dataset IDs before running — the portal endpoints changed from the original spec.

---

## Adding or updating a site

1. Edit `analysis/config/sites.yml` — add/modify the site entry with correct lat/lon and opening date.
2. If the site is on a new street, geocoding will handle it automatically on the next pipeline run.
3. Add a site profile page in `site/src/site-profiles/` using an existing page as a template.
4. Re-run the pipeline and rebuild the site.

---

## Updating opening dates

Opening dates are configured in `analysis/config/sites.yml`. After editing:

```bash
python analysis/run_pipeline.py   # recomputes all metrics
npm run build
```

No geocoding is re-done (cache is not affected by opening date changes).

---

## Repository layout

```
analysis/
  config/
    sites.yml              ← site addresses, coordinates, opening dates
    study_parameters.yml   ← zone radii, pre/post window, YoY window, call-type keywords
    data_sources.yml       ← portal endpoints and staged filenames
  src/
    fetch_portal_data.py   ← optional: download from portal
    stage_inputs.py        ← read GeoJSON, normalize fields
    geocode_calls.py       ← Census batch geocoder with cache
    validate_inputs.py     ← schema and date-range checks
    build_zones.py         ← buffered zone polygons
    compute_pre_post.py    ← 12-month pre/post counts
    compute_spillover.py   ← counts by zone ring
    compute_rolling_yoy.py ← 3-month rolling YoY
    compute_controls.py    ← control corridor YoY
    export_site_data.py    ← download CSVs, build metadata
    utils.py               ← shared paths and helpers
  run_pipeline.py          ← orchestrator

data/
  raw/current/             ← staged source files (not committed)
  interim/                 ← normalized parquet files + geocode cache
  processed/
    charts/                ← chart CSV outputs (copied to site)
    maps/                  ← zone and site GeoJSON outputs (copied to site)
    downloads/             ← public download CSVs
    metadata/              ← build.json (copied to site)

site/
  src/                     ← Eleventy source
    _includes/             ← Nunjucks layouts
    _data/                 ← global data (sites.yml, build.json)
    assets/css/            ← main.css
    assets/js/             ← charts-findings.js, map.js, site-profile.js
    site-profiles/         ← one .md per site
  public/                  ← built output (not committed)

.github/workflows/
  ci.yml                   ← build check on every push/PR
  deploy-pages.yml         ← deploy to GitHub Pages on push to main
```

---

## Deployment

Push to `main`. GitHub Actions runs the pipeline and deploys to GitHub Pages automatically. Set `SOCRATA_APP_TOKEN` as a repository secret if you have one (improves portal rate limits).

Before deploying, update `site/src/_data/site.json` with the correct GitHub repo slug.
