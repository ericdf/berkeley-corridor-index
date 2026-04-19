"""Compute 12-month pre/post non-traffic call counts for each site.

Post-period is marked insufficient when less than POST_COVERAGE_THRESHOLD of
the window falls within the available data range. Pre count is always shown;
post fields are null for insufficient windows.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dateutil.relativedelta import relativedelta
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    CHARTS_DIR, INTERIM_DIR,
    ensure_dirs, load_sites, load_study_params, log,
)

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
POST_COVERAGE_THRESHOLD = 0.50  # require 6 of 12 months of post-window to be in data


def count_calls_in_zone(calls_gdf: gpd.GeoDataFrame, zone_poly, date_start: pd.Timestamp, date_end: pd.Timestamp) -> int:
    mask = (calls_gdf["event_date"] >= date_start) & (calls_gdf["event_date"] < date_end) & calls_gdf["is_non_traffic"]
    subset = calls_gdf[mask].to_crs(CRS_PROJ)
    return int(subset.geometry.within(zone_poly).sum())


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    window = params["pre_post_window_months"]
    radius_m = params["zones"]["wider_nearby_m"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    data_max_date = df["event_date"].max()

    geometry = gpd.points_from_xy(df["lon"], df["lat"])
    calls_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS_GEO)

    rows = []
    for site in sites:
        opening = pd.Timestamp(site["opening_date"])
        pre_start = opening - relativedelta(months=window)
        post_end = opening + relativedelta(months=window)

        pt = Point(site["lon"], site["lat"])
        zone_poly = (
            gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO)
            .to_crs(CRS_PROJ)
            .geometry.buffer(radius_m)
            .iloc[0]
        )

        pre_count = count_calls_in_zone(calls_gdf, zone_poly, pre_start, opening)

        # Determine whether post-period has sufficient data coverage
        post_days_total = (post_end - opening).days
        post_days_available = max((min(data_max_date, post_end) - opening).days, 0)
        post_coverage = post_days_available / post_days_total if post_days_total > 0 else 0
        post_sufficient = post_coverage >= POST_COVERAGE_THRESHOLD

        # Always compute partial post count for operator visibility
        data_end = min(data_max_date, post_end)
        partial_post_count = count_calls_in_zone(calls_gdf, zone_poly, opening, data_end)

        if post_sufficient:
            post_count = partial_post_count
            pct_change = round((post_count - pre_count) / pre_count * 100, 1) if pre_count > 0 else None
            log(f"{site['address']}: pre={pre_count}, post={post_count}, change={pct_change}%")
        else:
            post_count = None
            pct_change = None
            # Annualize the partial count so it's comparable to the 12-month pre figure
            annualized = round(partial_post_count / post_coverage) if post_coverage > 0 else None
            pre_rate = round(pre_count / window) if pre_count else 0
            log(
                f"{site['address']}: pre={pre_count} ({pre_rate}/mo avg) | "
                f"PARTIAL POST ({post_coverage:.0%} of window, {post_days_available}d): "
                f"{partial_post_count} calls observed, ~{annualized} annualized — "
                f"{'ELEVATED vs pre' if annualized and pre_count and annualized > pre_count * 1.2 else 'within normal range vs pre'}"
            )

        rows.append({
            "site_id": site["id"],
            "address": site["address"],
            "opening_date": site["opening_date"],
            "pre_start": pre_start.date().isoformat(),
            "pre_end": opening.date().isoformat(),
            "post_start": opening.date().isoformat(),
            "post_end": post_end.date().isoformat(),
            "pre_count": pre_count,
            "post_count": post_count,
            "pct_change": pct_change,
            "post_sufficient": str(post_sufficient).lower(),
            "post_coverage_pct": round(post_coverage * 100, 1),
        })

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "pre_post_site_nontraffic_calls.csv", index=False)
    log("Wrote pre_post_site_nontraffic_calls.csv")
    return result


if __name__ == "__main__":
    main()
