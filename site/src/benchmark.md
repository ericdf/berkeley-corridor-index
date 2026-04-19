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
  Connected dots show each site's citywide percentile rank before opening (hollow) and after opening (filled),
  both expressed as annualized monthly rates so the two periods are comparable.
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
  Histogram of all-period non-traffic call counts at ~2,700 grid points across Berkeley.
  Vertical markers show each site's all-period count. Most of Berkeley is far below these levels.
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

All four sites were **above the 82nd percentile citywide before any conversion opened** — these were already above-average activity locations, not quiet blocks that became busy after the projects launched.

After opening, all four sites moved higher in the citywide ranking. The rate increases vary by site:

- **1461 University**: 11.5 → 18.8 calls/month (+64%) — the clearest increase
- **1620 San Pablo**: 3.9 → 8.0 calls/month (+105%) — rate roughly doubled, though from a lower base
- **1619 University**: 2.5 → 4.8 calls/month (+92%) — similar pattern
- **1761 University**: 11.3 → 14.0 calls/month (+24%) — modest increase, but post period is only ~2 months

The pre-existing elevation complicates causal interpretation: some share of post-opening activity likely reflects pre-existing corridor characteristics rather than the conversions themselves. The indexed comparison with control corridors on the [Findings page](/findings/) provides additional context.

Percentile rankings are descriptive only. Higher call counts may reflect mixed-use corridor activity, transit access, existing disorder patterns, or service clustering — not necessarily resident misconduct.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/js/charts-benchmark.js" type="module"></script>
