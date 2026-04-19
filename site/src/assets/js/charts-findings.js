// Findings page charts using Observable Plot

async function loadCsv(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return d3.csvParse(await res.text(), d3.autoType);
}

function clearLoading(el) {
  el.querySelector(".chart-loading")?.remove();
}

function renderError(el, msg) {
  el.innerHTML = `<p class="chart-loading" style="color:#c00">${msg}</p>`;
}

// Pre/post: side-by-side bars per site; sites with null post get a note instead of an After bar
async function renderPrePost() {
  const el = document.getElementById("chart-prepost");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/pre_post_site_nontraffic_calls.csv");
    clearLoading(el);

    const long = [];
    const insufficient = [];
    for (const row of data) {
      long.push({ address: row.address, period: "Before", count: row.pre_count });
      if (String(row.post_sufficient).toLowerCase() === "true") {
        long.push({ address: row.address, period: "After", count: row.post_count });
      } else {
        insufficient.push({ address: row.address, count: row.pre_count });
      }
    }

    const plot = Plot.plot({
      marginLeft: 160,
      marginBottom: 40,
      x: { label: "Non-traffic calls (12-month period)", grid: true },
      y: { label: null },
      color: { legend: true, domain: ["Before", "After"], range: ["#9aabbd", "#2a5f9e"] },
      marks: [
        Plot.barX(long, {
          x: "count",
          y: "address",
          fill: "period",
          dx: d => d.period === "After" ? 1 : 0,
          tip: true,
        }),
        // Label sites with insufficient post data
        Plot.text(insufficient, {
          x: "count",
          y: "address",
          text: () => "  ← insufficient post data",
          textAnchor: "start",
          fill: "#888",
          fontSize: 11,
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

// Zone spillover: one facet per site, before/after bars per zone
async function renderSpillover() {
  const el = document.getElementById("chart-spillover");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/zone_comparison_nontraffic_calls.csv");
    clearLoading(el);

    const zoneLabel = {
      site_block: "Zone 1 — site block",
      adjacent_blocks: "Zone 2 — adjacent",
      wider_nearby: "Zone 3 — wider area",
    };

    const long = [];
    for (const row of data) {
      const sufficient = String(row.post_sufficient).toLowerCase() === "true";
      long.push({ address: row.address, zone: zoneLabel[row.zone] ?? row.zone, period: "Before", count: row.pre_count });
      if (sufficient) {
        long.push({ address: row.address, zone: zoneLabel[row.zone] ?? row.zone, period: "After", count: row.post_count });
      }
    }

    const plot = Plot.plot({
      marginLeft: 180,
      marginBottom: 40,
      x: { label: "Non-traffic calls (12-month period)", grid: true },
      y: { label: null },
      fy: { label: null, padding: 0.3 },
      color: { legend: true, domain: ["Before", "After"], range: ["#9aabbd", "#2a5f9e"] },
      marks: [
        Plot.barX(long, {
          x: "count",
          y: "zone",
          fy: "address",
          fill: "period",
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

// Rolling YoY: one line per site with opening-date markers
async function renderRolling() {
  const el = document.getElementById("chart-rolling");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/rolling_3mo_yoy_nontraffic_calls.csv");
    clearLoading(el);

    const parsed = data.map(d => ({ ...d, window_start: new Date(d.window_start) }));

    // Collect one opening-date marker per site (first window where is_post_opening flips true)
    const openings = [];
    const seen = new Set();
    for (const d of parsed) {
      if ((d.is_post_opening === true || d.is_post_opening === "True") && !seen.has(d.site_id)) {
        openings.push({ site_id: d.site_id, address: d.address, x: d.window_start });
        seen.add(d.site_id);
      }
    }

    const plot = Plot.plot({
      marginLeft: 60,
      marginBottom: 50,
      x: { label: "3-month window start", type: "utc" },
      y: { label: "YoY % change", tickFormat: d => `${d >= 0 ? "+" : ""}${d}%`, grid: true },
      color: { legend: true, label: "Site" },
      marks: [
        Plot.ruleY([0], { stroke: "#bbb" }),
        Plot.line(parsed, {
          x: "window_start",
          y: "yoy_pct_change",
          stroke: "address",
          tip: true,
        }),
        Plot.ruleX(openings, {
          x: "x",
          stroke: "address",
          strokeDasharray: "4 3",
          strokeOpacity: 0.6,
        }),
      ],
    });
    el.appendChild(plot);
  } catch (e) {
    renderError(el, "Chart data not yet available. Run the analysis pipeline first.");
    console.warn(e);
  }
}

// Control corridors line chart
async function renderControls() {
  const el = document.getElementById("chart-controls");
  if (!el) return;
  try {
    const data = await loadCsv("/data/charts/corridor_controls.csv");
    clearLoading(el);

    const parsed = data.map(d => ({ ...d, window_start: new Date(d.window_start) }));

    const plot = Plot.plot({
      marginLeft: 60,
      marginBottom: 50,
      x: { label: "3-month window start", type: "utc" },
      y: { label: "YoY % change", tickFormat: d => `${d >= 0 ? "+" : ""}${d}%`, grid: true },
      color: { legend: true, label: "Corridor" },
      marks: [
        Plot.ruleY([0], { stroke: "#bbb" }),
        Plot.line(parsed, {
          x: "window_start",
          y: "yoy_pct_change",
          stroke: "corridor_label",
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

renderPrePost();
renderSpillover();
renderRolling();
renderControls();
