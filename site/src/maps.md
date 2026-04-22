---
layout: base.njk
title: Maps
description: Maps of the University Avenue core cluster, San Pablo node, site locations, zones, and comparison corridors.
scripts:
  - /assets/js/map.js
---

# Maps

The map below shows the two primary treatment geographies, individual site locations, and the two comparison corridors. The University Avenue core cluster and the San Pablo node are analyzed independently because they are geographically distinct — the Golden Bear Inn site sits approximately 440 m northwest of the University cluster and incorporating it into a combined convex hull pulls in low-activity intervening blocks.

Zone polygons around each site are shown for reference only — the primary analysis uses the cluster polygons, not individual site buffers.

<div id="site-map" class="map-container" aria-label="Berkeley interim housing study area map"></div>

<div class="map-legend">
  <h3>Legend</h3>
  <ul>
    <li><span class="legend-swatch corridor-swatch"></span> University Ave core cluster (primary study area)</li>
    <li><span class="legend-swatch san-pablo-swatch"></span> San Pablo node (analyzed separately)</li>
    <li><span class="legend-dot site-dot"></span> Study site</li>
    <li><span class="legend-swatch zone1-swatch"></span> Immediate site zone, 100 m (descriptive only)</li>
    <li><span class="legend-swatch control-swatch"></span> Comparison corridors (North Shattuck, South Telegraph)</li>
    <li><span class="legend-line district-line"></span> Council district boundaries</li>
  </ul>
</div>

<p class="map-note">
  University core cluster = convex hull of three University Ave sites, buffered 250 m.
  San Pablo node = 250 m buffer around 1620 San Pablo Ave.
  Immediate zones = 100 m radius per property.
  Comparison corridor circles = 500 m radius.
  Data: Berkeley open data portal.
</p>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
