"""Compute monthly non-traffic calls in each site's immediate zone.

Secondary / descriptive output only. Used for site profile charts.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ensure_dirs, load_sites, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    radius_m = params["immediate_zone_m"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    all_rows = []
    for site in sites:
        zone_poly = (
            gpd.GeoDataFrame(geometry=[Point(site["lon"], site["lat"])], crs=CRS_GEO)
            .to_crs(CRS_PROJ)
            .geometry.buffer(radius_m)
            .iloc[0]
        )
        site_calls = calls_gdf[calls_gdf.geometry.within(zone_poly)].copy()
        site_calls["month"] = site_calls["event_date"].dt.to_period("M")

        monthly = (
            site_calls.groupby("month")
            .size()
            .reset_index(name="non_traffic_count")
        )
        monthly["date"] = monthly["month"].dt.to_timestamp()
        monthly["year"] = monthly["date"].dt.year
        monthly["month_num"] = monthly["date"].dt.month
        monthly["site_id"] = site["id"]
        monthly["address"] = site["address"]
        monthly["opening_date"] = site["opening_date"]
        monthly["is_post_opening"] = monthly["date"] >= pd.Timestamp(site["opening_date"])
        all_rows.append(monthly[["site_id", "address", "opening_date",
                                  "year", "month_num", "date",
                                  "non_traffic_count", "is_post_opening"]])

    result = pd.concat(all_rows, ignore_index=True).sort_values(["site_id", "date"])
    result.to_csv(CHARTS_DIR / "property_immediate_zone_monthly.csv", index=False)
    log(f"Wrote property_immediate_zone_monthly.csv ({len(result)} site-month rows)")
    return result


if __name__ == "__main__":
    main()
