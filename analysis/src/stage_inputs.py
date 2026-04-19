"""Stage raw inputs into interim/ with normalized column names and types.

Reads GeoJSON files from data/raw/current/, writes cleaned DataFrames to data/interim/.
Coordinates are always extracted from GeoJSON geometry (not property fields).
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    INTERIM_DIR, RAW_CURRENT,
    ensure_dirs, load_data_sources, load_study_params, log,
)


def read_geojson(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y
    return gdf


def print_fields(label: str, gdf: gpd.GeoDataFrame) -> None:
    cols = [c for c in gdf.columns if c != "geometry"]
    log(f"Fields in {label}: {cols}")
    log(f"  Sample values: {gdf[cols].head(1).to_dict('records')}")


def stage_calls(src: dict, params: dict) -> pd.DataFrame:
    path = RAW_CURRENT / src["staged_filename"]
    if not path.exists():
        raise FileNotFoundError(
            f"Staged calls file not found: {path}\n"
            "Copy callsforservice_csv.geojson into data/raw/current/ and retry."
        )

    gdf = read_geojson(path)
    print_fields("calls_for_service", gdf)

    date_field = src.get("date_field", "CreateDatetime")
    type_field = src.get("type_field", "Call_Type")

    if date_field not in gdf.columns:
        raise KeyError(f"Date field '{date_field}' not found. Available: {list(gdf.columns)}")
    if type_field not in gdf.columns:
        raise KeyError(f"Call-type field '{type_field}' not found. Available: {list(gdf.columns)}")

    df = pd.DataFrame(gdf.drop(columns="geometry"))
    df = df.rename(columns={date_field: "event_date", type_field: "call_type"})

    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce", utc=True).dt.tz_localize(None)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["call_type_lower"] = df["call_type"].str.lower().str.strip()

    pattern = "|".join(params["non_traffic_call_types"])
    df["is_non_traffic"] = df["call_type_lower"].str.contains(pattern, na=False)

    df = df.dropna(subset=["event_date"])
    log(f"Staged calls: {len(df):,} rows, {df['is_non_traffic'].sum():,} non-traffic (coordinates added by geocode step)")
    return df


def main() -> None:
    ensure_dirs()
    sources = load_data_sources()
    params = load_study_params()

    df_calls = stage_calls(sources["calls_for_service"], params)
    df_calls.to_parquet(INTERIM_DIR / "calls_staged.parquet", index=False)
    log("Wrote calls_staged.parquet")


if __name__ == "__main__":
    main()
