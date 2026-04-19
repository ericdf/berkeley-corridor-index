---
layout: base.njk
title: Data Sources
description: Source data, fetch dates, and downloadable files for the Berkeley interim housing analysis.
---

# Data Sources

## Source Data

All source data comes from the City of Berkeley's public open data portal.

| Dataset | Portal link | Format |
|---------|-------------|--------|
| Police Calls for Service | [data.cityofberkeley.info](https://data.cityofberkeley.info/Public-Safety/Berkeley-PD-Calls-for-Service/k2nh-s5h5) | CSV / JSON |
| Police Stop Data | [data.cityofberkeley.info](https://data.cityofberkeley.info/Public-Safety/Berkeley-PD-Stop-Data/sg85-5hbb) | CSV / JSON |
| Arrest Data | [data.cityofberkeley.info](https://data.cityofberkeley.info/Public-Safety/Berkeley-PD-Arrests/6p4x-gyij) | CSV / JSON |
| Council Districts | [data.cityofberkeley.info](https://data.cityofberkeley.info/Boundaries/City-of-Berkeley-Council-Districts/qnky-x6t5) | GeoJSON |

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
| [site_summary.csv](/downloads/site_summary.csv) | One row per site — address, opening date, program type |
| [site_level_results.csv](/downloads/site_level_results.csv) | Pre/post non-traffic call counts by site |
| [opening_dates.csv](/downloads/opening_dates.csv) | Verified opening dates |
| [methodology_inputs.csv](/downloads/methodology_inputs.csv) | Study parameters used in the pipeline |

### Chart Data

| File | Description |
|------|-------------|
| [pre_post_site_nontraffic_calls.csv](/data/charts/pre_post_site_nontraffic_calls.csv) | Pre/post counts by site |
| [zone_comparison_nontraffic_calls.csv](/data/charts/zone_comparison_nontraffic_calls.csv) | Zone spillover results |
| [rolling_3mo_yoy_nontraffic_calls.csv](/data/charts/rolling_3mo_yoy_nontraffic_calls.csv) | Rolling YoY trend data |
| [corridor_controls.csv](/data/charts/corridor_controls.csv) | Control corridor trend data |

---

## Processing Notes

- All geographic filtering uses 4326 (WGS84) coordinates projected to UTM Zone 10N for distance calculations.
- Non-traffic call classification uses keyword matching on the `cvlegend` field. See `study_parameters.yml` for the full keyword list.
- Opening dates are approximate and based on publicly available records. See `sites.yml` to review or update them.
- The pipeline is fully reproducible from source data. See the [README](https://github.com/{{ site.github_repo }}) for instructions.

<script>
  fetch("/data/metadata/build.json")
    .then(r => r.json())
    .then(d => {
      document.getElementById("build-meta").innerHTML = `
        <table>
          <tr><th>Build time</th><td>${d.build_timestamp}</td></tr>
          <tr><th>Git SHA</th><td>${d.git_sha}</td></tr>
          <tr><th>Data refreshed</th><td>${d.data_refresh_date}</td></tr>
        </table>`;
    })
    .catch(() => {
      document.getElementById("build-meta").textContent = "Build metadata not available.";
    });
</script>
