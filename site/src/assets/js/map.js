// Maps page — Leaflet map: separate University core and San Pablo node polygons

const BERKELEY_CENTER = [37.8716, -122.2827];
const ZOOM = 13;

async function loadGeoJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

async function initMap() {
  const map = L.map("site-map").setView(BERKELEY_CENTER, ZOOM);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map);

  // Council district boundaries
  try {
    const districts = await loadGeoJson("/data/maps/council_districts_simplified.geojson");
    L.geoJSON(districts, {
      style: { color: "#888", weight: 1, fill: false, dashArray: "4 3" },
    }).addTo(map);
  } catch (e) { console.warn("Council districts unavailable:", e.message); }

  // Control corridors (comparison areas)
  try {
    const controls = await loadGeoJson("/data/maps/control_corridors.geojson");
    L.geoJSON(controls, {
      style: { color: "#888", weight: 1.5, fillColor: "#888", fillOpacity: 0.08, dashArray: "3 4" },
      onEachFeature(feature, layer) {
        if (feature.properties?.label) layer.bindPopup(`<strong>${feature.properties.label}</strong><br>Comparison corridor`);
      },
    }).addTo(map);
  } catch (e) { console.warn("Control corridors unavailable:", e.message); }

  // Immediate site zones (secondary / descriptive)
  try {
    const zones = await loadGeoJson("/data/maps/immediate_site_zones.geojson");
    L.geoJSON(zones, {
      style: { color: "rgba(220,80,60,0.6)", weight: 1, fillColor: "rgba(220,80,60,0.12)", fillOpacity: 1 },
      onEachFeature(feature, layer) {
        layer.bindPopup(`<strong>${feature.properties.address}</strong><br>100m zone (descriptive only)`);
      },
    }).addTo(map);
  } catch (e) { console.warn("Immediate site zones unavailable:", e.message); }

  // San Pablo node polygon
  try {
    const sp = await loadGeoJson("/data/maps/san_pablo_node.geojson");
    L.geoJSON(sp, {
      style: { color: "#c47a00", weight: 2.5, fillColor: "#c47a00", fillOpacity: 0.08 },
      onEachFeature(feature, layer) {
        layer.bindPopup(`<strong>${feature.properties.label}</strong><br>San Pablo node`);
      },
    }).addTo(map);
  } catch (e) { console.warn("San Pablo node unavailable:", e.message); }

  // University core cluster polygon — primary treatment geography
  try {
    const core = await loadGeoJson("/data/maps/university_core_cluster.geojson");
    L.geoJSON(core, {
      style: { color: "#2a5f9e", weight: 2.5, fillColor: "#2a5f9e", fillOpacity: 0.08 },
      onEachFeature(feature, layer) {
        layer.bindPopup(`<strong>${feature.properties.label}</strong><br>University core cluster (primary study area)`);
      },
    }).addTo(map);
  } catch (e) { console.warn("University core cluster unavailable:", e.message); }

  // Site markers — on top of everything
  try {
    const sites = await loadGeoJson("/data/maps/sites.geojson");
    L.geoJSON(sites, {
      pointToLayer(feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 7,
          fillColor: "#c00",
          color: "#800",
          weight: 1.5,
          fillOpacity: 0.9,
        });
      },
      onEachFeature(feature, layer) {
        const p = feature.properties;
        layer.bindPopup(`<strong>${p.address}</strong><br>${p.program_type ?? ""}<br>Opened: ${p.opening_date ?? "unknown"}`);
      },
    }).addTo(map);
  } catch (e) { console.warn("Sites GeoJSON unavailable:", e.message); }
}

initMap().catch(console.error);
