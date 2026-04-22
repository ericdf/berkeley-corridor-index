# Methodology: Berkeley Interim Housing Site Analysis

## Overview

This analysis uses publicly available Berkeley Police Department data to measure the public safety impact of motel-to-shelter conversions on University Avenue and San Pablo Avenue. It employs five independent analytical approaches whose convergent findings strengthen the overall conclusions.

---

## Data Sources

### Calls for Service
Berkeley PD calls-for-service data, sourced from the City of Berkeley open data portal in GeoJSON format. Covers January 2021 through April 2026. Each record represents a citizen-initiated or officer-initiated call with a call type, timestamp, and block-level address. Coordinates are geocoded from block addresses. **Non-traffic calls** — the subset used for analysis — are defined as calls matching any of the following types: disturbance, noise, trespassing, suspicious person/vehicle, welfare check, mentally ill / 5150, theft, robbery, assault, battery, vandalism, encampment, fight, person down.

### RIPA Stop Data
California's Racial and Identity Profiling Act (RIPA) requires law enforcement agencies to record data on every pedestrian and vehicle stop. Two datasets are used:
- **Old format** (RIPAData.csv): October 2020 – December 2023
- **New format** (Berkeley_PD_Stop_Data_2024-Current.csv): January 2024 – April 2026

The new format adds a `PerceivedPersonUnhoused` field not present in the old format. Both formats include GPS coordinates, stop type (pedestrian / vehicular), city of residence, basis of suspicion, result of stop, and offense codes. Datasets are combined with the old format trimmed at December 2023 to avoid double-counting.

### OSM Road Network
Primary and secondary road centerlines for Berkeley from OpenStreetMap, used to define corridor geographies for the trajectory index analysis.

---

## Study Sites

| ID | Address | Program Type | Opening Date |
|----|---------|-------------|--------------|
| site_1461 | 1461 University Ave | Interim housing / shelter | July 1, 2021 |
| site_1619 | 1619 University Ave | Reentry / supportive housing | July 31, 2023 |
| site_1761 | 1761 University Ave | Interim housing | February 1, 2026 |
| site_golden_bear | 1620 San Pablo Ave | Permanent supportive housing | January 1, 2023 |

The Hope Center (2012 Berkeley Way, opened September 2022) is analyzed as a related facility whose impact propagates to the North Shattuck corridor.

---

## Analytical Methods

### 1. Site-Level Pre/Post Comparison
For each site, non-traffic call counts and pedestrian stop counts are measured within a 100-meter buffer for the 12-month window before opening and all available months after opening. Rates are normalized to calls/stops per month to allow comparison across windows of different lengths. The 100-meter buffer is chosen to capture activity closely associated with the facility while limiting bleed from adjacent unrelated activity.

### 2. Call Type Shift Analysis
Within the same 100-meter site buffers, calls are categorized into 15 types using the raw call type field. Pre- and post-opening rates per month are compared for each category. This answers whether the *composition* of police demand changed, not just the volume.

### 3. Corridor Trajectory Index
All named primary and secondary Berkeley corridors are extracted from OSM road data, buffered 75 meters, and monthly non-traffic call counts are computed for each. An index is constructed using the 2021 monthly average as baseline (= 100). Annual averages of the index are compared across corridors to identify which improved, held flat, or worsened over the study period. Long corridors with distinct character zones (Shattuck Avenue) are excluded from comparison as heterogeneous.

### 4. North Shattuck Time Series
A dedicated monthly call series is computed for the North Shattuck corridor (Shattuck Avenue north of University Avenue, buffered 75 meters) to test whether the Hope Center opening in September 2022 produced a detectable step-change. A 3-month rolling average is used to smooth month-to-month variance.

### 5. Stop Offense Profile
Pedestrian stops within 100-meter site buffers are categorized by offense type using the `offense_raw` field (SuspectedViolation in old format; best available charge field in new format). Site offense distributions are compared to the citywide pedestrian stop baseline. This provides an independent, officer-recorded characterization of the activity near each site.

### 6. City of Residence Analysis
The `CityOfResidence` field from stop data is used to measure what fraction of pedestrian stops near each site involve individuals from outside Berkeley, compared to the citywide baseline. This tests whether shelter siting draws a non-local population into Berkeley as an incremental cost to the city.

---

## Reporting and Enforcement Context

This study covers 2021–2026, a period during which Berkeley experienced documented reductions in both citizen reporting and proactive policing. Following the murder of George Floyd in May 2020, Berkeley's city government pursued an aggressive agenda to reduce police department staffing and scope. Sworn officer headcount declined substantially over the study period. Calling the police on unhoused individuals became socially stigmatized in Berkeley's public discourse, and residents were actively discouraged from doing so by community organizations and elected officials.

These factors create a systematic downward bias in both the calls-for-service and stop data used in this analysis. Citizen calls undercount actual incidents because a meaningful share of residents chose not to call. Officer-initiated stops undercount actual enforcement contacts because officers facing heightened scrutiny reduced proactive engagement.

**The consequence for interpretation is directional and consistent: the increases documented near shelter sites are conservative estimates of the true neighborhood impact.** The observed changes occurred against a measurable headwind of reduced reporting and enforcement. That the signal is detectable at all — and that it diverges so clearly from comparison corridors where conditions improved over the same period — suggests the underlying change in neighborhood conditions was substantial.

Analysts who wish to challenge these findings on underenforcement grounds face a symmetric problem: if reduced enforcement suppressed the data near shelter sites, it suppressed the data on comparison corridors equally. The divergence between corridors remains, and grows more difficult to explain absent the shelter siting decisions.

---

## Limitations

- **Opening dates** for some sites are approximate. Sensitivity to opening date assumptions has not been formally tested, though the corridor-level findings do not depend on any single site's opening date.
- **100-meter buffer** captures activity near each facility but cannot distinguish on-site incidents from activity by non-residents passing through the area.
- **Pre-period length varies** across sites. Site 1461 has only 9 months of pre-opening stop data, falling entirely within the COVID-19 period of suppressed activity. Pre/post stop comparisons for 1461 should be interpreted cautiously.
- **Sample sizes** for stop-level analysis are modest at individual sites (35–144 pedestrian stops per site over the full period). Percentage differences under 5 points should not be treated as reliable.
- **1619 University Ave occupancy ramp:** The site was originally intended for a recalcitrant encampment population that declined placement. The city pivoted to a different population, and the site reached only ~14 of 23 rooms occupied by February 2024 with a continued slow ramp. Full occupancy date is unknown. Post-opening figures for this site understate steady-state impact.
- **Correlation, not causation.** This is an observational study. The findings are consistent with a causal interpretation and inconsistent with the most plausible alternative explanations, but do not constitute proof of causation.

---

## Reproducibility

All analysis code is in `analysis/src/`. The full pipeline is orchestrated by `analysis/run_pipeline.py`. Raw data must be staged in `data/raw/current/` before running. See `analysis/config/` for site definitions, study parameters, and incumbent facility list.
