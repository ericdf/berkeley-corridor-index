// New findings charts: corridor rankings, call type shift, North Shattuck, stop pre/post

const _BASE = (window.BASE_PATH || "/").replace(/\/$/, "");
async function loadCsv(path) {
  const res = await fetch(_BASE + path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return d3.csvParse(await res.text(), d3.autoType);
}

function clearLoading(el) { el.querySelector(".chart-loading")?.remove(); }
function renderError(el, msg) {
  el.innerHTML = `<p class="chart-loading" style="color:#c00">${msg}</p>`;
}

const SHELTER_CORRIDORS = new Set([
  "University Avenue (west of MLK)",
  "San Pablo Avenue (north)",
]);

// Chart 7: Corridor rankings — horizontal bars, worst to best
async function renderCorridorRankings() {
  const el = document.getElementById("chart-corridor-rankings");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/corridor_rankings.csv");
    clearLoading(el);

    // Exclude Shattuck halves (heterogeneous corridor)
    const rows = data
      .filter(d => !d.corridor.toLowerCase().includes("shattuck"))
      .sort((a, b) => b.trajectory_index - a.trajectory_index);

    // Shorten labels for display
    const LABEL_MAP = {
      "University Avenue (east of MLK)": "University Ave (east)",
      "University Avenue (west of MLK)": "University Ave (west) ●",
      "San Pablo Avenue (north)":        "San Pablo Ave (north) ●",
      "San Pablo Avenue (south)":        "San Pablo Ave (south)",
      "Telegraph Avenue (south)":        "Telegraph Ave (south)",
      "Telegraph Avenue (north)":        "Telegraph Ave (north)",
      "Adeline Street (south)":          "Adeline St (south)",
      "Adeline Street (north)":          "Adeline St (north)",
    };
    rows.forEach(d => { d.label = LABEL_MAP[d.corridor] || d.corridor; });

    const containerWidth = el.clientWidth || 680;
    const plot = Plot.plot({
      marginLeft: 190,
      marginTop: 20,
      marginBottom: 50,
      width: containerWidth,
      x: {
        label: "2025 call level vs. 2021 baseline (100 = flat)",
        grid: true,
        domain: [40, 200],
      },
      y: { label: null },
      color: {
        domain: [true, false],
        range: ["#c0392b", "#888"],
        legend: false,
      },
      marks: [
        Plot.ruleX([100], { stroke: "#666", strokeDasharray: "4 3", strokeWidth: 1.5 }),
        Plot.barX(rows, {
          x: "trajectory_index",
          y: "label",
          fill: d => SHELTER_CORRIDORS.has(d.corridor),
          sort: { y: "x", reverse: true },
          tip: true,
          title: d =>
            `${d.corridor}\n2021 avg: ${d.avg_monthly_2021} calls/mo\n2025 avg: ${d.avg_monthly_2025} calls/mo\nIndex: ${d.trajectory_index}`,
        }),
        Plot.text(rows, {
          x: d => d.trajectory_index + 2,
          y: "label",
          text: d => d.trajectory_index.toFixed(0),
          sort: { y: "x", reverse: true },
          fill: d => SHELTER_CORRIDORS.has(d.corridor) ? "#c0392b" : "#555",
          fontSize: 11,
          textAnchor: "start",
          dy: 1,
        }),
        Plot.ruleX([0]),
      ],
    });
    el.appendChild(plot);

    const note = document.createElement("p");
    note.className = "chart-note";
    note.style.color = "#c0392b";
    note.textContent = "Red bars = corridors with study shelter sites.";
    el.appendChild(note);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 8: Call type shift — small multiples, pre vs post bars per site
async function renderCallTypeShift() {
  const el = document.getElementById("chart-call-type-shift");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/call_type_shift_wide.csv");
    clearLoading(el);

    // Show only top-changed categories per site (rate_change >= 0.1 or <= -0.1)
    const rows = data
      .filter(d => d.opening_date != null && Math.abs(d.rate_change) >= 0.08)
      .flatMap(d => [
        { label: d.label, category: d.category, period: "Before opening", rate: d.pre_rate },
        { label: d.label, category: d.category, period: "After opening",  rate: d.post_rate },
      ]);

    const siteOrder = ["1461 University", "1619 University", "1761 University", "Golden Bear Inn", "Hope Center (Berkeley Way)"];

    const plot = Plot.plot({
      marginLeft: 160,
      marginTop: 30,
      marginBottom: 50,
      width: 680,
      x: { label: "Calls per month (100m zone)", grid: true },
      fy: { domain: siteOrder, label: null, padding: 0.15 },
      color: {
        legend: true,
        domain: ["Before opening", "After opening"],
        range: ["#aaa", "#2a5f9e"],
      },
      marks: [
        Plot.barX(rows, {
          x: "rate",
          y: "category",
          fill: "period",
          fy: "label",
          tip: true,
          title: d => `${d.label} — ${d.category}\n${d.period}: ${d.rate.toFixed(2)} calls/mo`,
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

// Chart 9: North Shattuck cascade — time series with Hope Center annotation
async function renderNorthShattuck() {
  const el = document.getElementById("chart-north-shattuck");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/north_shattuck_monthly.csv");
    clearLoading(el);

    const parsed = data.map(d => ({ ...d, date: new Date(d.date) }));
    const hopeCenter = new Date("2022-09-01");
    const preSignal  = new Date("2022-05-01");

    const plot = Plot.plot({
      marginLeft: 55,
      marginTop: 40,
      marginBottom: 50,
      width: 680,
      x: { label: null, type: "utc" },
      y: { label: "Non-traffic calls / month", grid: true },
      marks: [
        Plot.ruleY([0], { stroke: "#eee" }),
        // Shaded pre-signal zone
        Plot.rectX(
          [{ x1: preSignal, x2: hopeCenter }],
          { x1: "x1", x2: "x2", fill: "#f5c6c6", fillOpacity: 0.4 }
        ),
        Plot.areaY(parsed, {
          x: "date",
          y: "count",
          fill: "#2a5f9e",
          fillOpacity: 0.08,
        }),
        Plot.line(parsed, {
          x: "date",
          y: "count",
          stroke: "#2a5f9e",
          strokeOpacity: 0.3,
          strokeWidth: 1,
        }),
        Plot.line(parsed.filter(d => d.rolling_3mo_avg != null), {
          x: "date",
          y: "rolling_3mo_avg",
          stroke: "#2a5f9e",
          strokeWidth: 2.5,
          tip: true,
          title: d => `${d.date.toLocaleDateString("en-US",{month:"short",year:"numeric"})}: ${d.rolling_3mo_avg} (3mo avg)`,
        }),
        // Hope Center opening line
        Plot.ruleX([hopeCenter], {
          stroke: "#c0392b",
          strokeDasharray: "4 3",
          strokeWidth: 1.5,
        }),
        Plot.text([{ date: hopeCenter, label: "Hope Center opens" }], {
          x: "date",
          y: () => null,
          text: "label",
          frameAnchor: "top",
          dy: 8,
          dx: 4,
          fill: "#c0392b",
          fontSize: 10,
          textAnchor: "start",
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Chart 10: Pedestrian stop pre/post — paired horizontal bars
async function renderStopPrePost() {
  const el = document.getElementById("chart-stop-prepost");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/stop_prepost.csv");
    clearLoading(el);

    const rows = data
      .filter(d => d.stop_type === "pedestrian" && d.address !== "1761 University Ave")
      .flatMap(d => [
        { address: d.address, period: "Before opening", rate: d.pre_rate },
        { address: d.address, period: "After opening",  rate: d.post_rate },
      ]);

    const plot = Plot.plot({
      marginLeft: 170,
      marginTop: 20,
      marginBottom: 50,
      width: 560,
      x: { label: "Pedestrian stops per month (100m zone)", grid: true },
      y: { label: null },
      color: {
        legend: true,
        domain: ["Before opening", "After opening"],
        range: ["#aaa", "#c0392b"],
      },
      marks: [
        Plot.barX(rows, {
          x: "rate",
          y: "address",
          fill: "period",
          tip: true,
          title: d => `${d.address}\n${d.period}: ${d.rate.toFixed(2)} stops/mo`,
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

renderCorridorRankings();
renderCallTypeShift();
renderNorthShattuck();
renderStopPrePost();
