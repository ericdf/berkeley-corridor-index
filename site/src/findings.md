---
layout: base.njk
title: Findings
description: Corridor-level and property-level non-traffic police call results for the University Avenue interim housing cluster.
---

# Findings

This page presents results of the before-and-after analysis. Because the four study sites are geographically clustered along the same corridor, the primary analysis treats the University Avenue area as a shared treatment environment. Individual opening dates are analyzed as sequential interventions within that shared corridor.

All results use non-traffic calls for service from the Berkeley Police Department's public dataset.

---

## 1. Corridor Trend Over Time

Monthly non-traffic calls within the University Avenue corridor cluster, with each site opening marked.

<div id="chart-corridor-trend" class="chart-container" aria-label="Corridor monthly non-traffic calls over time">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  Vertical markers indicate site opening dates in sequence.
  Shaded line = 3-month rolling average.
  <a href="/downloads/site_level_results.csv">Download pre/post data</a>
</p>

---

## 2. Corridor vs. Comparison Corridors

All series indexed to 100 during the baseline period (before the first site opening) so trends are comparable regardless of baseline call volume.

<div id="chart-index" class="chart-container" aria-label="Indexed comparison: corridor vs controls">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">
  North Shattuck and South Telegraph are comparison corridors — similar street character, no interim housing conversions in the study period.
  Divergence from comparison corridors after openings is consistent with a corridor-level effect, but does not prove causation.
</p>

---

## 3. Active Sites and Call Volume

Monthly corridor calls alongside the count of active sites, showing whether call volume changed as successive sites opened.

<div id="chart-active-sites" class="chart-container" aria-label="Active sites and corridor call volume">
  <p class="chart-loading">Loading chart…</p>
</div>

---

## 4. Immediate Property Areas

The charts below show monthly non-traffic calls in the immediate block around each property (descriptive only — these small zones overlap within the broader corridor analysis above).

<div id="chart-property-local" class="chart-container" aria-label="Immediate site zone monthly calls">
  <p class="chart-loading">Loading chart…</p>
</div>

<p class="chart-note">Immediate zone = {{ params.immediate_zone_m }}m radius per property. These results are secondary and descriptive.</p>

---

## 5. Interpretation Notes

- Because the sites are close together, corridor-level analysis avoids double-counting from overlapping buffers.
- Changes in call volume after successive openings do not prove the sites caused the change.
- Comparison with North Shattuck and South Telegraph provides context for citywide trends.
- When the corridor diverges from comparison areas specifically after site openings, that pattern is worth public attention — but it remains association, not causation.

<script src="/assets/js/charts-findings.js" type="module"></script>
