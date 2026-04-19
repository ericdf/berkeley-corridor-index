"""Index treatment geographies and control corridors to a common baseline.

Baseline = average monthly calls before the first site opening in each group.
All series indexed to 100 at baseline.

Output: corridor_vs_controls_index.csv
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


def monthly_counts(calls_gdf: gpd.GeoDataFrame, poly) -> pd.Series:
    in_area = calls_gdf[calls_gdf.geometry.within(poly)].copy()
    in_area["month"] = in_area["event_date"].dt.to_period("M")
    return in_area.groupby("month").size().rename("count")


def index_series(calls_gdf, poly, label, series_id, baseline_cutoff) -> pd.DataFrame:
    monthly = monthly_counts(calls_gdf, poly)
    baseline_monthly = monthly_counts(calls_gdf[calls_gdf["event_date"] < baseline_cutoff], poly)
    baseline_avg = baseline_monthly.mean() if len(baseline_monthly) > 0 else 1

    df = monthly.reset_index()
    df.columns = ["month", "count"]
    df["date"] = df["month"].dt.to_timestamp()
    df["index_value"] = (df["count"] / baseline_avg * 100).round(1)
    df["series_id"] = series_id
    df["label"] = label
    return df[["series_id", "label", "date", "count", "index_value"]]


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    # Baseline = before the first opening overall
    first_opening = min(pd.Timestamp(s["opening_date"]) for s in sites)
    log(f"Baseline period: data start to {first_opening.date()}")

    all_series = []

    # University core cluster
    core_gdf = gpd.read_file(MAPS_DIR / "university_core_cluster.geojson").to_crs(CRS_PROJ)
    all_series.append(index_series(
        calls_gdf, core_gdf.geometry.iloc[0],
        params["university_core"]["label"], "university_core", first_opening,
    ))

    # San Pablo node
    sp_gdf = gpd.read_file(MAPS_DIR / "san_pablo_node.geojson").to_crs(CRS_PROJ)
    all_series.append(index_series(
        calls_gdf, sp_gdf.geometry.iloc[0],
        params["san_pablo_node"]["label"], "san_pablo_node", first_opening,
    ))

    # Control corridors
    for cid, cfg in params["control_corridors"].items():
        pt = Point(cfg["center_lon"], cfg["center_lat"])
        poly = gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO).to_crs(CRS_PROJ).geometry.buffer(cfg["radius_m"]).iloc[0]
        all_series.append(index_series(calls_gdf, poly, cfg["label"], cid, first_opening))

    result = pd.concat(all_series, ignore_index=True).sort_values(["label", "date"])
    result.to_csv(CHARTS_DIR / "corridor_vs_controls_index.csv", index=False)
    log(f"Wrote corridor_vs_controls_index.csv ({len(result)} rows)")
    return result


if __name__ == "__main__":
    main()
