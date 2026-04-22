---
layout: base.njk
title: Citywide Benchmark
description: How do non-traffic call counts near the studied sites compare to the rest of Berkeley, before and after opening?
---

# Citywide Benchmark

This page addresses two related questions: are the studied sites unusually active relative to the rest of Berkeley, and were they already that way before the conversions opened?

We placed a 100 m grid across the entire city (~2,700 points) and counted non-traffic police calls within 100 m of each point. The four study sites are ranked against this citywide distribution — both for their pre-opening rate and their post-opening rate.

---

## Before vs. After: Percentile Ranking

<div id="chart-pre-post-pct" class="chart-container" aria-label="Site percentile rankings before and after opening">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Connected dots show each site's percentile rank before opening (gray) and after opening (blue),
  expressed as annualized monthly rates so the two periods are comparable.
  Top panel: ranked against all ~2,700 Berkeley grid points.
  Bottom panel: ranked against the ~367 grid points within 75m of a primary or secondary road —
  a more like-for-like comparison for sites on major commercial corridors.
  A rightward shift means the site became relatively more active after opening.
</p>

---

## Before vs. After: Monthly Call Rate

<div id="chart-rate-change" class="chart-container" aria-label="Pre vs post monthly call rate by site">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Non-traffic calls per month within 100 m, averaged over each period.
  Pre = Jan 2021 to site opening. Post = site opening to Apr 2026.
  Note that 1761 University opened in Feb 2026 and has only ~2 months of post data.
</p>

---

## Citywide Distribution

<div id="chart-distribution" class="chart-container" aria-label="Histogram of non-traffic calls across all Berkeley grid points">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Each bar shows how many of the ~2,700 Berkeley grid points recorded that call-count range over the full study period.
  The tall bars on the left represent the large number of quiet locations across the city.
  The vertical markers show where each study site falls in that distribution — the further right the marker, the more activity at that location relative to the rest of Berkeley.
</p>

---

## Citywide Hotspot Map

<div id="benchmark-map" class="map-container" aria-label="Berkeley non-traffic call hotspot map"></div>

<div class="map-legend">
  <h3>Legend</h3>
  <ul>
    <li><span class="legend-swatch" style="background:rgba(220,80,60,0.8);border:none;"></span> Top decile (90th+ percentile)</li>
    <li><span class="legend-swatch" style="background:rgba(240,160,40,0.6);border:none;"></span> Elevated (75th–90th percentile)</li>
    <li><span class="legend-swatch" style="background:rgba(160,190,220,0.4);border:none;"></span> Below 75th percentile</li>
    <li><span class="legend-dot site-dot"></span> Study site</li>
  </ul>
</div>

<p class="map-note">
  Each dot = one 100 m grid point. Color = all-period citywide percentile.
  Grid spacing: 100 m. Data: Berkeley open data portal.
</p>

---

## Interpretation

### Which comparison universe is right?

The citywide percentiles (91st–99th) include quiet residential streets, parks, and hillside neighborhoods — not a fair comparison for sites on University and San Pablo Avenues. The corridor-only universe (367 grid points on or near primary and secondary roads) is the more appropriate baseline.

Even against that more demanding baseline, the study sites stand out — and their activity increased substantially after the shelters opened:

| Site | Pre (corridor pct) | Post (corridor pct) | Rate change |
|------|--------------------|---------------------|-------------|
| 1461 University | 87th | 96th | +64% |
| 1761 University | 87th | 91th | +24% |
| 1620 San Pablo | 67th | 82nd | +105% |
| 1619 University | 55th | 68th | +92% |

Every site was already above the median for major commercial corridors before opening. Every site moved higher after opening. Two (1461 and 1761 University) were already in the top decile of active corridors before the conversion — and climbed further. The other two more than doubled their call rates.

The rate increases are notable regardless of the comparison universe:

- **1461 University**: 11.5 → 18.8 calls/month — **+64%**, the largest in absolute terms
- **1620 San Pablo**: 3.9 → 8.0 calls/month — rate **more than doubled**
- **1619 University**: 2.5 → 4.8 calls/month — rate **nearly doubled**
- **1761 University**: 11.3 → 14.0 calls/month — post period is only ~2 months

The [indexed comparison with control corridors](/findings/) examines whether major Berkeley corridors generally trended upward during this period, which is the most direct way to assess how much of these increases are attributable to the conversions versus broader trends.

Percentile rankings are descriptive only. Higher call counts may reflect mixed-use corridor activity, transit access, existing disorder patterns, or service clustering — not necessarily resident misconduct.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/js/charts-benchmark.js" type="module"></script>
