"""Build the combined all-sites corridor polygon (appendix / reference only).

Convex hull of all four study sites buffered by combined_corridor.buffer_m.
Not used as a primary analysis geography — kept for methodology reference.
"""

import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import MAPS_DIR, ensure_dirs, load_sites, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> gpd.GeoDataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    cfg = params["combined_corridor"]
    buffer_m = cfg["buffer_m"]

    points = [Point(s["lon"], s["lat"]) for s in sites]
    pts_gdf = gpd.GeoDataFrame(geometry=points, crs=CRS_GEO).to_crs(CRS_PROJ)

    hull = unary_union(pts_gdf.geometry).convex_hull
    poly = hull.buffer(buffer_m)

    gdf = gpd.GeoDataFrame(
        [{"label": cfg["label"], "buffer_m": buffer_m,
          "site_count": len(sites), "geometry": poly}],
        crs=CRS_PROJ,
    ).to_crs(CRS_GEO)

    gdf.to_file(MAPS_DIR / "combined_all_sites.geojson", driver="GeoJSON")
    log(f"Combined corridor written ({buffer_m}m buffer around all {len(sites)}-site hull)")
    return gdf


if __name__ == "__main__":
    main()
