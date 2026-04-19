---
layout: base.njk
title: Findings
description: Concentration, site-level pre/post, and cluster trend results for the Berkeley interim housing study.
---

# Findings

This page presents results from two distinct treatment geographies: the **University Avenue core cluster** (1461, 1619, and 1761 University) and the **San Pablo node** (1620 San Pablo Ave, Golden Bear Inn). Each is analyzed independently. All results use non-traffic calls for service from the Berkeley Police Department's public dataset.

---

## 1. Concentration of Calls Near Study Sites

Non-traffic police calls are concentrated within 100 m of the studied properties relative to the surrounding study area.

<div id="chart-concentration" class="chart-container" aria-label="Share of study-area calls near each site">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Share of non-traffic calls within the combined study area (university cluster + San Pablo node) that fall within each site's 100 m zone,
  split by pre- and post-opening periods.
  <a href="/data-sources/">Download data</a>
</p>

---

## 2. Site-by-Site Pre/Post Changes

Monthly non-traffic calls in the 600 m zone around each site, 12 months before and after opening. Sites with insufficient post-period data are flagged.

<div id="chart-prepost" class="chart-container" aria-label="Pre/post call counts by site">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  1761 University has less than 6 months of post-opening data and is not shown as a definitive result.
  <a href="/downloads/site_level_results.csv">Download pre/post data</a>
</p>

---

## 3. University Core Cluster Trend

Monthly non-traffic calls within the University Avenue core cluster, with each University site opening marked.

<div id="chart-cluster-trend" class="chart-container" aria-label="University core cluster monthly non-traffic calls over time">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Bold line = 3-month rolling average. Dashed vertical lines = site opening dates (University Ave sites only).
</p>

---

## 4. San Pablo Node Trend

Monthly non-traffic calls within the San Pablo node (250 m buffer around 1620 San Pablo Ave).

<div id="chart-sp-trend" class="chart-container" aria-label="San Pablo node monthly non-traffic calls over time">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Dashed vertical line = Golden Bear Inn opening date (January 2023).
</p>

---

## 5. Comparison Corridors

University core cluster and San Pablo node indexed to 100 during the pre-period baseline, alongside two comparison corridors.

<div id="chart-index" class="chart-container" aria-label="Indexed comparison: treatment geographies vs controls">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  North Shattuck and South Telegraph are comparison corridors with similar street character and no interim housing conversions in the study period.
  Divergence from comparison corridors is consistent with a local effect but does not prove causation.
</p>

---

## 6. Adjacent-Block Spillover

Zone-level comparison for each site: immediate 100 m zone vs. 100–300 m adjacent ring vs. 300–600 m wider area.

<div id="chart-spillover" class="chart-container" aria-label="Zone comparison for all sites">
  <p class="chart-loading">Loading chart…</p>
</div>

---

## 7. Interpretation Notes

- **Concentration**: 100 m site zones contain a disproportionate share of study-area calls, especially at 1461 University and 1761 University.
- **Mixed pre/post results**: 1461 University showed a substantial increase after opening; 1619 University and 1620 San Pablo showed modest declines; 1761 University has insufficient post data.
- **Cluster vs. node**: The University cluster and the San Pablo site show different patterns — grouping them into one corridor average would obscure that difference.
- **Association, not causation**: Changes in call volume after openings do not prove the sites caused the change. Comparison with control corridors provides context for broader citywide trends.
- **Data limitations**: Calls data required geocoding from block addresses; approximately 15% of records could not be geocoded. Opening dates are approximate for some sites.

<script src="/assets/js/charts-findings.js" type="module"></script>
