"""Build geographic zone polygons for each study site.

Produces buffered polygons (site block, adjacent, wider) and exports GeoJSON.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    MAPS_DIR, RAW_CURRENT,
    ensure_dirs, load_sites, load_study_params, log, write_json,
)

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"  # UTM zone 10N — meters, appropriate for Berkeley


def make_zone_gdf(sites: list[dict], radius_m: float, zone_name: str) -> gpd.GeoDataFrame:
    records = []
    for site in sites:
        pt = Point(site["lon"], site["lat"])
        records.append({
            "site_id": site["id"],
            "address": site["address"],
            "zone": zone_name,
            "geometry": pt,
        })
    gdf = gpd.GeoDataFrame(records, crs=CRS_GEO)
    gdf = gdf.to_crs(CRS_PROJ)
    gdf["geometry"] = gdf["geometry"].buffer(radius_m)
    return gdf.to_crs(CRS_GEO)


def make_sites_gdf(sites: list[dict]) -> gpd.GeoDataFrame:
    records = []
    for site in sites:
        records.append({
            "site_id": site["id"],
            "address": site["address"],
            "label": site["label"],
            "opening_date": site["opening_date"],
            "program_type": site["program_type"],
            "geometry": Point(site["lon"], site["lat"]),
        })
    return gpd.GeoDataFrame(records, crs=CRS_GEO)


def main() -> dict[str, gpd.GeoDataFrame]:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    z = params["zones"]

    site_block_gdf = make_zone_gdf(sites, z["site_block_m"], "site_block")
    adjacent_gdf = make_zone_gdf(sites, z["adjacent_blocks_m"], "adjacent_blocks")
    wider_gdf = make_zone_gdf(sites, z["wider_nearby_m"], "wider_nearby")
    sites_gdf = make_sites_gdf(sites)

    # Subtract inner zones to get annular rings for cleaner zone assignment
    site_block_proj = site_block_gdf.to_crs(CRS_PROJ)
    adjacent_proj = make_zone_gdf(sites, z["adjacent_blocks_m"], "adjacent_blocks").to_crs(CRS_PROJ)
    wider_proj = make_zone_gdf(sites, z["wider_nearby_m"], "wider_nearby").to_crs(CRS_PROJ)

    adj_ring = adjacent_proj.copy()
    adj_ring["geometry"] = [
        a.difference(b)
        for a, b in zip(adjacent_proj.geometry, site_block_proj.geometry)
    ]
    wide_ring = wider_proj.copy()
    wide_ring["geometry"] = [
        a.difference(b)
        for a, b in zip(wider_proj.geometry, adjacent_proj.geometry)
    ]

    site_block_gdf.to_file(MAPS_DIR / "site_block_zones.geojson", driver="GeoJSON")
    adj_ring.to_crs(CRS_GEO).to_file(MAPS_DIR / "adjacent_block_zones.geojson", driver="GeoJSON")
    wide_ring.to_crs(CRS_GEO).to_file(MAPS_DIR / "wider_nearby_zones.geojson", driver="GeoJSON")
    sites_gdf.to_file(MAPS_DIR / "sites.geojson", driver="GeoJSON")

    # Simplified council districts passthrough (if available)
    district_src = RAW_CURRENT / "council_districts.geojson"
    if district_src.exists():
        gdf_d = gpd.read_file(district_src).to_crs(CRS_GEO)
        gdf_d["geometry"] = gdf_d["geometry"].simplify(0.0001)
        gdf_d.to_file(MAPS_DIR / "council_districts_simplified.geojson", driver="GeoJSON")
        log("Wrote council_districts_simplified.geojson")
    else:
        log("Council districts raw file not found — skipping")

    log(f"Zone GeoJSON written to {MAPS_DIR}")
    return {
        "site_block": site_block_gdf,
        "adjacent": adj_ring.to_crs(CRS_GEO),
        "wider": wide_ring.to_crs(CRS_GEO),
        "sites": sites_gdf,
    }


if __name__ == "__main__":
    main()
