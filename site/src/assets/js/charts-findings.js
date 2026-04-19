// Findings page charts using Observable Plot

async function loadCsv(path) {
  const res = await fetch(path);
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

// Chart 1: Corridor trend with rolling average and opening markers
async function renderCorridorTrend() {
  const el = document.getElementById("chart-corridor-trend");
  if (!el) return;
  try {
    const [monthly, rolling, events] = await Promise.all([
      loadCsv("/data/charts/corridor_monthly_calls.csv"),
      loadCsv("/data/charts/corridor_rolling_3mo_avg.csv"),
      loadCsv("/data/charts/corridor_opening_events.csv"),
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

// Chart 2: Indexed comparison (corridor vs controls, baseline = 100)
async function renderIndexedComparison() {
  const el = document.getElementById("chart-index");
  if (!el) return;
  try {
    const [indexed, events] = await Promise.all([
      loadCsv("/data/charts/corridor_vs_controls_index.csv"),
      loadCsv("/data/charts/corridor_opening_events.csv"),
    ]);
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
        ...openingMarks(events),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 3: Active sites vs corridor call volume
async function renderActiveSites() {
  const el = document.getElementById("chart-active-sites");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/cumulative_openings_effects.csv");
    clearLoading(el);

    const parsed = data.map(d => ({ ...d, date: new Date(d.date) }));

    // Dual panel: calls on top, active sites on bottom
    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 10,
      marginBottom: 50,
      x: { label: null, type: "utc" },
      fy: { label: null },
      marks: [
        Plot.ruleY([0], { stroke: "#ddd" }),
        Plot.areaY(parsed, {
          x: "date",
          y: "non_traffic_count",
          fy: () => "Non-traffic calls / month",
          fill: "#2a5f9e",
          fillOpacity: 0.15,
        }),
        Plot.line(parsed, {
          x: "date",
          y: "non_traffic_count",
          fy: () => "Non-traffic calls / month",
          stroke: "#2a5f9e",
          strokeWidth: 1.5,
          tip: true,
        }),
        Plot.step(parsed, {
          x: "date",
          y: "active_sites",
          fy: () => "Active sites",
          stroke: "#c00",
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

// Chart 4: Immediate property zones — small multiples per site
async function renderPropertyLocal() {
  const el = document.getElementById("chart-property-local");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/property_immediate_zone_monthly.csv");
    clearLoading(el);

    const parsed = data.map(d => ({ ...d, date: new Date(d.date) }));

    const plot = Plot.plot({
      marginLeft: 50,
      marginTop: 10,
      marginBottom: 50,
      x: { label: null, type: "utc" },
      y: { label: "Calls / month", grid: true },
      fy: { label: null, padding: 0.25 },
      marks: [
        Plot.ruleY([0], { stroke: "#ddd" }),
        Plot.line(parsed, {
          x: "date",
          y: "non_traffic_count",
          fy: "address",
          stroke: "#2a5f9e",
          strokeWidth: 1.5,
          tip: true,
        }),
        // Opening date marker per site
        ...parsed
          .filter((d, i, arr) => i === arr.findIndex(r => r.site_id === d.site_id))
          .map(d => Plot.ruleX([new Date(d.opening_date)], {
            fy: () => d.address,
            stroke: "#c00",
            strokeDasharray: "3 3",
            strokeOpacity: 0.7,
          })),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

renderCorridorTrend();
renderIndexedComparison();
renderActiveSites();
renderPropertyLocal();
