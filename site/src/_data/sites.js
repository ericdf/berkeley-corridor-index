const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

module.exports = function () {
  const p = path.resolve(__dirname, "../../../analysis/config/sites.yml");
  const raw = yaml.load(fs.readFileSync(p, "utf8"));
  return raw.sites;
};
