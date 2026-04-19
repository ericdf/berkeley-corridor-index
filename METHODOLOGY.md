# Berkeley Interim Housing Site Analysis: Methodology

## Purpose

This project examines whether several converted motel housing sites in Berkeley were followed by changes in nearby **non-traffic police calls for service**.

The goal is not to debate homelessness policy in general. The goal is to measure whether nearby public-safety demand changed after specific sites opened.

## Sites Studied

We focused on these University Avenue locations:

- 1461 University Ave  
- 1512 University Ave  
- 1619 University Ave  
- 1761 University Ave  

These properties were converted into various housing, shelter, or reentry programs at different times.

## Main Question

Did nearby police activity increase after these sites opened?

## Why We Used Non-Traffic Calls

Traffic stops and traffic collisions happen for many reasons unrelated to housing sites.

To better measure neighborhood impact, we focused on **non-traffic calls**, such as:

- disturbance  
- trespassing  
- suspicious person  
- welfare check  
- theft  
- mentally ill / 5150 related calls  
- similar public-safety or public-order calls

## Data Used

We used public Berkeley police datasets provided in GeoJSON and CSV formats, including:

- calls for service  
- stop data  
- arrest data  
- council district boundaries

The calls-for-service dataset was the most useful for before/after comparisons because it covered multiple years.

## Before / After Comparison

For each site, we identified an approximate opening date.

Then we compared:

- **12 months before opening**
- **12 months after opening**

This helps answer whether activity changed after the site began operating.

## Example

If a site opened in May 2022:

- Pre-period = May 2021 to April 2022  
- Post-period = May 2022 to April 2023

## Why This Matters

Comparing before and after the same location helps control for things that were already true about the area, such as:

- same street  
- same nearby businesses  
- same transit access  
- same neighborhood layout

## Comparison Areas

We also compared results to other busy Berkeley commercial corridors, including:

- North Shattuck  
- South Telegraph

These areas were used as rough controls because they also have traffic, pedestrians, shops, and transit access.

## Neighbor Impact Zones

To estimate impact on nearby residents and businesses, we divided areas into zones:

### Zone 1: Site Block

The block where the facility sits.

### Zone 2: Adjacent Blocks

The nearest surrounding blocks.

### Zone 3: Wider Nearby Area

Blocks farther away.

## Why We Did This

If only the site block increases, impacts may be contained on-site.

If adjacent blocks also increase, neighbors may be affected.

## Seasonal Checks

Some activity rises in warmer months or during the school year.

To avoid misleading results, we also used:

### Rolling 3-Month Year-over-Year Comparisons

Example:

- Feb–Apr 2025 compared with Feb–Apr 2026

This compares the same season in different years.

## What Counts as an Increase

We measured percentage change.

Example:

- 100 calls before  
- 150 calls after  

This equals a **50% increase**.

## Limits of the Study

This project does **not** prove every call was caused by a housing site.

Other factors can matter:

- citywide trends  
- economy  
- staffing changes  
- weather  
- reporting behavior  
- nearby developments

The results show association and timing patterns, not absolute proof of cause.

## Why This Still Matters

When multiple sites show similar increases after opening, especially nearby increases on adjacent blocks, that is useful evidence for public discussion.

## Bottom Line

We used a simple common-sense approach:

1. Find opening dates  
2. Compare before and after  
3. Compare with similar nearby areas  
4. Check whether neighbors were affected  
5. Use multiple time periods to reduce seasonal bias

This helps move the conversation from opinion to measurable facts.
