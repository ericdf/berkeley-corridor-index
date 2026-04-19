"""Build the University Avenue corridor cluster polygon.

Corridor is defined as the convex hull of all study site points,
buffered by corridor_buffer_m. This is the primary treatment geography.
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
    buffer_m = params["corridor"]["buffer_m"]

    points = [Point(s["lon"], s["lat"]) for s in sites]
    pts_gdf = gpd.GeoDataFrame(geometry=points, crs=CRS_GEO).to_crs(CRS_PROJ)

    hull = unary_union(pts_gdf.geometry).convex_hull
    corridor_poly = hull.buffer(buffer_m)

    corridor_gdf = gpd.GeoDataFrame(
        [{"label": params["corridor"]["label"], "buffer_m": buffer_m,
          "site_count": len(sites), "geometry": corridor_poly}],
        crs=CRS_PROJ,
    ).to_crs(CRS_GEO)

    corridor_gdf.to_file(MAPS_DIR / "university_corridor_cluster.geojson", driver="GeoJSON")
    log(f"Corridor polygon written ({buffer_m}m buffer around {len(sites)}-site convex hull)")
    return corridor_gdf


if __name__ == "__main__":
    main()
