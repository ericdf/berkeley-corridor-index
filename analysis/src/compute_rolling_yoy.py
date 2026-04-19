"""Compute rolling 3-month year-over-year comparisons for each site.

For each 3-month window in the data, compares call counts year-over-year
so that seasonal patterns don't bias the before/after reading.
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


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    window_mo = params["rolling_yoy_window_months"]
    radius_m = params["zones"]["wider_nearby_m"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    min_year = df["event_date"].dt.year.min()
    max_year = df["event_date"].dt.year.max()

    rows = []
    for site in sites:
        pt = Point(site["lon"], site["lat"])
        site_gdf = gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO).to_crs(CRS_PROJ)
        zone = site_gdf.geometry.buffer(radius_m).iloc[0]

        site_calls = calls_gdf[calls_gdf.geometry.within(zone)].copy()
        opening = pd.Timestamp(site["opening_date"])

        for year in range(min_year + 1, max_year + 1):
            for start_month in range(1, 13):
                window_start = pd.Timestamp(year=year, month=start_month, day=1)
                window_end = window_start + relativedelta(months=window_mo)
                prev_start = window_start - relativedelta(years=1)
                prev_end = window_end - relativedelta(years=1)

                if window_end > pd.Timestamp.now():
                    continue

                curr_count = len(site_calls[
                    (site_calls["event_date"] >= window_start) &
                    (site_calls["event_date"] < window_end)
                ])
                prev_count = len(site_calls[
                    (site_calls["event_date"] >= prev_start) &
                    (site_calls["event_date"] < prev_end)
                ])

                pct = ((curr_count - prev_count) / prev_count * 100) if prev_count > 0 else None

                rows.append({
                    "site_id": site["id"],
                    "address": site["address"],
                    "window_start": window_start.date().isoformat(),
                    "window_end": window_end.date().isoformat(),
                    "year": year,
                    "month": start_month,
                    "current_count": curr_count,
                    "prior_year_count": prev_count,
                    "yoy_pct_change": round(pct, 1) if pct is not None else None,
                    "is_post_opening": window_start >= opening,
                })

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "rolling_3mo_yoy_nontraffic_calls.csv", index=False)
    log("Wrote rolling_3mo_yoy_nontraffic_calls.csv")
    return result


if __name__ == "__main__":
    main()
