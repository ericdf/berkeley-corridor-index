---
layout: base.njk
title: Maps
description: Maps of the University Avenue corridor study area, site locations, zones, and comparison corridors.
---

# Maps

The map below shows the University Avenue corridor study area, individual site locations, and the two comparison corridors. Zone polygons around each site are shown for reference only — the primary analysis uses the corridor polygon, not individual site buffers.

<div id="site-map" class="map-container" aria-label="Berkeley interim housing corridor map"></div>

<div class="map-legend">
  <h3>Legend</h3>
  <ul>
    <li><span class="legend-swatch corridor-swatch"></span> University Ave corridor cluster (primary study area)</li>
    <li><span class="legend-dot site-dot"></span> Study site</li>
    <li><span class="legend-swatch zone1-swatch"></span> Immediate site zone (descriptive only)</li>
    <li><span class="legend-swatch control-swatch"></span> Comparison corridors (North Shattuck, South Telegraph)</li>
    <li><span class="legend-line district-line"></span> Council district boundaries</li>
  </ul>
</div>

<p class="map-note">
  Corridor polygon = convex hull of all study sites, buffered 250 m.
  Immediate zones = 100 m radius per property.
  Comparison corridor circles = 500 m radius.
  Data: Berkeley open data portal.
</p>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/js/map.js" type="module"></script>
