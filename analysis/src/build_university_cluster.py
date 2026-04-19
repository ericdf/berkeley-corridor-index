"""Build the University Avenue core cluster polygon.

Convex hull of the three University Ave sites buffered by university_core.buffer_m.
This is the primary treatment geography for the University cluster analysis.
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
    cfg = params["university_core"]
    buffer_m = cfg["buffer_m"]

    core_sites = [s for s in sites if s.get("geography_group") == "university_core"]
    points = [Point(s["lon"], s["lat"]) for s in core_sites]
    pts_gdf = gpd.GeoDataFrame(geometry=points, crs=CRS_GEO).to_crs(CRS_PROJ)

    hull = unary_union(pts_gdf.geometry).convex_hull
    poly = hull.buffer(buffer_m)

    gdf = gpd.GeoDataFrame(
        [{"label": cfg["label"], "buffer_m": buffer_m,
          "site_count": len(core_sites), "geometry": poly}],
        crs=CRS_PROJ,
    ).to_crs(CRS_GEO)

    gdf.to_file(MAPS_DIR / "university_core_cluster.geojson", driver="GeoJSON")
    log(f"University core cluster written ({buffer_m}m buffer around {len(core_sites)}-site hull)")
    return gdf


if __name__ == "__main__":
    main()
