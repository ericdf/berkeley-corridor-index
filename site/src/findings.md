---
layout: base.njk
title: Findings
description: Pre/post non-traffic police call results for four Berkeley interim housing sites.
---

# Findings

This page presents the main results of the before-and-after analysis.
All results use non-traffic calls for service from the Berkeley Police Department's public dataset.

---

## Pre / Post Comparison

For each site, we compared non-traffic call counts in the 12 months before and 12 months after the site's opening date.

<div id="chart-prepost" class="chart-container" aria-label="Pre/post non-traffic calls by site">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Source: Berkeley Police Department calls for service &middot;
  <a href="/downloads/site_level_results.csv">Download CSV</a>
</p>

---

## Zone Spillover

Were changes confined to the site block, or did adjacent blocks also show increases?

<div id="chart-spillover" class="chart-container" aria-label="Zone spillover by site">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Zone 1 = site block (&le;100m) &middot; Zone 2 = adjacent blocks (&le;300m) &middot; Zone 3 = wider nearby area (&le;600m)
</p>

---

## Rolling 3-Month Year-over-Year Trend

Comparing the same three-month window across consecutive years helps filter out seasonal variation.

<div id="chart-rolling" class="chart-container" aria-label="Rolling 3-month year-over-year trend">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">Vertical lines mark site opening dates.</p>

---

## Control Corridors

For context, we applied the same rolling YoY method to two comparable Berkeley commercial corridors.

<div id="chart-controls" class="chart-container" aria-label="Control corridor trends">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  North Shattuck and South Telegraph serve as rough baselines for citywide trend patterns.
</p>

---

## Interpretation Notes

- Changes in call volume after a site opens do not prove the site caused the change.
- Other factors — citywide trends, economy, staffing, weather, reporting behavior — can affect call counts.
- When multiple sites show similar increases in adjacent blocks after opening, that pattern is worth public attention.
- Results are presented to support evidence-based discussion, not to advocate for a particular policy.

<script src="/assets/js/charts-findings.js" type="module"></script>
