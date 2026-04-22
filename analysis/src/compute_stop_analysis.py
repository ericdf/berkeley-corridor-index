"""Analyze RIPA stop data near shelter sites.

Three analyses:
  1. Pedestrian stop counts pre/post each site opening (100m buffer)
  2. Perceived-unhoused stop concentration near sites vs citywide (2024+ only)
  3. City-of-residence breakdown near sites vs citywide baseline —
     empirical test of the county placement pipeline hypothesis

Vehicle stops are retained in the data but flagged; core analysis uses
pedestrian only. Vehicle results are included for reference.

Outputs:
  data/processed/charts/stop_prepost.csv
  data/processed/charts/stop_unhoused_concentration.csv
  data/processed/charts/stop_residence.csv
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ensure_dirs, load_sites, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 100
PRE_MONTHS = 12


def make_zone(lat, lon):
    return (
        gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=CRS_GEO)
        .to_crs(CRS_PROJ)
        .geometry.buffer(BUFFER_M)
        .iloc[0]
    )


def in_zone(stops: gpd.GeoDataFrame, zone) -> gpd.GeoDataFrame:
    return stops[stops.geometry.within(zone)]


def count_window(stops: gpd.GeoDataFrame, start: pd.Timestamp, end: pd.Timestamp) -> int:
    return int(stops[(stops["stop_datetime"] >= start) & (stops["stop_datetime"] < end)].shape[0])


def main() -> None:
    ensure_dirs()
    sites = load_sites()

    df = pd.read_parquet(INTERIM_DIR / "stops_staged.parquet")
    df = df.dropna(subset=["lat", "lon"])

    stops = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)

    ped = stops[stops["is_pedestrian"]].copy()
    veh = stops[~stops["is_pedestrian"]].copy()
    log(f"Pedestrian: {len(ped):,}  Vehicular: {len(veh):,}")

    data_start = stops["stop_datetime"].min()
    data_end = stops["stop_datetime"].max()

    # ----------------------------------------------------------------
    # 1. Pre/post pedestrian stops per site
    # ----------------------------------------------------------------
    log("\n--- 1. Pre/post pedestrian stops ---")
    prepost_rows = []
    for s in sites:
        opening = pd.Timestamp(s["opening_date"])
        pre_start = opening - pd.DateOffset(months=PRE_MONTHS)
        pre_start = max(pre_start, data_start)
        pre_months = max(0.0, (opening - pre_start).days / 30.44)
        post_months = max(0.0, (data_end - opening).days / 30.44)

        zone = make_zone(s["lat"], s["lon"])

        for label, subset, is_ped in [("pedestrian", ped, True), ("vehicular", veh, False)]:
            zs = in_zone(subset, zone)
            pre_n  = count_window(zs, pre_start, opening)
            post_n = count_window(zs, opening, data_end)
            pre_r  = round(pre_n / pre_months, 2) if pre_months > 0 else None
            post_r = round(post_n / post_months, 2) if post_months > 0 else None
            chg    = round((post_r - pre_r) / pre_r * 100, 1) if pre_r and pre_r > 0 else None

            prepost_rows.append({
                "site_id": s["id"], "label": s["label"], "address": s["address"],
                "opening_date": s["opening_date"],
                "stop_type": label, "is_primary": is_ped,
                "pre_count": pre_n, "post_count": post_n,
                "pre_months": round(pre_months, 1), "post_months": round(post_months, 1),
                "pre_rate": pre_r, "post_rate": post_r,
                "rate_change_pct": chg,
            })

        row = next(r for r in prepost_rows[-2:] if r["stop_type"] == "pedestrian")
        log(f"  {s['address']}: ped pre {row['pre_rate']}/mo → post {row['post_rate']}/mo "
            f"({row['rate_change_pct']:+.1f}%)" if row['rate_change_pct'] is not None
            else f"  {s['address']}: ped pre {row['pre_rate']}/mo → post {row['post_rate']}/mo")

    pd.DataFrame(prepost_rows).to_csv(CHARTS_DIR / "stop_prepost.csv", index=False)
    log("Wrote stop_prepost.csv")

    # ----------------------------------------------------------------
    # 2. Perceived-unhoused concentration (2024+ new format only)
    # ----------------------------------------------------------------
    log("\n--- 2. Perceived-unhoused concentration (2024+) ---")
    ped_new = ped[ped["source"] == "new"].copy()
    citywide_unhoused_rate = (
        ped_new["perceived_unhoused"].sum() / len(ped_new)
        if len(ped_new) > 0 else 0
    )
    log(f"  Citywide pedestrian stops perceived unhoused: "
        f"{int(ped_new['perceived_unhoused'].sum())} / {len(ped_new)} "
        f"= {citywide_unhoused_rate:.1%}")

    unhoused_rows = []
    for s in sites:
        zone = make_zone(s["lat"], s["lon"])
        zs = in_zone(ped_new, zone)
        if len(zs) == 0:
            continue
        n_unhoused = int(zs["perceived_unhoused"].sum())
        rate = n_unhoused / len(zs)
        unhoused_rows.append({
            "site_id": s["id"], "label": s["label"], "address": s["address"],
            "ped_stops_total": len(zs),
            "perceived_unhoused_n": n_unhoused,
            "pct_unhoused": round(rate * 100, 1),
            "citywide_pct_unhoused": round(citywide_unhoused_rate * 100, 1),
            "ratio_vs_citywide": round(rate / citywide_unhoused_rate, 2) if citywide_unhoused_rate > 0 else None,
        })
        log(f"  {s['address']}: {n_unhoused}/{len(zs)} = {rate:.1%} unhoused "
            f"(citywide {citywide_unhoused_rate:.1%}, "
            f"{rate/citywide_unhoused_rate:.1f}x)")

    pd.DataFrame(unhoused_rows).to_csv(CHARTS_DIR / "stop_unhoused_concentration.csv", index=False)
    log("Wrote stop_unhoused_concentration.csv")

    # ----------------------------------------------------------------
    # 3. City of residence: near sites vs citywide
    # ----------------------------------------------------------------
    log("\n--- 3. City of residence ---")

    def residence_summary(subset: pd.DataFrame, label: str) -> dict:
        total = len(subset)
        if total == 0:
            return {}
        berkeley = (subset["city_of_residence"] == "BERKELEY").sum()
        unknown  = subset["city_of_residence"].isin(["UNKNOWN", "OUT OF STATE CITY", ""]).sum()
        non_berk = total - berkeley - unknown
        return {
            "group": label,
            "total_stops": total,
            "berkeley_n": int(berkeley),
            "non_berkeley_n": int(non_berk),
            "unknown_n": int(unknown),
            "pct_berkeley": round(berkeley / total * 100, 1),
            "pct_non_berkeley": round(non_berk / total * 100, 1),
        }

    res_rows = [residence_summary(ped, "citywide_all_years")]

    for s in sites:
        zone = make_zone(s["lat"], s["lon"])
        zs = in_zone(ped, zone)
        res_rows.append(residence_summary(zs, s["address"]))

        # Also break down top non-Berkeley cities near each site
        non_berk = zs[
            ~zs["city_of_residence"].isin(["BERKELEY", "UNKNOWN", "OUT OF STATE CITY", ""])
        ]
        top = non_berk["city_of_residence"].value_counts().head(5)
        r = res_rows[-1]
        log(f"  {s['address']}: {r['pct_berkeley']:.1f}% Berkeley, "
            f"{r['pct_non_berkeley']:.1f}% non-Berkeley  "
            f"| top origins: {top.to_dict()}")

    res_df = pd.DataFrame(res_rows)
    res_df.to_csv(CHARTS_DIR / "stop_residence.csv", index=False)
    log("Wrote stop_residence.csv")


if __name__ == "__main__":
    main()
