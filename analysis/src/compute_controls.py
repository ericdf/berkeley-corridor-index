"""Compute control corridor non-traffic call trends.

Applies the same rolling 3-month YoY method to North Shattuck and
South Telegraph to provide context for citywide trend baselines.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dateutil.relativedelta import relativedelta
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    CHARTS_DIR, INTERIM_DIR,
    ensure_dirs, load_study_params, log,
)

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def main() -> pd.DataFrame:
    ensure_dirs()
    params = load_study_params()
    corridors = params["control_corridors"]
    window_mo = params["rolling_yoy_window_months"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    min_year = df["event_date"].dt.year.min()
    max_year = df["event_date"].dt.year.max()

    rows = []
    for corridor_id, corridor in corridors.items():
        pt = Point(corridor["center_lon"], corridor["center_lat"])
        corridor_gdf = gpd.GeoDataFrame(geometry=[pt], crs=CRS_GEO).to_crs(CRS_PROJ)
        zone = corridor_gdf.geometry.buffer(corridor["radius_m"]).iloc[0]
        corridor_calls = calls_gdf[calls_gdf.geometry.within(zone)].copy()

        for year in range(min_year + 1, max_year + 1):
            for start_month in range(1, 13):
                window_start = pd.Timestamp(year=year, month=start_month, day=1)
                window_end = window_start + relativedelta(months=window_mo)
                prev_start = window_start - relativedelta(years=1)
                prev_end = window_end - relativedelta(years=1)

                if window_end > pd.Timestamp.now():
                    continue

                curr = len(corridor_calls[
                    (corridor_calls["event_date"] >= window_start) &
                    (corridor_calls["event_date"] < window_end)
                ])
                prev = len(corridor_calls[
                    (corridor_calls["event_date"] >= prev_start) &
                    (corridor_calls["event_date"] < prev_end)
                ])

                pct = ((curr - prev) / prev * 100) if prev > 0 else None

                rows.append({
                    "corridor_id": corridor_id,
                    "corridor_label": corridor["label"],
                    "window_start": window_start.date().isoformat(),
                    "window_end": window_end.date().isoformat(),
                    "year": year,
                    "month": start_month,
                    "current_count": curr,
                    "prior_year_count": prev,
                    "yoy_pct_change": round(pct, 1) if pct is not None else None,
                })

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "corridor_controls.csv", index=False)
    log("Wrote corridor_controls.csv")
    return result


if __name__ == "__main__":
    main()
