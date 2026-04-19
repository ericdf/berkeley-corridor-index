const { DateTime } = require("luxon");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("site/src/assets");
  eleventyConfig.addPassthroughCopy({ "data/processed/downloads": "downloads" });
  eleventyConfig.addPassthroughCopy({ "data/processed/charts": "data/charts" });
  eleventyConfig.addPassthroughCopy({ "data/processed/maps": "data/maps" });
  eleventyConfig.addPassthroughCopy({ "data/processed/metadata": "data/metadata" });

  eleventyConfig.addFilter("readableDate", (dateObj) =>
    DateTime.fromJSDate(dateObj, { zone: "utc" }).toFormat("LLL dd, yyyy")
  );

  eleventyConfig.addFilter("year", () => new Date().getFullYear());

  return {
    dir: {
      input: "site/src",
      output: "site/public",
      includes: "_includes",
      data: "_data",
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
