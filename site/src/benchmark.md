---
layout: base.njk
title: Citywide Benchmark
description: How do non-traffic call counts near the studied sites compare to the rest of Berkeley?
---

# Citywide Benchmark

This page addresses the selection-bias question: are the studied sites unusually active, or similar to many other Berkeley locations?

We placed a 100 m grid across the entire city (~2,700 points) and counted non-traffic police calls within 100 m of each point over the study period. The four study sites are ranked against this citywide distribution.

All sites also fall within the Berkeley flatlands, so the citywide and flats-only percentiles are nearly identical.

---

## Site Rankings

<div id="chart-percentile-dot" class="chart-container" aria-label="Site percentile rankings against citywide distribution">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Each dot represents one study site. Position on the x-axis shows its percentile rank among all ~2,700 Berkeley 100 m grid points.
  The vertical line marks the 90th percentile.
</p>

---

## Citywide Distribution

<div id="chart-distribution" class="chart-container" aria-label="Histogram of non-traffic calls across all Berkeley grid points">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Histogram of non-traffic call counts (100 m radius) at ~2,700 points across Berkeley.
  Vertical markers show each study site's call count.
  Most Berkeley grid points have far lower call counts than the studied sites.
</p>

---

## Citywide Hotspot Map

<div id="benchmark-map" class="map-container" aria-label="Berkeley non-traffic call hotspot map"></div>

<div class="map-legend">
  <h3>Legend</h3>
  <ul>
    <li><span class="legend-swatch" style="background:rgba(220,80,60,0.8);border:none;"></span> High call density (top decile)</li>
    <li><span class="legend-swatch" style="background:rgba(240,160,40,0.6);border:none;"></span> Elevated (75th–90th percentile)</li>
    <li><span class="legend-swatch" style="background:rgba(200,220,240,0.6);border:none;"></span> Below 75th percentile</li>
    <li><span class="legend-dot site-dot"></span> Study site</li>
  </ul>
</div>

<p class="map-note">
  Each dot = one 100 m grid point. Color = citywide percentile of non-traffic call count within 100 m.
  Grid spacing: 100 m. Data: Berkeley open data portal.
</p>

---

## Interpretation

All four study sites rank above the **90th percentile citywide** for non-traffic call density within a 100 m radius. 1461 University and 1761 University rank above the **98th percentile**.

Percentile rankings are descriptive only. Higher call counts may reflect:

- mixed-use corridor activity
- transit access and foot traffic
- existing disorder patterns preceding the conversions
- reporting behavior in denser areas
- service clustering (shelters, social services) attracting calls

High rankings do not prove the conversions caused elevated call volumes, nor do they reflect resident misconduct. They indicate that these locations are among the most active in Berkeley for non-traffic police contact, which warrants attention independent of causal interpretation.

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/js/charts-benchmark.js" type="module"></script>
