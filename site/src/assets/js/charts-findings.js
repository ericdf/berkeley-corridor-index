// Findings page charts using Observable Plot

const _BASE = (window.BASE_PATH || "/").replace(/\/$/, "");
async function loadCsv(path) {
  const res = await fetch(_BASE + path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return d3.csvParse(await res.text(), d3.autoType);
}

function clearLoading(el) { el.querySelector(".chart-loading")?.remove(); }
function renderError(el, msg) { el.innerHTML = `<p class="chart-loading" style="color:#c00">${msg}</p>`; }

function openingMarks(events) {
  return events.flatMap(d => [
    Plot.ruleX([new Date(d.opening_date)], { stroke: "#c00", strokeDasharray: "4 3", strokeOpacity: 0.7 }),
    Plot.text([d], {
      x: d => new Date(d.opening_date),
      y: () => null,
      text: d => String(d.sequence),
      frameAnchor: "top",
      dy: 6,
      fill: "#c00",
      fontSize: 10,
      fontWeight: "bold",
    }),
  ]);
}

// Chart 1: Concentration — pre/post grouped bars per site
async function renderConcentration() {
  const el = document.getElementById("chart-concentration");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/concentration_share.csv");
    clearLoading(el);

    // per-site pre/post rows only
    const rows = data
      .filter(d => d.site_id !== "all_sites" && (d.period === "pre" || d.period === "post"))
      .map(d => ({ ...d, label: d.period === "pre" ? "Before opening" : "After opening" }));

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: { label: "Share of period calls within 100m zone (%)", grid: true },
      y: { label: null },
      color: { legend: true, domain: ["Before opening", "After opening"], range: ["#888", "#2a5f9e"] },
      marks: [
        Plot.barX(rows, Plot.groupY({ x: "sum" }, {
          x: "share_of_citywide_pct",
          y: "address",
          fill: "label",
          tip: true,
          title: d => `${d.address} — ${d.label}\n${d.share_of_citywide_pct}% of period calls\n(${(d.calls_in_zone ?? 0).toLocaleString()} in zone)`,
        })),
        Plot.ruleX([0]),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 2: Pre/post grouped bar chart (one bar per site, sufficient sites only)
async function renderPrePost() {
  const el = document.getElementById("chart-prepost");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/pre_post_site_nontraffic_calls.csv");
    clearLoading(el);

    const sufficient = data.filter(d => String(d.post_sufficient).toLowerCase() === "true");

    // Reshape to long for grouped bars
    const rows = sufficient.flatMap(d => [
      { address: d.address, period: "Pre-opening (12 mo)", count: d.pre_count },
      { address: d.address, period: "Post-opening (12 mo)", count: d.post_count },
    ]);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: { label: "Non-traffic calls", grid: true },
      y: { label: null },
      color: { legend: true, domain: ["Pre-opening (12 mo)", "Post-opening (12 mo)"], range: ["#888", "#2a5f9e"] },
      marks: [
        Plot.barX(rows, {
          x: "count",
          y: "address",
          fill: "period",
          tip: true,
        }),
        Plot.ruleX([0]),
      ],
    });
    el.appendChild(plot);

    // Note about excluded sites
    const excluded = data.filter(d => String(d.post_sufficient).toLowerCase() !== "true");
    if (excluded.length) {
      const note = document.createElement("p");
      note.className = "chart-note";
      note.textContent = `Excluded (insufficient post data): ${excluded.map(d => d.address).join(", ")}.`;
      el.after(note);
    }
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 3: University core cluster trend with rolling avg and opening markers
async function renderClusterTrend() {
  const el = document.getElementById("chart-cluster-trend");
  if (!el) return;
  try {
    const [monthly, rolling, events] = await Promise.all([
      loadCsv("/data/charts/university_cluster_monthly.csv"),
      loadCsv("/data/charts/university_cluster_rolling.csv"),
      loadCsv("/data/charts/cluster_opening_events.csv"),
    ]);
    clearLoading(el);

    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 30,
      marginBottom: 50,
      x: { label: null, type: "utc" },
      y: { label: "Non-traffic calls / month", grid: true },
      marks: [
        Plot.ruleY([0], { stroke: "#ddd" }),
        Plot.areaY(monthly, {
          x: d => new Date(d.date),
          y: "non_traffic_count",
          fill: "#2a5f9e",
          fillOpacity: 0.1,
        }),
        Plot.line(monthly, {
          x: d => new Date(d.date),
          y: "non_traffic_count",
          stroke: "#2a5f9e",
          strokeOpacity: 0.35,
          strokeWidth: 1,
        }),
        Plot.line(rolling, {
          x: d => new Date(d.date),
          y: "rolling_3mo_avg",
          stroke: "#2a5f9e",
          strokeWidth: 2.5,
          tip: true,
        }),
        ...openingMarks(events),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 4: San Pablo node trend
async function renderSanPabloTrend() {
  const el = document.getElementById("chart-sp-trend");
  if (!el) return;
  try {
    const [monthly, rolling, events] = await Promise.all([
      loadCsv("/data/charts/san_pablo_monthly.csv"),
      loadCsv("/data/charts/san_pablo_rolling.csv"),
      loadCsv("/data/charts/san_pablo_opening_events.csv"),
    ]);
    clearLoading(el);

    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 30,
      marginBottom: 50,
      x: { label: null, type: "utc" },
      y: { label: "Non-traffic calls / month", grid: true },
      marks: [
        Plot.ruleY([0], { stroke: "#ddd" }),
        Plot.areaY(monthly, {
          x: d => new Date(d.date),
          y: "non_traffic_count",
          fill: "#c47a00",
          fillOpacity: 0.1,
        }),
        Plot.line(monthly, {
          x: d => new Date(d.date),
          y: "non_traffic_count",
          stroke: "#c47a00",
          strokeOpacity: 0.35,
          strokeWidth: 1,
        }),
        Plot.line(rolling, {
          x: d => new Date(d.date),
          y: "rolling_3mo_avg",
          stroke: "#c47a00",
          strokeWidth: 2.5,
          tip: true,
        }),
        ...openingMarks(events),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 5: Indexed comparison (university core + san pablo + controls, baseline = 100)
async function renderIndexedComparison() {
  const el = document.getElementById("chart-index");
  if (!el) return;
  try {
    const indexed = await loadCsv("/data/charts/corridor_vs_controls_index.csv");
    clearLoading(el);

    const parsed = indexed.map(d => ({ ...d, date: new Date(d.date) }));

    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 30,
      marginBottom: 50,
      x: { label: null, type: "utc" },
      y: { label: "Index (baseline = 100)", grid: true },
      color: { legend: true, label: "Area" },
      marks: [
        Plot.ruleY([100], { stroke: "#999", strokeDasharray: "2 2" }),
        Plot.line(parsed, {
          x: "date",
          y: "index_value",
          stroke: "label",
          strokeWidth: 2,
          tip: true,
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 6: Spillover — pre/post grouped bars by site and zone
async function renderSpillover() {
  const el = document.getElementById("chart-spillover");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/zone_comparison_nontraffic_calls.csv");
    clearLoading(el);

    if (!data || data.length === 0) {
      renderError(el, "Spillover data not yet available.");
      return;
    }

    // Reshape: one row per site+zone+period for grouped bars
    const zoneOrder = ["site_block", "adjacent_blocks", "wider_nearby"];
    const zoneLabel = { site_block: "100m zone", adjacent_blocks: "100–300m", wider_nearby: "300–600m" };

    const rows = data.flatMap(d => [
      { address: d.address, zone: zoneLabel[d.zone] ?? d.zone, period: "Pre-opening", count: d.pre_count },
      ...(String(d.post_sufficient).toLowerCase() === "true"
        ? [{ address: d.address, zone: zoneLabel[d.zone] ?? d.zone, period: "Post-opening", count: d.post_count }]
        : []),
    ]);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      x: { label: "Non-traffic calls (12-month window)", grid: true },
      fy: { label: null, padding: 0.2 },
      color: { legend: true, domain: ["Pre-opening", "Post-opening"], range: ["#888", "#2a5f9e"] },
      marks: [
        Plot.barX(rows, {
          x: "count",
          y: "zone",
          fill: "period",
          fy: "address",
          tip: true,
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

renderConcentration();
renderPrePost();
renderClusterTrend();
renderSanPabloTrend();
renderIndexedComparison();
renderSpillover();
