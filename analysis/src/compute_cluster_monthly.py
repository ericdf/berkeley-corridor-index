"""Compute monthly non-traffic call counts for each treatment geography.

Produces:
  university_cluster_monthly.csv   — University core cluster
  san_pablo_monthly.csv            — San Pablo node
  controls_monthly.csv             — North Shattuck and South Telegraph
  cluster_opening_events.csv       — opening markers for University core charts
  san_pablo_opening_events.csv     — opening markers for San Pablo charts
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, MAPS_DIR, ensure_dirs, load_sites, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def monthly_in_poly(calls_gdf: gpd.GeoDataFrame, poly) -> pd.DataFrame:
    subset = calls_gdf[calls_gdf.geometry.within(poly)].copy()
    subset["month"] = subset["event_date"].dt.to_period("M")
    monthly = subset.groupby("month").size().reset_index(name="non_traffic_count")
    monthly["date"] = monthly["month"].dt.to_timestamp()
    monthly["year"] = monthly["date"].dt.year
    monthly["month_num"] = monthly["date"].dt.month
    return monthly[["year", "month_num", "date", "non_traffic_count"]].sort_values("date")


def main() -> None:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    # University core cluster
    core_gdf = gpd.read_file(MAPS_DIR / "university_core_cluster.geojson").to_crs(CRS_PROJ)
    core_monthly = monthly_in_poly(calls_gdf, core_gdf.geometry.iloc[0])
    core_monthly.to_csv(CHARTS_DIR / "university_cluster_monthly.csv", index=False)
    log(f"University cluster: {len(core_monthly)} months, {core_monthly['non_traffic_count'].sum():,} non-traffic calls")

    # San Pablo node
    sp_gdf = gpd.read_file(MAPS_DIR / "san_pablo_node.geojson").to_crs(CRS_PROJ)
    sp_monthly = monthly_in_poly(calls_gdf, sp_gdf.geometry.iloc[0])
    sp_monthly.to_csv(CHARTS_DIR / "san_pablo_monthly.csv", index=False)
    log(f"San Pablo node: {len(sp_monthly)} months, {sp_monthly['non_traffic_count'].sum():,} non-traffic calls")

    # Control corridors
    corridors_cfg = params["control_corridors"]
    ctrl_rows = []
    for cid, cfg in corridors_cfg.items():
        pt = Point(cfg["center_lon"], cfg["center_lat"])
        poly = gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO).to_crs(CRS_PROJ).geometry.buffer(cfg["radius_m"]).iloc[0]
        monthly = monthly_in_poly(calls_gdf, poly)
        monthly["label"] = cfg["label"]
        monthly["series_id"] = cid
        ctrl_rows.append(monthly)
    ctrl_df = pd.concat(ctrl_rows, ignore_index=True).sort_values(["label", "date"])
    ctrl_df.to_csv(CHARTS_DIR / "controls_monthly.csv", index=False)
    log(f"Controls monthly: {len(ctrl_df)} rows")

    # Opening events — University core
    core_sites = sorted(
        [s for s in sites if s.get("geography_group") == "university_core"],
        key=lambda x: x["opening_date"],
    )
    core_events = [{"site_id": s["id"], "address": s["address"],
                    "opening_date": s["opening_date"], "sequence": i}
                   for i, s in enumerate(core_sites, 1)]
    pd.DataFrame(core_events).to_csv(CHARTS_DIR / "cluster_opening_events.csv", index=False)

    # Opening events — San Pablo
    sp_sites = sorted(
        [s for s in sites if s.get("geography_group") == "san_pablo_node"],
        key=lambda x: x["opening_date"],
    )
    sp_events = [{"site_id": s["id"], "address": s["address"],
                  "opening_date": s["opening_date"], "sequence": i}
                 for i, s in enumerate(sp_sites, 1)]
    pd.DataFrame(sp_events).to_csv(CHARTS_DIR / "san_pablo_opening_events.csv", index=False)

    log("Opening event CSVs written")


if __name__ == "__main__":
    main()
