"""Rank study sites against the distribution of individual 100m grid points
on specific comparison corridors.

For each comparison corridor, identifies all citywide benchmark grid points
within 75m of that corridor, then ranks each study site's call count within
that corridor's point distribution — both all-period and pre-period.

This answers: "Among every 100m zone on South Telegraph / College Ave / etc.,
where do the study sites rank?"

Outputs:
  data/processed/charts/corridor_point_rankings.csv   (long: one row per site × corridor)
  data/processed/charts/corridor_point_rankings_wide.csv  (wide: sites as columns)
"""

import sys
import textwrap
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import LineString

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ROOT, ensure_dirs, log

CRS_GEO  = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 75
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_HEADERS = {"User-Agent": "motel_conversions_analysis/1.0 (research project)"}
TIMEOUT_S = 30

# Corridors: (label, osm_name, bbox_dict)
# bbox: lat_min, lat_max, lon_min, lon_max
CORRIDORS = [
    ("South Telegraph",       "Telegraph Avenue",  dict(lat_min=37.844, lat_max=37.868, lon_min=-122.262, lon_max=-122.257)),
    ("Shattuck (south)",      "Shattuck Avenue",   dict(lat_min=37.857, lat_max=37.870, lon_min=-122.270, lon_max=-122.267)),
    ("Adeline (south)",       "Adeline Street",    dict(lat_min=37.846, lat_max=37.870, lon_min=-122.271, lon_max=-122.267)),
    ("Ashby Avenue",          "Ashby Avenue",      dict(lat_min=37.854, lat_max=37.860, lon_min=-122.290, lon_max=-122.245)),
    ("College Ave (Elmwood)", "College Avenue",    dict(lat_min=37.854, lat_max=37.862, lon_min=-122.254, lon_max=-122.247)),
    ("Fourth Street",         "Fourth Street",     dict(lat_min=37.867, lat_max=37.883, lon_min=-122.306, lon_max=-122.297)),
    ("Solano Avenue",         "Solano Avenue",     dict(lat_min=37.887, lat_max=37.893, lon_min=-122.308, lon_max=-122.272)),
]

REFERENCE_DIR = ROOT / "data" / "reference"


def fetch_corridor_poly(osm_name: str, bbox: dict):
    """Fetch OSM way geometries and return a projected buffer polygon."""
    s, w, n, e = bbox["lat_min"], bbox["lon_min"], bbox["lat_max"], bbox["lon_max"]
    query = textwrap.dedent(f"""
        [out:json][timeout:{TIMEOUT_S}];
        way["name"~"{osm_name}",i]({s},{w},{n},{e});
        (._;>;);
        out body;
    """).strip()
    try:
        resp = requests.get(OVERPASS_URL, params={"data": query},
                            headers=OVERPASS_HEADERS, timeout=TIMEOUT_S + 5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"  Overpass failed for {osm_name!r}: {e}")
        return None

    nodes = {el["id"]: (el["lon"], el["lat"])
             for el in data["elements"] if el["type"] == "node"}
    ways  = [el for el in data["elements"] if el["type"] == "way"]
    lines = []
    for way in ways:
        coords = [nodes[nid] for nid in way["nodes"] if nid in nodes]
        if len(coords) >= 2:
            lines.append(LineString(coords))
    if not lines:
        log(f"  No valid geometries for {osm_name!r}")
        return None

    gdf = gpd.GeoDataFrame({"geometry": lines}, crs=CRS_GEO).to_crs(CRS_PROJ)
    poly = gdf.geometry.union_all().buffer(BUFFER_M)
    log(f"  {len(lines)} ways → corridor polygon")
    return poly


def percentile_of(value, distribution):
    return float(np.mean(distribution <= value) * 100)


def main() -> None:
    ensure_dirs()

    # Load benchmark grid
    grid = pd.read_csv(CHARTS_DIR / "citywide_benchmark_points.csv")
    grid_gdf = gpd.GeoDataFrame(
        grid,
        geometry=gpd.points_from_xy(grid["lon"], grid["lat"]),
        crs=CRS_GEO,
    ).to_crs(CRS_PROJ)

    # Load study sites
    sites = pd.read_csv(CHARTS_DIR / "site_percentiles.csv")

    rows = []

    for label, osm_name, bbox in CORRIDORS:
        log(f"\n{label}")
        poly = fetch_corridor_poly(osm_name, bbox)
        if poly is None:
            continue

        # Filter grid points within this corridor
        in_corridor = grid_gdf.geometry.within(poly)
        corridor_pts = grid_gdf[in_corridor]
        n_pts = len(corridor_pts)
        log(f"  {n_pts} grid points within corridor buffer")
        if n_pts < 5:
            log(f"  Too few points — skipping")
            continue

        all_counts = corridor_pts["call_count_100m"].values
        pre_counts = corridor_pts["pre_count_100m"].values

        log(f"  All-period: median={np.median(all_counts):.0f}, "
            f"90th={np.percentile(all_counts, 90):.0f}, max={all_counts.max():.0f}")

        for _, site in sites.iterrows():
            pct_all = percentile_of(site["call_count_100m"], all_counts)
            pct_pre = percentile_of(site["pre_count_100m"], pre_counts)
            rows.append({
                "site_id":          site["site_id"],
                "label":            site["label"],
                "corridor":         label,
                "n_corridor_pts":   n_pts,
                "site_count_all":   site["call_count_100m"],
                "site_count_pre":   site["pre_count_100m"],
                "percentile_all":   round(pct_all, 1),
                "percentile_pre":   round(pct_pre, 1),
                "corridor_median":  round(float(np.median(all_counts)), 1),
                "corridor_p90":     round(float(np.percentile(all_counts, 90)), 1),
                "corridor_max":     round(float(all_counts.max()), 1),
            })

    result = pd.DataFrame(rows)
    out_long = CHARTS_DIR / "corridor_point_rankings.csv"
    result.to_csv(out_long, index=False)
    log(f"\nWrote {len(result)} rows → {out_long}")

    # Wide pivot: corridors as rows, sites as columns
    wide = result.pivot_table(
        index="corridor",
        columns="label",
        values="percentile_all",
        aggfunc="first",
    ).round(1)
    wide.index.name = "corridor"
    out_wide = CHARTS_DIR / "corridor_point_rankings_wide.csv"
    wide.to_csv(out_wide)
    log(f"Wrote wide table → {out_wide}")

    log("\n=== All-period percentile ranks (site vs. corridor point distribution) ===")
    log(wide.to_string())


if __name__ == "__main__":
    main()
