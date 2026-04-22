---
layout: base.njk
title: Data Sources
description: Source data, fetch dates, and downloadable files for the Berkeley interim housing analysis.
scripts:
  - /assets/js/data-sources.js
---

# Data Sources

## Source Data

All source data comes from the City of Berkeley's public safety open data.

| Dataset | Source |
|---------|--------|
| Police Calls for Service | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |
| Police Stop Data (RIPA) | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |
| Council Districts | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |

---

## Build Information

<div id="build-meta" class="build-meta">
  <p>Loading build metadata…</p>
</div>

---

## Downloads

Processed files ready for your own analysis:

| File | Description |
|------|-------------|
| [site_summary.csv]({{ '/downloads/site_summary.csv' | url }}) | One row per site — address, opening date, program type |
| [site_level_results.csv]({{ '/downloads/site_level_results.csv' | url }}) | Pre/post non-traffic call counts by site |
| [opening_dates.csv]({{ '/downloads/opening_dates.csv' | url }}) | Verified opening dates |
| [methodology_inputs.csv]({{ '/downloads/methodology_inputs.csv' | url }}) | Study parameters used in the pipeline |

### Chart Data

| File | Description |
|------|-------------|
| [pre_post_site_nontraffic_calls.csv]({{ '/data/charts/pre_post_site_nontraffic_calls.csv' | url }}) | Pre/post counts by site |
| [zone_comparison_nontraffic_calls.csv]({{ '/data/charts/zone_comparison_nontraffic_calls.csv' | url }}) | Zone spillover results |
| [rolling_3mo_yoy_nontraffic_calls.csv]({{ '/data/charts/rolling_3mo_yoy_nontraffic_calls.csv' | url }}) | Rolling YoY trend data |
| [corridor_controls.csv]({{ '/data/charts/corridor_controls.csv' | url }}) | Control corridor trend data |

---

## Processing Notes

- All geographic filtering uses 4326 (WGS84) coordinates projected to UTM Zone 10N for distance calculations.
- Non-traffic call classification uses keyword matching on the `cvlegend` field. See `study_parameters.yml` for the full keyword list.
- Opening dates are approximate and based on publicly available records. See `sites.yml` to review or update them.
- The pipeline is fully reproducible from source data. See the [README](https://github.com/ericdf/berkeley-corridor-index) for instructions.
