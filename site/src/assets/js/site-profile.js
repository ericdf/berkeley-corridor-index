// Site profile page — small Leaflet map + Observable Plot charts

const _BASE = (window.BASE_PATH || "/").replace(/\/$/, "");
async function loadCsv(path) {
  const res = await fetch(_BASE + path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  const text = await res.text();
  return d3.csvParse(text, d3.autoType);
}

function siteId() {
  const el = document.querySelector("[data-site]");
  return el?.dataset.site ?? null;
}

function clearLoading(el) {
  const p = el?.querySelector(".chart-loading");
  if (p) p.remove();
}

function renderError(el, msg) {
  if (el) el.innerHTML = `<p class="chart-loading" style="color:#c00">${msg}</p>`;
}

// Small map
function initProfileMap() {
  const mapEl = document.getElementById("profile-map");
  if (!mapEl) return;
  const lat = parseFloat(mapEl.dataset.lat);
  const lon = parseFloat(mapEl.dataset.lon);
  const address = mapEl.dataset.address;

  const map = L.map("profile-map").setView([lat, lon], 15);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: "abcd",
    maxZoom: 19,
  }).addTo(map);

  L.circleMarker([lat, lon], {
    radius: 8,
    fillColor: "#c00",
    color: "#800",
    weight: 2,
    fillOpacity: 0.9,
  }).bindPopup(`<strong>${address}</strong>`).addTo(map);
}

// Pre/post chart filtered to this site
async function renderPrePost(id) {
  const el = document.getElementById("chart-site-prepost");
  if (!el) return;
  try {
    const data = (await loadCsv("/data/charts/pre_post_site_nontraffic_calls.csv"))
      .filter(d => d.site_id === id);
    clearLoading(el);
    if (!data.length) { renderError(el, "No data for this site."); return; }

    const row = data[0];
    const sufficient = String(row.post_sufficient).toLowerCase() === "true";
    const long = [{ period: "12 months before", count: row.pre_count }];
    if (sufficient) long.push({ period: "12 months after", count: row.post_count });

    const marks = [
      Plot.barX(long, { x: "count", y: "period", fill: "period", tip: true }),
      Plot.ruleX([0]),
    ];
    if (!sufficient) {
      marks.push(Plot.text([{ x: row.pre_count, y: "12 months after" }], {
        x: "x", y: "y",
        text: () => "  Insufficient post-period data",
        textAnchor: "start", fill: "#888", fontSize: 12,
      }));
    }

    const plot = Plot.plot({
      marginLeft: 160,
      x: { label: "Non-traffic calls", grid: true },
      y: { label: null },
      color: { domain: ["12 months before", "12 months after"], range: ["#9aabbd", "#2a5f9e"] },
      marks,
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available.");
    console.warn(e);
  }
}

// Zone spillover filtered to this site
async function renderZones(id) {
  const el = document.getElementById("chart-site-zones");
  if (!el) return;
  try {
    const data = (await loadCsv("/data/charts/zone_comparison_nontraffic_calls.csv"))
      .filter(d => d.site_id === id);
    clearLoading(el);
    if (!data.length) { renderError(el, "No data for this site."); return; }

    const zoneLabel = { site_block: "Zone 1", adjacent_blocks: "Zone 2", wider_nearby: "Zone 3" };
    const long = [];
    for (const row of data) {
      long.push({ zone: zoneLabel[row.zone] ?? row.zone, period: "Before", count: row.pre_count });
      long.push({ zone: zoneLabel[row.zone] ?? row.zone, period: "After", count: row.post_count });
    }
    const plot = Plot.plot({
      marginLeft: 80,
      x: { label: "Non-traffic calls" },
      y: { label: null },
      color: { legend: true, domain: ["Before", "After"], range: ["#aab", "#2a5f9e"] },
      marks: [
        Plot.barX(long, Plot.groupY({ x: "sum" }, { x: "count", y: "zone", fill: "period", tip: true })),
        Plot.ruleX([0]),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available.");
    console.warn(e);
  }
}

// Rolling YoY filtered to this site
async function renderRolling(id) {
  const el = document.getElementById("chart-site-rolling");
  if (!el) return;
  try {
    const data = (await loadCsv("/data/charts/rolling_3mo_yoy_nontraffic_calls.csv"))
      .filter(d => d.site_id === id);
    clearLoading(el);
    if (!data.length) { renderError(el, "No data for this site."); return; }

    const parsed = data.map(d => ({ ...d, window_start: new Date(d.window_start) }));
    const openingAttr = document.getElementById("chart-site-rolling")?.dataset.opening;
    const opening = openingAttr ? new Date(openingAttr) : null;

    const marks = [
      Plot.ruleY([0], { stroke: "#bbb" }),
      Plot.line(parsed, { x: "window_start", y: "yoy_pct_change", stroke: "#2a5f9e", tip: true }),
    ];
    if (opening) marks.push(Plot.ruleX([opening], { stroke: "#c00", strokeDasharray: "4 3", title: "Site opened" }));

    const plot = Plot.plot({
      marginLeft: 60,
      x: { label: "Window start", type: "utc" },
      y: { label: "YoY % change", tickFormat: d => `${d >= 0 ? "+" : ""}${d}%` },
      marks,
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available.");
    console.warn(e);
  }
}

const id = siteId();
initProfileMap();
if (id) {
  renderPrePost(id);
  renderZones(id);
  renderRolling(id);
}
