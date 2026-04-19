// Benchmark page — pre/post percentile comparison, rate change, histogram, hotspot map

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

// Chart 1: Connected dot plot — pre vs post percentile, citywide vs corridor
async function renderPrePostPercentile() {
  const el = document.getElementById("chart-pre-post-pct");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/site_percentiles.csv");
    clearLoading(el);

    // Four rows per site: pre/post × citywide/corridor
    const rows = data.flatMap(d => [
      { address: d.address, universe: "Citywide", period: "Before opening", pct: d.pre_percentile_citywide },
      { address: d.address, universe: "Citywide", period: "After opening",  pct: d.percentile_citywide },
      { address: d.address, universe: "Major corridors only", period: "Before opening", pct: d.pre_percentile_corridor },
      { address: d.address, universe: "Major corridors only", period: "After opening",  pct: d.percentile_corridor },
    ]).filter(d => d.pct != null);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: { label: "Percentile rank within universe", domain: [0, 100], grid: true },
      y: { label: null },
      fy: { label: null, padding: 0.3 },
      color: { legend: true, domain: ["Before opening", "After opening"], range: ["#aaa", "#2a5f9e"] },
      marks: [
        Plot.ruleX([90], { stroke: "#c00", strokeDasharray: "4 3", strokeOpacity: 0.5 }),
        Plot.line(rows, {
          x: "pct", y: "address", z: "address",
          fy: "universe", stroke: "#ddd", strokeWidth: 1.5,
        }),
        Plot.dot(rows, {
          x: "pct", y: "address", fill: "period",
          fy: "universe", r: 7, tip: true,
          title: d => `${d.address}\n${d.period}\n${d.pct}th percentile (${d.universe})`,
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 2: Grouped bars — pre vs post monthly rate
async function renderRateChange() {
  const el = document.getElementById("chart-rate-change");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/site_percentiles.csv");
    clearLoading(el);

    const rows = data.flatMap(d => [
      { address: d.address, period: "Before opening", rate: d.pre_rate_per_month },
      { address: d.address, period: "After opening",  rate: d.post_rate_per_month },
    ]);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: { label: "Non-traffic calls / month (100m radius)", grid: true },
      y: { label: null },
      color: { legend: true, domain: ["Before opening", "After opening"], range: ["#aaa", "#2a5f9e"] },
      marks: [
        Plot.barX(rows, {
          x: "rate",
          y: "address",
          fill: "period",
          tip: true,
          title: d => `${d.address}\n${d.period}: ${d.rate} calls/month`,
        }),
        Plot.ruleX([0]),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 3: Histogram of citywide distribution with site markers
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
      marginBottom: 60,
      x: { label: "Non-traffic calls within 100m (all period)", grid: true },
      y: { label: "Grid points", grid: true },
      marks: [
        Plot.rectY(grid, Plot.binX({ y: "count" }, {
          x: "call_count_100m",
          fill: "#2a5f9e",
          fillOpacity: 0.5,
          thresholds: 40,
        })),
        Plot.ruleY([0]),
        ...sites.map(s => Plot.ruleX([s.call_count_100m], {
          stroke: "#c00", strokeDasharray: "4 3", strokeOpacity: 0.8,
        })),
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

  const map = L.map("benchmark-map").setView([37.872, -122.280], 13);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: "abcd", maxZoom: 19,
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

  try {
    const sites = await loadJson("/data/maps/sites.geojson");
    L.geoJSON(sites, {
      pointToLayer(feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 8, fillColor: "#c00", color: "#800", weight: 1.5, fillOpacity: 0.9,
        });
      },
      onEachFeature(feature, layer) {
        layer.bindPopup(`<strong>${feature.properties.address}</strong><br>Study site`);
      },
    }).addTo(map);
  } catch (e) { console.warn("Sites unavailable:", e.message); }
}

renderPrePostPercentile();
renderRateChange();
renderDistribution();
initBenchmarkMap();
