// Homepage hero chart — corridor monthly calls with opening markers

async function loadCsv(path) {
  const res = await fetch(path);
  if (!res.ok) return null;
  return d3.csvParse(await res.text(), d3.autoType);
}

async function init() {
  const el = document.getElementById("chart-hero");
  if (!el) return;

  const [monthly, events, rolling] = await Promise.all([
    loadCsv("/data/charts/corridor_monthly_calls.csv"),
    loadCsv("/data/charts/corridor_opening_events.csv"),
    loadCsv("/data/charts/corridor_rolling_3mo_avg.csv"),
  ]);

  if (!monthly) {
    el.innerHTML = `<p class="chart-loading" style="color:#888">Run the analysis pipeline to generate chart data.</p>`;
    return;
  }

  el.querySelector(".chart-loading")?.remove();

  const dates = monthly.map(d => new Date(d.date));
  const openingDates = events ? events.map(d => ({ date: new Date(d.opening_date), address: d.address, seq: d.sequence })) : [];
  const rollingData = rolling ? rolling.map(d => ({ ...d, date: new Date(d.date) })) : [];

  const marks = [
    Plot.ruleY([0], { stroke: "#ddd" }),
    Plot.areaY(monthly, {
      x: d => new Date(d.date),
      y: "non_traffic_count",
      fill: "#2a5f9e",
      fillOpacity: 0.12,
    }),
    Plot.line(monthly, {
      x: d => new Date(d.date),
      y: "non_traffic_count",
      stroke: "#2a5f9e",
      strokeOpacity: 0.4,
      strokeWidth: 1,
    }),
  ];

  if (rollingData.length) {
    marks.push(Plot.line(rollingData, {
      x: "date",
      y: "rolling_3mo_avg",
      stroke: "#2a5f9e",
      strokeWidth: 2.5,
      tip: true,
    }));
  }

  openingDates.forEach(({ date, address, seq }) => {
    marks.push(Plot.ruleX([date], { stroke: "#c00", strokeDasharray: "4 3", strokeOpacity: 0.7 }));
    marks.push(Plot.text([{ date, address, seq }], {
      x: "date",
      y: () => null,
      text: d => `${d.seq}`,
      frameAnchor: "top",
      dy: 6,
      fill: "#c00",
      fontSize: 10,
      fontWeight: "bold",
    }));
  });

  const plot = Plot.plot({
    marginLeft: 50,
    marginTop: 30,
    marginBottom: 50,
    x: { label: null, type: "utc" },
    y: { label: "Non-traffic calls / month", grid: true },
    marks,
  });

  el.appendChild(plot);

  // Opening legend below chart
  if (openingDates.length) {
    const legend = document.createElement("p");
    legend.className = "chart-note";
    legend.innerHTML = openingDates
      .map(d => `<span style="color:#c00;font-weight:bold">${d.seq}</span> ${d.address} (${new Date(d.date).toLocaleDateString("en-US", { month: "short", year: "numeric" })})`)
      .join(" &nbsp;·&nbsp; ");
    el.after(legend);
  }
}

init().catch(console.error);
