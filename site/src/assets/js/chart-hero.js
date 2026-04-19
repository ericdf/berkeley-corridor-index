// Homepage hero chart — share of study-area calls within each site's 100m zone

async function loadCsv(path) {
  const res = await fetch(path);
  if (!res.ok) return null;
  return d3.csvParse(await res.text(), d3.autoType);
}

async function init() {
  const el = document.getElementById("chart-hero");
  if (!el) return;

  const data = await loadCsv("/data/charts/concentration_share.csv");

  if (!data) {
    el.innerHTML = `<p class="chart-loading" style="color:#888">Run the analysis pipeline to generate chart data.</p>`;
    return;
  }

  el.querySelector(".chart-loading")?.remove();

  // Per-site, "all" period rows, excluding the "all_sites" summary row
  const siteRows = data
    .filter(d => d.site_id !== "all_sites" && d.period === "all")
    .sort((a, b) => b.share_of_study_area_pct - a.share_of_study_area_pct);

  const plot = Plot.plot({
    marginLeft: 180,
    marginTop: 20,
    marginBottom: 50,
    x: {
      label: "Share of study-area non-traffic calls (%)",
      grid: true,
    },
    y: {
      label: null,
    },
    marks: [
      Plot.barX(siteRows, {
        x: "share_of_study_area_pct",
        y: "address",
        fill: "#2a5f9e",
        fillOpacity: 0.75,
        tip: true,
        title: d => `${d.address}\n${d.share_of_study_area_pct}% of study-area calls\n(${d.calls_in_zone.toLocaleString()} calls in 100m zone)`,
      }),
      Plot.ruleX([0]),
    ],
  });

  el.appendChild(plot);
}

init().catch(console.error);
