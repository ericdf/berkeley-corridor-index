const fs = require("fs");
const path = require("path");

module.exports = function () {
  const p = path.resolve(__dirname, "../../../data/processed/metadata/build.json");
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return { build_timestamp: "unknown", git_sha: "unknown", data_refresh_date: "unknown" };
  }
};
