"""Compute citywide 100m-grid benchmark for non-traffic call concentration.

Generates a regular 100m grid across Berkeley, counts non-traffic calls
within 100m of each grid point, and ranks the study sites against the
citywide (and optionally flats-only) distribution.

Computes both all-period and pre-opening-only rankings so the benchmark
page can show whether sites were already high-activity before conversion.

Outputs:
  data/processed/charts/citywide_benchmark_points.csv   — grid point metrics
  data/processed/charts/site_percentiles.csv            — site rankings (all-period + pre-opening)
  data/processed/maps/citywide_benchmark_points.geojson — for Leaflet map
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, MAPS_DIR, ROOT, ensure_dirs, load_sites, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 100
GRID_SPACING_M = 100
REFERENCE_DIR = ROOT / "data" / "reference"


def build_berkeley_boundary():
    districts = gpd.read_file(MAPS_DIR / "council_districts_simplified.geojson").to_crs(CRS_PROJ)
    return unary_union(districts.geometry)


def build_grid(boundary_proj) -> gpd.GeoDataFrame:
    minx, miny, maxx, maxy = boundary_proj.bounds
    xs = np.arange(minx, maxx + GRID_SPACING_M, GRID_SPACING_M)
    ys = np.arange(miny, maxy + GRID_SPACING_M, GRID_SPACING_M)
    xx, yy = np.meshgrid(xs, ys)
    pts = [Point(x, y) for x, y in zip(xx.ravel(), yy.ravel())]
    gdf = gpd.GeoDataFrame(geometry=pts, crs=CRS_PROJ)
    gdf = gdf[gdf.geometry.within(boundary_proj)].reset_index(drop=True)
    gdf["grid_id"] = gdf.index
    log(f"Grid: {len(gdf):,} points within Berkeley boundary")
    return gdf


def count_calls_at_grid(grid: gpd.GeoDataFrame, calls: gpd.GeoDataFrame) -> pd.Series:
    grid_buf = grid.copy()
    grid_buf["geometry"] = grid_buf.geometry.buffer(BUFFER_M)
    joined = gpd.sjoin(calls, grid_buf, how="left", predicate="within")
    counts = joined.groupby("index_right").size()
    return grid.index.map(counts).fillna(0).astype(int)


def site_count(calls: gpd.GeoDataFrame, site: dict) -> int:
    pt = gpd.GeoDataFrame(geometry=[Point(site["lon"], site["lat"])], crs=CRS_GEO).to_crs(CRS_PROJ)
    zone = pt.geometry.buffer(BUFFER_M).iloc[0]
    return int(calls[calls.geometry.within(zone)].shape[0])


def percentile_of(value: float, dist: np.ndarray) -> float:
    return round(float((dist < value).sum() / len(dist) * 100), 1)


def main() -> None:
    ensure_dirs()
    sites = load_sites()

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()

    calls_all = gpd.GeoDataFrame(
        df_nt, geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)
    log(f"Non-traffic calls with coords: {len(calls_all):,}")

    # First site opening = start of post period for benchmark
    first_opening = min(pd.Timestamp(s["opening_date"]) for s in sites)
    data_start = df_nt["event_date"].min()
    data_end = df_nt["event_date"].max()
    pre_months = (first_opening - data_start).days / 30.44
    post_months = (data_end - first_opening).days / 30.44

    calls_pre = calls_all[calls_all["event_date"] < first_opening]
    log(f"Pre-opening calls: {len(calls_pre):,} over {pre_months:.1f} months (before {first_opening.date()})")

    boundary = build_berkeley_boundary()
    grid = build_grid(boundary)

    # All-period counts (used for map coloring)
    log("Counting all-period calls at grid points…")
    grid["call_count_100m"] = count_calls_at_grid(grid, calls_all)

    # Pre-opening counts (normalized to rate for fair comparison with all-period)
    log("Counting pre-opening calls at grid points…")
    grid["pre_count_100m"] = count_calls_at_grid(grid, calls_pre)
    # Annualize pre counts to the same total period length for a fair rank comparison
    full_months = (data_end - data_start).days / 30.44
    grid["pre_count_annualized"] = (grid["pre_count_100m"] / pre_months * full_months).round(1)

    # Flats layer
    flats_path = REFERENCE_DIR / "berkeley_flats.geojson"
    if flats_path.exists():
        flats_poly = unary_union(gpd.read_file(flats_path).to_crs(CRS_PROJ).geometry)
        grid["in_flats"] = grid.geometry.within(flats_poly)
        log(f"Flats: {grid['in_flats'].sum():,} of {len(grid):,} grid points")
    else:
        grid["in_flats"] = False
        log("berkeley_flats.geojson absent — flats percentile skipped")

    # Percentiles against all-period distribution
    all_dist = grid["call_count_100m"].values
    grid["percentile_citywide"] = [percentile_of(v, all_dist) for v in all_dist]

    flats_mask = grid["in_flats"]
    flats_dist = grid.loc[flats_mask, "call_count_100m"].values if flats_mask.any() else None
    grid["percentile_flats"] = np.nan
    if flats_dist is not None:
        grid.loc[flats_mask, "percentile_flats"] = [
            percentile_of(v, flats_dist) for v in grid.loc[flats_mask, "call_count_100m"]
        ]

    # Pre-opening percentiles (rank pre-annualized against same annualized pre distribution)
    pre_ann_dist = grid["pre_count_annualized"].values
    grid["percentile_citywide_pre"] = [percentile_of(v, pre_ann_dist) for v in pre_ann_dist]

    # Export grid CSV + GeoJSON
    grid_geo = grid.to_crs(CRS_GEO)
    grid_geo["lon"] = grid_geo.geometry.x.round(6)
    grid_geo["lat"] = grid_geo.geometry.y.round(6)
    grid_geo[["grid_id", "lon", "lat", "call_count_100m", "pre_count_100m",
               "percentile_citywide", "percentile_citywide_pre", "percentile_flats",
               "in_flats"]].to_csv(CHARTS_DIR / "citywide_benchmark_points.csv", index=False)
    log(f"Wrote citywide_benchmark_points.csv ({len(grid_geo):,} rows)")

    grid_geo[["grid_id", "call_count_100m", "percentile_citywide",
               "percentile_citywide_pre", "in_flats", "geometry"]].to_file(
        MAPS_DIR / "citywide_benchmark_points.geojson", driver="GeoJSON"
    )
    log("Wrote citywide_benchmark_points.geojson")

    # Site percentiles — all-period and pre-opening
    site_rows = []
    for s in sites:
        count_all = site_count(calls_all, s)
        count_pre = site_count(calls_pre, s)
        count_pre_ann = round(count_pre / pre_months * full_months, 1)
        pre_rate = round(count_pre / pre_months, 1)
        post_count = count_all - count_pre
        post_rate = round(post_count / post_months, 1)

        pct_all = percentile_of(count_all, all_dist)
        pct_pre = percentile_of(count_pre_ann, pre_ann_dist)
        pct_flats = percentile_of(count_all, flats_dist) if flats_dist is not None else None

        site_rows.append({
            "site_id": s["id"],
            "address": s["address"],
            "label": s["label"],
            "geography_group": s.get("geography_group", ""),
            "opening_date": s["opening_date"],
            # All-period (full dataset)
            "call_count_100m": count_all,
            "percentile_citywide": pct_all,
            "percentile_flats": pct_flats,
            # Pre-opening
            "pre_count_100m": count_pre,
            "pre_rate_per_month": pre_rate,
            "pre_percentile_citywide": pct_pre,
            # Post-opening rate
            "post_count_100m": post_count,
            "post_rate_per_month": post_rate,
            "rate_change_pct": round((post_rate - pre_rate) / pre_rate * 100, 1) if pre_rate > 0 else None,
        })
        log(f"{s['address']}: pre {pre_rate}/mo ({pct_pre}th pct) → post {post_rate}/mo ({pct_all}th pct all-period)")

    pd.DataFrame(site_rows).to_csv(CHARTS_DIR / "site_percentiles.csv", index=False)
    log("Wrote site_percentiles.csv")

    log(f"All-period distribution — median: {np.median(all_dist):.0f}, "
        f"90th pct: {np.percentile(all_dist, 90):.0f}, max: {all_dist.max()}")


if __name__ == "__main__":
    main()
