"""Compute monthly non-traffic call counts within the University Avenue corridor.

Primary corridor-level time series. Also produces corridor_opening_events.csv
(opening-date markers for chart annotations).
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, MAPS_DIR, ensure_dirs, load_sites, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    corridor = gpd.read_file(MAPS_DIR / "university_corridor_cluster.geojson").to_crs(CRS_PROJ)
    corridor_poly = corridor.geometry.iloc[0]

    in_corridor = calls_gdf[calls_gdf.geometry.within(corridor_poly)].copy()
    in_corridor["month"] = in_corridor["event_date"].dt.to_period("M")

    monthly = (
        in_corridor.groupby("month")
        .size()
        .reset_index(name="non_traffic_count")
    )
    monthly["date"] = monthly["month"].dt.to_timestamp()
    monthly["year"] = monthly["date"].dt.year
    monthly["month_num"] = monthly["date"].dt.month
    monthly = monthly[["year", "month_num", "date", "non_traffic_count"]].sort_values("date")
    monthly.to_csv(CHARTS_DIR / "corridor_monthly_calls.csv", index=False)
    log(f"Corridor monthly calls: {len(monthly)} months, {monthly['non_traffic_count'].sum():,} total non-traffic calls")

    # Opening events — sorted by date, for chart annotations
    opening_rows = []
    for i, s in enumerate(sorted(sites, key=lambda x: x["opening_date"]), 1):
        opening_rows.append({
            "site_id": s["id"],
            "address": s["address"],
            "opening_date": s["opening_date"],
            "sequence": i,
        })
    pd.DataFrame(opening_rows).to_csv(CHARTS_DIR / "corridor_opening_events.csv", index=False)
    log("Wrote corridor_opening_events.csv")

    return monthly


if __name__ == "__main__":
    main()
