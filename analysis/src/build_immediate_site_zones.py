"""Build immediate site zones — small per-property buffers for descriptive use only.

These are secondary to the corridor-level analysis.
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
    radius_m = params["immediate_zone_m"]

    rows = []
    for s in sites:
        pt = Point(s["lon"], s["lat"])
        rows.append({
            "site_id": s["id"],
            "address": s["address"],
            "opening_date": s["opening_date"],
            "geometry": pt,
        })

    gdf = gpd.GeoDataFrame(rows, crs=CRS_GEO).to_crs(CRS_PROJ)
    gdf["geometry"] = gdf.geometry.buffer(radius_m)
    gdf = gdf.to_crs(CRS_GEO)
    gdf.to_file(MAPS_DIR / "immediate_site_zones.geojson", driver="GeoJSON")
    log(f"Immediate site zones written ({radius_m}m buffer per site)")
    return gdf


if __name__ == "__main__":
    main()
