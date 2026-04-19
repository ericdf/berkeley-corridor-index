"""Compute citywide 100m-grid benchmark for non-traffic call concentration.

Generates a regular 100m grid across Berkeley, counts non-traffic calls
within 100m of each grid point, and ranks the study sites against the
citywide (and optionally flats-only) distribution.

Outputs:
  data/processed/charts/citywide_benchmark_points.csv   — grid point metrics
  data/processed/charts/site_percentiles.csv            — site rankings
  data/processed/maps/citywide_benchmark_points.geojson — for Leaflet map
"""

import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint, Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, MAPS_DIR, ROOT, ensure_dirs, load_sites, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 100
GRID_SPACING_M = 100
REFERENCE_DIR = ROOT / "data" / "reference"


def build_berkeley_boundary() -> "shapely.geometry.base.BaseGeometry":
    """Union of council district polygons = Berkeley city boundary."""
    districts = gpd.read_file(MAPS_DIR / "council_districts_simplified.geojson").to_crs(CRS_PROJ)
    return unary_union(districts.geometry)


def build_grid(boundary_proj) -> gpd.GeoDataFrame:
    """Regular 100m grid points clipped to Berkeley boundary."""
    minx, miny, maxx, maxy = boundary_proj.bounds
    xs = np.arange(minx, maxx + GRID_SPACING_M, GRID_SPACING_M)
    ys = np.arange(miny, maxy + GRID_SPACING_M, GRID_SPACING_M)
    xx, yy = np.meshgrid(xs, ys)
    coords = list(zip(xx.ravel(), yy.ravel()))

    points = [Point(x, y) for x, y in coords]
    pts_gdf = gpd.GeoDataFrame(geometry=points, crs=CRS_PROJ)
    in_boundary = pts_gdf[pts_gdf.geometry.within(boundary_proj)].copy()
    in_boundary = in_boundary.reset_index(drop=True)
    in_boundary["grid_id"] = in_boundary.index
    log(f"Grid: {len(in_boundary):,} points within Berkeley boundary")
    return in_boundary


def count_calls_at_grid(
    grid_proj: gpd.GeoDataFrame,
    calls_proj: gpd.GeoDataFrame,
) -> pd.Series:
    """Count calls within BUFFER_M of each grid point using spatial join."""
    grid_buf = grid_proj.copy()
    grid_buf["geometry"] = grid_buf.geometry.buffer(BUFFER_M)
    joined = gpd.sjoin(calls_proj, grid_buf, how="left", predicate="within")
    counts = joined.groupby("index_right").size()
    return grid_proj.index.map(counts).fillna(0).astype(int)


def site_call_count(calls_proj: gpd.GeoDataFrame, site: dict) -> int:
    pt = gpd.GeoDataFrame(geometry=[Point(site["lon"], site["lat"])], crs=CRS_GEO).to_crs(CRS_PROJ)
    zone = pt.geometry.buffer(BUFFER_M).iloc[0]
    return int(calls_proj[calls_proj.geometry.within(zone)].shape[0])


def percentile_of(value: float, distribution: np.ndarray) -> float:
    """Return percentile rank (0–100) of value in distribution."""
    return round(float((distribution < value).sum() / len(distribution) * 100), 1)


def main() -> None:
    ensure_dirs()
    sites = load_sites()

    # Load non-traffic calls with coordinates
    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()
    calls_proj = gpd.GeoDataFrame(
        df_nt, geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)
    log(f"Non-traffic calls with coords: {len(calls_proj):,}")

    # Berkeley boundary
    berkeley_boundary = build_berkeley_boundary()

    # Grid
    grid = build_grid(berkeley_boundary)

    # Count calls at each grid point
    log("Counting calls within 100m of each grid point…")
    grid["call_count_100m"] = count_calls_at_grid(grid, calls_proj)

    # Flats layer (optional — skip gracefully if absent)
    flats_path = REFERENCE_DIR / "berkeley_flats.geojson"
    if flats_path.exists():
        flats = gpd.read_file(flats_path).to_crs(CRS_PROJ)
        flats_poly = unary_union(flats.geometry)
        grid["in_flats"] = grid.geometry.within(flats_poly)
        flats_n = grid["in_flats"].sum()
        log(f"Flats boundary loaded: {flats_n:,} of {len(grid):,} grid points in flatlands")
    else:
        grid["in_flats"] = False
        log("berkeley_flats.geojson not found — flats percentile will be null")

    # Citywide percentile for each grid point
    citywide_dist = grid["call_count_100m"].values
    grid["percentile_citywide"] = [percentile_of(v, citywide_dist) for v in citywide_dist]

    # Flats-only percentile
    flats_mask = grid["in_flats"]
    if flats_mask.any():
        flats_dist = grid.loc[flats_mask, "call_count_100m"].values
        grid.loc[flats_mask, "percentile_flats"] = [
            percentile_of(v, flats_dist) for v in grid.loc[flats_mask, "call_count_100m"]
        ]
    grid["percentile_flats"] = grid.get("percentile_flats", pd.Series(np.nan, index=grid.index))
    if "percentile_flats" not in grid.columns:
        grid["percentile_flats"] = np.nan

    # Export grid CSV (lon/lat in WGS84)
    grid_geo = grid.to_crs(CRS_GEO)
    grid_geo["lon"] = grid_geo.geometry.x.round(6)
    grid_geo["lat"] = grid_geo.geometry.y.round(6)
    grid_csv = grid_geo[["grid_id", "lon", "lat", "call_count_100m",
                           "percentile_citywide", "percentile_flats", "in_flats"]].copy()
    grid_csv.to_csv(CHARTS_DIR / "citywide_benchmark_points.csv", index=False)
    log(f"Wrote citywide_benchmark_points.csv ({len(grid_csv):,} rows)")

    # Export grid GeoJSON (points only, lightweight)
    grid_geo_out = grid_geo[["grid_id", "call_count_100m", "percentile_citywide",
                               "percentile_flats", "in_flats", "geometry"]].copy()
    grid_geo_out.to_file(MAPS_DIR / "citywide_benchmark_points.geojson", driver="GeoJSON")
    log("Wrote citywide_benchmark_points.geojson")

    # Site percentiles
    site_rows = []
    for s in sites:
        count = site_call_count(calls_proj, s)
        pct_city = percentile_of(count, citywide_dist)
        if flats_mask.any() and s.get("geography_group") in ("university_core", "san_pablo_node"):
            pct_flats = percentile_of(count, flats_dist)
        else:
            pct_flats = None
        site_rows.append({
            "site_id": s["id"],
            "address": s["address"],
            "label": s["label"],
            "geography_group": s.get("geography_group", ""),
            "call_count_100m": count,
            "percentile_citywide": pct_city,
            "percentile_flats": pct_flats,
        })
        log(f"{s['address']}: {count} calls → citywide {pct_city}th pct"
            + (f", flats {pct_flats}th pct" if pct_flats is not None else ""))

    pd.DataFrame(site_rows).to_csv(CHARTS_DIR / "site_percentiles.csv", index=False)
    log("Wrote site_percentiles.csv")

    # Summary stats for operator
    log(f"Citywide distribution — median: {np.median(citywide_dist):.0f}, "
        f"90th pct: {np.percentile(citywide_dist, 90):.0f}, "
        f"max: {citywide_dist.max()}")


if __name__ == "__main__":
    main()
