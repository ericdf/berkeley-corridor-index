---
layout: base.njk
title: Data Sources
description: Source data, fetch dates, and downloadable files for the Berkeley interim housing analysis.
---

# Data Sources

## Source Data

All source data comes from the City of Berkeley's public safety open data.

| Dataset | Source |
|---------|--------|
| Police Calls for Service | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |
| Police Stop Data (RIPA) | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |
| Council Districts | [berkeleyca.gov — Police Data](https://berkeleyca.gov/safety-health/police/data-crime-calls-service-stops-and-use-force) |

---

## Processing Notes

- All geographic filtering uses 4326 (WGS84) coordinates projected to UTM Zone 10N for distance calculations.
- Non-traffic call classification uses keyword matching on the `cvlegend` field. See `study_parameters.yml` for the full keyword list.
- Opening dates are approximate and based on publicly available records. See `sites.yml` to review or update them.
- The pipeline is fully reproducible from source data. See the [README](https://github.com/ericdf/berkeley-corridor-index) for instructions.
