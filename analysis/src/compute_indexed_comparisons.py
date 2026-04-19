"""Index corridor and control corridors to a common baseline for comparison.

Baseline = average monthly calls in the period before the first site opening.
All series indexed to 100 at baseline. Output: corridor_vs_controls_index.csv.
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


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    corridors_cfg = params["control_corridors"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    # Baseline: before the earliest site opening
    first_opening = min(pd.Timestamp(s["opening_date"]) for s in sites)
    baseline_calls = calls_gdf[calls_gdf["event_date"] < first_opening]
    log(f"Baseline period: data start to {first_opening.date()} ({len(baseline_calls):,} non-traffic calls)")

    corridor_gdf = gpd.read_file(MAPS_DIR / "university_corridor_cluster.geojson").to_crs(CRS_PROJ)
    corridor_poly = corridor_gdf.geometry.iloc[0]

    series_map = {"University Ave corridor": (corridor_poly, "corridor")}
    for cid, cfg in corridors_cfg.items():
        pt = Point(cfg["center_lon"], cfg["center_lat"])
        poly = gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO).to_crs(CRS_PROJ).geometry.buffer(cfg["radius_m"]).iloc[0]
        series_map[cfg["label"]] = (poly, cid)

    all_series = []
    for label, (poly, series_id) in series_map.items():
        monthly = monthly_counts(calls_gdf, poly)
        baseline_monthly = monthly_counts(baseline_calls, poly)
        baseline_avg = baseline_monthly.mean() if len(baseline_monthly) > 0 else 1

        df_series = monthly.reset_index()
        df_series.columns = ["month", "count"]
        df_series["date"] = df_series["month"].dt.to_timestamp()
        df_series["index_value"] = (df_series["count"] / baseline_avg * 100).round(1)
        df_series["series_id"] = series_id
        df_series["label"] = label
        all_series.append(df_series[["series_id", "label", "date", "count", "index_value"]])

    result = pd.concat(all_series, ignore_index=True).sort_values(["label", "date"])
    result.to_csv(CHARTS_DIR / "corridor_vs_controls_index.csv", index=False)
    log(f"Wrote corridor_vs_controls_index.csv ({len(result)} rows, baseline avg before {first_opening.date()})")
    return result


if __name__ == "__main__":
    main()
