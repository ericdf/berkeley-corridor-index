// Maps page — Leaflet map with site markers and zone overlays

const BERKELEY_CENTER = [37.8716, -122.2727];
const ZOOM = 14;

const ZONE_STYLES = {
  site_block: { color: "rgba(220,80,60,0.8)", fillColor: "rgba(220,80,60,0.2)", weight: 1.5, fillOpacity: 1 },
  adjacent_blocks: { color: "rgba(240,160,40,0.8)", fillColor: "rgba(240,160,40,0.18)", weight: 1.5, fillOpacity: 1 },
  wider_nearby: { color: "rgba(60,140,200,0.7)", fillColor: "rgba(60,140,200,0.12)", weight: 1, fillOpacity: 1 },
};

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

  const zoneFiles = [
    { path: "/data/maps/wider_nearby_zones.geojson", zone: "wider_nearby" },
    { path: "/data/maps/adjacent_block_zones.geojson", zone: "adjacent_blocks" },
    { path: "/data/maps/site_block_zones.geojson", zone: "site_block" },
  ];

  for (const { path, zone } of zoneFiles) {
    try {
      const geojson = await loadGeoJson(path);
      L.geoJSON(geojson, {
        style: ZONE_STYLES[zone],
        onEachFeature(feature, layer) {
          if (feature.properties?.address) {
            layer.bindPopup(`<strong>${feature.properties.address}</strong><br>${zone.replace("_", " ")}`);
          }
        },
      }).addTo(map);
    } catch (e) {
      console.warn(`Could not load ${path}:`, e.message);
    }
  }

  // Council districts
  try {
    const districts = await loadGeoJson("/data/maps/council_districts_simplified.geojson");
    L.geoJSON(districts, {
      style: { color: "#444", weight: 1.5, fill: false, dashArray: "4 3" },
    }).addTo(map);
  } catch (e) {
    console.warn("Council districts not available:", e.message);
  }

  // Site markers
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
  } catch (e) {
    console.warn("Sites GeoJSON not available:", e.message);
  }
}

initMap().catch(console.error);
