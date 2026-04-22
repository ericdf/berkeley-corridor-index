"""Rank all named Berkeley primary/secondary corridors by call trajectory 2021-2025.

Groups OSM road segments by primary name, buffers 75m, counts non-traffic calls
per month, and computes a trajectory index (2025 avg / 2021 avg * 100).
Corridors with fewer than MIN_ANNUAL_CALLS in 2021 are excluded as too quiet
to produce stable rates.

Shows where the study corridors (University Ave, San Pablo) rank in the
full distribution of Berkeley named corridors.

Outputs:
  data/processed/charts/corridor_rankings.csv
"""

import ast
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ROOT, ensure_dirs, log

REFERENCE_DIR = ROOT / "data" / "reference"

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 75
MIN_ANNUAL_CALLS = 30   # minimum 2021 call count to include corridor

STUDY_CORRIDORS = {
    "University Avenue (west of MLK)",
    "University Avenue (east of MLK)",
    "San Pablo Avenue (south)",
    "San Pablo Avenue (north)",
    "Shattuck Avenue (south of University)",
    "Shattuck Avenue (north of University)",
    "Telegraph Avenue (south)",
    "Telegraph Avenue (north)",
}

# Split long N-S corridors at University Ave latitude; split University Ave at MLK longitude.
# Segments south/west of the divider get the study shelter sites.
SPLIT_LAT = 37.870   # roughly University Ave cross-street
SPLIT_LON = -122.272  # roughly MLK Jr Way

CORRIDOR_SPLITS: dict[str, tuple[str, str]] = {
    # N-S roads: split by latitude into (south_label, north_label)
    "Shattuck Avenue":  ("Shattuck Avenue (south of University)", "Shattuck Avenue (north of University)"),
    "San Pablo Avenue": ("San Pablo Avenue (south)",              "San Pablo Avenue (north)"),
    "Telegraph Avenue": ("Telegraph Avenue (south)",              "Telegraph Avenue (north)"),
    "Adeline Street":   ("Adeline Street (south)",                "Adeline Street (north)"),
    # E-W roads: split by longitude into (west_label, east_label)
    "University Avenue": ("University Avenue (west of MLK)",      "University Avenue (east of MLK)"),
}


def primary_name(raw) -> str | None:
    """Extract first name from OSM name field (stored as numpy array or scalar)."""
    if raw is None:
        return None
    import numpy as np
    if isinstance(raw, np.ndarray):
        return str(raw[0]).strip() if len(raw) > 0 else None
    if isinstance(raw, list):
        return str(raw[0]).strip() if raw else None
    try:
        parsed = ast.literal_eval(str(raw))
        if isinstance(parsed, list) and parsed:
            return str(parsed[0]).strip()
    except (ValueError, SyntaxError):
        pass
    return str(raw).strip()


def main() -> None:
    ensure_dirs()

    roads = gpd.read_file(REFERENCE_DIR / "berkeley_major_roads.geojson").to_crs(CRS_PROJ)
    roads["primary_name"] = roads["name"].apply(primary_name)
    roads = roads[roads["primary_name"].notna()]

    # For corridors in CORRIDOR_SPLITS, tag each segment north/south or east/west
    # before dissolving, so they become separate corridor entries.
    split_lat_proj = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy([-122.30], [SPLIT_LAT]), crs=CRS_GEO
    ).to_crs(CRS_PROJ).geometry.iloc[0].y

    split_lon_proj = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy([SPLIT_LON], [37.87]), crs=CRS_GEO
    ).to_crs(CRS_PROJ).geometry.iloc[0].x

    def assign_corridor_label(row):
        name = row["primary_name"]
        if name not in CORRIDOR_SPLITS:
            return name
        label_lo, label_hi = CORRIDOR_SPLITS[name]
        centroid = row["geometry"].centroid
        # N-S roads split by latitude; E-W roads split by longitude
        if name == "University Avenue":
            return label_lo if centroid.x < split_lon_proj else label_hi
        else:
            return label_lo if centroid.y < split_lat_proj else label_hi

    roads["corridor_label"] = roads.apply(assign_corridor_label, axis=1)

    corridors = (
        roads.groupby("corridor_label")["geometry"]
        .apply(lambda geoms: unary_union(geoms).buffer(BUFFER_M))
        .reset_index()
        .rename(columns={"corridor_label": "primary_name"})
    )
    corridors = gpd.GeoDataFrame(corridors, geometry="geometry", crs=CRS_PROJ)
    log(f"Named corridors: {len(corridors)}")

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()
    df_nt["year"] = df_nt["event_date"].dt.year
    df_nt["month"] = df_nt["event_date"].dt.month

    calls = gpd.GeoDataFrame(
        df_nt, geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)

    # Spatial join: assign each call to corridor(s) it falls within
    joined = gpd.sjoin(calls, corridors, how="inner", predicate="within")

    # Monthly counts per corridor
    monthly = (
        joined.groupby(["primary_name", "year", "month"])
        .size()
        .reset_index(name="count")
    )

    rows = []
    for corridor_name, grp in monthly.groupby("primary_name"):
        y2021 = grp[grp["year"] == 2021]["count"]
        y2025 = grp[grp["year"] == 2025]["count"]

        annual_2021 = y2021.sum()
        if annual_2021 < MIN_ANNUAL_CALLS:
            continue

        avg_2021 = y2021.mean()
        avg_2025 = y2025.mean() if len(y2025) >= 6 else None  # require ≥6 months of 2025

        if avg_2025 is None or avg_2021 == 0:
            continue

        trajectory = round(avg_2025 / avg_2021 * 100, 1)

        rows.append({
            "corridor": corridor_name,
            "avg_monthly_2021": round(avg_2021, 1),
            "avg_monthly_2025": round(avg_2025, 1),
            "trajectory_index": trajectory,   # 100 = flat, >100 = worsening, <100 = improving
            "annual_calls_2021": int(annual_2021),
            "is_study_corridor": corridor_name in STUDY_CORRIDORS,
        })

    result = pd.DataFrame(rows).sort_values("trajectory_index", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1
    result["rank_of"] = len(result)

    result.to_csv(CHARTS_DIR / "corridor_rankings.csv", index=False)
    log(f"Ranked {len(result)} corridors (excluded {len(corridors) - len(result)} below activity threshold)")
    log("")
    log("Full ranking (worst → best):")
    for _, row in result.iterrows():
        marker = " <-- STUDY" if row["is_study_corridor"] else ""
        log(f"  #{int(row['rank']):2d}  {row['corridor']:<35s} "
            f"index={row['trajectory_index']:6.1f}  "
            f"({row['avg_monthly_2021']:.1f} → {row['avg_monthly_2025']:.1f}/mo){marker}")


if __name__ == "__main__":
    main()
