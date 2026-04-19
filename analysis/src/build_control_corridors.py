"""Build control corridor polygons for North Shattuck and South Telegraph."""

import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import MAPS_DIR, ensure_dirs, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> gpd.GeoDataFrame:
    ensure_dirs()
    params = load_study_params()
    corridors = params["control_corridors"]

    rows = []
    for cid, cfg in corridors.items():
        pt = Point(cfg["center_lon"], cfg["center_lat"])
        rows.append({"corridor_id": cid, "label": cfg["label"], "geometry": pt})

    gdf = gpd.GeoDataFrame(rows, crs=CRS_GEO).to_crs(CRS_PROJ)
    gdf["geometry"] = [
        row.geometry.buffer(corridors[row.corridor_id]["radius_m"])
        for _, row in gdf.iterrows()
    ]
    gdf = gdf.to_crs(CRS_GEO)
    gdf.to_file(MAPS_DIR / "control_corridors.geojson", driver="GeoJSON")
    log(f"Control corridors written: {list(corridors.keys())}")
    return gdf


if __name__ == "__main__":
    main()
