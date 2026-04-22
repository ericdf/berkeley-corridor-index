const _BASE = (window.BASE_PATH || "/").replace(/\/$/, "");

fetch(_BASE + "/data/metadata/build.json")
  .then(r => r.json())
  .then(d => {
    document.getElementById("build-meta").innerHTML = `
      <table>
        <tr><th>Build time</th><td>${d.build_timestamp}</td></tr>
        <tr><th>Git SHA</th><td>${d.git_sha}</td></tr>
        <tr><th>Data refreshed</th><td>${d.data_refresh_date}</td></tr>
      </table>`;
  })
  .catch(() => {
    document.getElementById("build-meta").textContent = "Build metadata not available.";
  });
