"""Build the San Pablo node polygon.

Single-site geography: 1620 San Pablo Ave buffered by san_pablo_node.buffer_m.
Analyzed independently because it sits ~440m northwest of the University cluster
and including it in a combined hull pulls in low-activity intervening blocks.
"""

import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import MAPS_DIR, ensure_dirs, load_sites, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> gpd.GeoDataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    cfg = params["san_pablo_node"]
    buffer_m = cfg["buffer_m"]

    node_sites = [s for s in sites if s.get("geography_group") == "san_pablo_node"]

    polys = []
    for s in node_sites:
        pt = gpd.GeoDataFrame(geometry=[Point(s["lon"], s["lat"])], crs=CRS_GEO).to_crs(CRS_PROJ)
        polys.append({"label": cfg["label"], "buffer_m": buffer_m,
                      "site_id": s["id"], "geometry": pt.geometry.buffer(buffer_m).iloc[0]})

    gdf = gpd.GeoDataFrame(polys, crs=CRS_PROJ).to_crs(CRS_GEO)
    gdf.to_file(MAPS_DIR / "san_pablo_node.geojson", driver="GeoJSON")
    log(f"San Pablo node written ({buffer_m}m buffer around {len(node_sites)} site)")
    return gdf


if __name__ == "__main__":
    main()
