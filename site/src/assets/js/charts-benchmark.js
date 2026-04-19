// Benchmark page — percentile dot plot, histogram, and Leaflet hotspot map

async function loadCsv(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return d3.csvParse(await res.text(), d3.autoType);
}

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.json();
}

function clearLoading(el) { el.querySelector(".chart-loading")?.remove(); }
function renderError(el, msg) { el.innerHTML = `<p class="chart-loading" style="color:#c00">${msg}</p>`; }

// Chart 1: Dot plot of site percentile rankings
async function renderPercentileDot() {
  const el = document.getElementById("chart-percentile-dot");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/site_percentiles.csv");
    clearLoading(el);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: {
        label: "Citywide percentile (non-traffic calls within 100m)",
        domain: [0, 100],
        grid: true,
      },
      y: { label: null },
      marks: [
        Plot.ruleX([90], { stroke: "#c00", strokeDasharray: "4 3", strokeOpacity: 0.7 }),
        Plot.text([{ x: 90, label: "90th pct" }], {
          x: "x", y: () => null, text: "label",
          frameAnchor: "top", dy: 6, fill: "#c00", fontSize: 10,
        }),
        Plot.dot(data, {
          x: "percentile_citywide",
          y: "address",
          fill: "#2a5f9e",
          r: 7,
          tip: true,
          title: d =>
            `${d.address}\n${d.call_count_100m.toLocaleString()} calls in 100m zone\nCitywide: ${d.percentile_citywide}th percentile` +
            (d.percentile_flats != null ? `\nFlats-only: ${d.percentile_flats}th percentile` : ""),
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 2: Histogram of citywide distribution with site markers
async function renderDistribution() {
  const el = document.getElementById("chart-distribution");
  if (!el) return;
  try {
    const [grid, sites] = await Promise.all([
      loadCsv("/data/charts/citywide_benchmark_points.csv"),
      loadCsv("/data/charts/site_percentiles.csv"),
    ]);
    clearLoading(el);

    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 30,
      marginBottom: 50,
      x: { label: "Non-traffic calls within 100m radius", grid: true },
      y: { label: "Grid points", grid: true },
      marks: [
        Plot.rectY(grid, Plot.binX({ y: "count" }, {
          x: "call_count_100m",
          fill: "#2a5f9e",
          fillOpacity: 0.5,
          thresholds: 40,
        })),
        Plot.ruleY([0]),
        // Site markers
        ...sites.map(s =>
          Plot.ruleX([s.call_count_100m], {
            stroke: "#c00",
            strokeDasharray: "4 3",
            strokeOpacity: 0.8,
          })
        ),
        Plot.text(sites, {
          x: "call_count_100m",
          y: () => null,
          text: d => d.label,
          frameAnchor: "top",
          dy: 6,
          fill: "#c00",
          fontSize: 9,
          rotate: -45,
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Map: benchmark hotspot layer + site markers
async function initBenchmarkMap() {
  const mapEl = document.getElementById("benchmark-map");
  if (!mapEl) return;

  const BERKELEY_CENTER = [37.872, -122.280];
  const map = L.map("benchmark-map").setView(BERKELEY_CENTER, 13);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map);

  function pctColor(pct) {
    if (pct >= 90) return "rgba(220,80,60,0.8)";
    if (pct >= 75) return "rgba(240,160,40,0.6)";
    return "rgba(160,190,220,0.4)";
  }

  try {
    const geojson = await loadJson("/data/maps/citywide_benchmark_points.geojson");
    L.geoJSON(geojson, {
      pointToLayer(feature, latlng) {
        const pct = feature.properties.percentile_citywide ?? 0;
        return L.circleMarker(latlng, {
          radius: pct >= 90 ? 5 : 3,
          fillColor: pctColor(pct),
          color: "none",
          fillOpacity: 1,
        });
      },
      onEachFeature(feature, layer) {
        const p = feature.properties;
        layer.bindPopup(
          `<strong>${p.call_count_100m} non-traffic calls</strong><br>` +
          `Citywide: ${p.percentile_citywide}th percentile`
        );
      },
    }).addTo(map);
  } catch (e) { console.warn("Benchmark points unavailable:", e.message); }

  // Study site markers on top
  try {
    const sites = await loadJson("/data/maps/sites.geojson");
    L.geoJSON(sites, {
      pointToLayer(feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: "#c00",
          color: "#800",
          weight: 1.5,
          fillOpacity: 0.9,
        });
      },
      onEachFeature(feature, layer) {
        const p = feature.properties;
        layer.bindPopup(`<strong>${p.address}</strong><br>Study site`);
      },
    }).addTo(map);
  } catch (e) { console.warn("Sites unavailable:", e.message); }
}

renderPercentileDot();
renderDistribution();
initBenchmarkMap();
