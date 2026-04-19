"""Compute zone spillover: compare pre/post counts by zone ring.

Zone 1 = site block (innermost buffer)
Zone 2 = adjacent blocks (annular ring)
Zone 3 = wider nearby (outermost annular ring)
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dateutil.relativedelta import relativedelta
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    CHARTS_DIR, INTERIM_DIR, MAPS_DIR,
    ensure_dirs, load_sites, load_study_params, log,
)

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
POST_COVERAGE_THRESHOLD = 0.50


def count_in_polygon(calls_gdf: gpd.GeoDataFrame, poly_gdf: gpd.GeoDataFrame,
                     date_start: pd.Timestamp, date_end: pd.Timestamp) -> int:
    mask = (calls_gdf["event_date"] >= date_start) & (calls_gdf["event_date"] < date_end)
    subset = calls_gdf[mask & calls_gdf["is_non_traffic"]].to_crs(CRS_PROJ).reset_index(drop=True)
    zone_poly = poly_gdf.to_crs(CRS_PROJ).geometry.union_all()
    return int(subset.geometry.within(zone_poly).sum())


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    window = params["pre_post_window_months"]
    z = params["zones"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    data_max_date = df["event_date"].max()
    geometry = gpd.points_from_xy(df["lon"], df["lat"])
    calls_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS_GEO)

    zone_files = {
        "site_block": MAPS_DIR / "site_block_zones.geojson",
        "adjacent_blocks": MAPS_DIR / "adjacent_block_zones.geojson",
        "wider_nearby": MAPS_DIR / "wider_nearby_zones.geojson",
    }
    zones = {k: gpd.read_file(v) for k, v in zone_files.items()}

    rows = []
    for site in sites:
        opening = pd.Timestamp(site["opening_date"])
        pre_start = opening - relativedelta(months=window)
        post_end = opening + relativedelta(months=window)

        post_days_total = (post_end - opening).days
        post_days_available = max((min(data_max_date, post_end) - opening).days, 0)
        post_sufficient = (post_days_available / post_days_total) >= POST_COVERAGE_THRESHOLD if post_days_total > 0 else False

        for zone_name, zone_gdf in zones.items():
            site_zone = zone_gdf[zone_gdf["site_id"] == site["id"]]
            if site_zone.empty:
                continue

            pre = count_in_polygon(calls_gdf, site_zone, pre_start, opening)

            if post_sufficient:
                post = count_in_polygon(calls_gdf, site_zone, opening, post_end)
                pct = round((post - pre) / pre * 100, 1) if pre > 0 else None
            else:
                post = None
                pct = None

            rows.append({
                "site_id": site["id"],
                "address": site["address"],
                "zone": zone_name,
                "pre_count": pre,
                "post_count": post,
                "pct_change": pct,
                "post_sufficient": str(post_sufficient).lower(),
            })

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "zone_comparison_nontraffic_calls.csv", index=False)
    log("Wrote zone_comparison_nontraffic_calls.csv")
    return result


if __name__ == "__main__":
    main()
