"""Compute call trajectory for clean retail comparison corridors.

Three corridors with no shelter facilities, selected as positive baselines
for what a commercial corridor looks like without shelter pressure:
  - Fourth Street (north of University Ave, retail district)
  - College Avenue / Elmwood (~4 blocks each side of Ashby Ave)
  - Solano Avenue (The Alameda to Albany border)

Fetches OSM street geometries via Overpass API (filtered by bbox + name),
buffers 75 m, counts non-traffic calls per month, and computes a trajectory
index matching corridor_rankings.csv format.

Outputs:
  data/processed/charts/clean_retail_corridors.csv
"""

import sys
import textwrap
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import LineString
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ROOT, ensure_dirs, log

CONFIG_PATH = ROOT / "analysis" / "config" / "clean_retail_corridors.yml"
CRS_GEO  = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 75
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT_S = 30


def fetch_osm_ways(street_name: str, bbox: dict) -> gpd.GeoDataFrame | None:
    """Fetch OSM way geometries matching street_name within bbox via Overpass."""
    s, w, n, e = bbox["lat_min"], bbox["lon_min"], bbox["lat_max"], bbox["lon_max"]
    # Query ways whose name matches, within the bounding box
    query = textwrap.dedent(f"""
        [out:json][timeout:{TIMEOUT_S}];
        way["name"~"{street_name}",i]({s},{w},{n},{e});
        (._;>;);
        out body;
    """).strip()

    headers = {"User-Agent": "motel_conversions_analysis/1.0 (research project)"}
    try:
        resp = requests.get(
            OVERPASS_URL,
            params={"data": query},
            headers=headers,
            timeout=TIMEOUT_S + 5,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"  Overpass request failed: {e}")
        return None

    elements = data.get("elements", [])
    nodes = {el["id"]: (el["lon"], el["lat"]) for el in elements if el["type"] == "node"}
    ways  = [el for el in elements if el["type"] == "way"]

    if not ways:
        log(f"  No OSM ways found for {street_name!r}")
        return None

    lines = []
    for way in ways:
        coords = [nodes[nid] for nid in way["nodes"] if nid in nodes]
        if len(coords) >= 2:
            lines.append(LineString(coords))

    if not lines:
        log(f"  Ways found but no valid geometries for {street_name!r}")
        return None

    log(f"  {len(lines)} OSM way segments for {street_name!r}")
    return gpd.GeoDataFrame({"geometry": lines}, crs=CRS_GEO)


def main() -> None:
    import yaml
    ensure_dirs()

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    corridors_cfg = config["clean_retail_corridors"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()
    df_nt["year"]  = df_nt["event_date"].dt.year
    df_nt["month"] = df_nt["event_date"].dt.month

    calls = gpd.GeoDataFrame(
        df_nt,
        geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]),
        crs=CRS_GEO,
    ).to_crs(CRS_PROJ)

    rows = []

    for cfg in corridors_cfg:
        label       = cfg["label"]
        street_name = cfg["street_name"]
        bbox        = cfg["bbox"]

        log(f"\nProcessing: {label}")

        edges = fetch_osm_ways(street_name, bbox)
        if edges is None:
            continue

        corridor_geom = edges.to_crs(CRS_PROJ).geometry.unary_union.buffer(BUFFER_M)
        corridor_gdf  = gpd.GeoDataFrame(
            {"corridor": [label]},
            geometry=[corridor_geom],
            crs=CRS_PROJ,
        )

        joined = gpd.sjoin(calls, corridor_gdf, how="inner", predicate="within")

        monthly = (
            joined.groupby(["year", "month"])
            .size()
            .reset_index(name="count")
        )

        y2021 = monthly[monthly["year"] == 2021]["count"]
        y2025 = monthly[monthly["year"] == 2025]["count"]

        annual_2021 = int(y2021.sum())
        avg_2021    = float(y2021.mean()) if len(y2021) > 0 else None
        avg_2025    = float(y2025.mean()) if len(y2025) >= 6 else None

        trajectory = round(avg_2025 / avg_2021 * 100, 1) if (avg_2021 and avg_2025) else None

        log(f"  2021 annual calls: {annual_2021}")
        if avg_2021: log(f"  avg monthly 2021: {avg_2021:.1f}")
        if avg_2025: log(f"  avg monthly 2025: {avg_2025:.1f}")
        if trajectory: log(f"  trajectory index: {trajectory}")

        for _, r in monthly.iterrows():
            rows.append({
                "corridor_id":       cfg["id"],
                "corridor":          label,
                "year":              int(r["year"]),
                "month":             int(r["month"]),
                "count":             int(r["count"]),
                "avg_monthly_2021":  round(avg_2021, 1) if avg_2021 else None,
                "avg_monthly_2025":  round(avg_2025, 1) if avg_2025 else None,
                "trajectory_index":  trajectory,
                "annual_calls_2021": annual_2021,
                "is_clean_retail":   True,
            })

    if not rows:
        log("\nNo data produced — check Overpass connectivity and bbox coordinates.")
        return

    result = pd.DataFrame(rows)
    out_path = CHARTS_DIR / "clean_retail_corridors.csv"
    result.to_csv(out_path, index=False)
    log(f"\nWrote {len(result)} rows to {out_path}")

    summary = (
        result.drop_duplicates(subset=["corridor_id"])
        [["corridor", "avg_monthly_2021", "avg_monthly_2025", "trajectory_index", "annual_calls_2021"]]
        .sort_values("trajectory_index")
    )
    log("\nClean retail summary (best → worst trajectory):")
    log(summary.to_string(index=False))


if __name__ == "__main__":
    main()
