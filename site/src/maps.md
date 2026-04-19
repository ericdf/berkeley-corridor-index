---
layout: base.njk
title: Maps
description: Maps of Berkeley interim housing sites, study zones, and council districts.
---

# Maps

The map below shows the four study sites on University Avenue, along with the geographic zones used in the analysis.

<div id="site-map" class="map-container" aria-label="Berkeley interim housing site map"></div>

<div class="map-legend">
  <h3>Legend</h3>
  <ul>
    <li><span class="legend-dot site-dot"></span> Study site</li>
    <li><span class="legend-swatch zone1-swatch"></span> Zone 1 — site block (&le;100 m)</li>
    <li><span class="legend-swatch zone2-swatch"></span> Zone 2 — adjacent blocks (&le;300 m)</li>
    <li><span class="legend-swatch zone3-swatch"></span> Zone 3 — wider nearby area (&le;600 m)</li>
    <li><span class="legend-line district-line"></span> Council district boundaries</li>
  </ul>
</div>

<p class="map-note">
  Zones are circular buffers centered on each site. Actual block boundaries may differ.
  Data: Berkeley open data portal.
</p>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/js/map.js" type="module"></script>
