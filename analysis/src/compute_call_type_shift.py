"""Analyze whether the nature of non-traffic calls changed before/after each site opened.

For each study site and monitored incumbent (1512), computes per-call-type rates
in the 12-month pre-opening window vs. the full post-opening window, normalized
to calls-per-month so the windows are comparable.

Sites with no known opening date get an all-period distribution only.

Buffer: 100m (same as benchmark modules).

Outputs:
  data/processed/charts/call_type_shift.csv   — long form: one row per site × category × period
  data/processed/charts/call_type_shift_wide.csv — wide form: one row per site × category
"""

import re
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ensure_dirs, load_config, load_sites, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"
BUFFER_M = 100
PRE_WINDOW_MONTHS = 12

# Maps substring patterns (matched against call_type_lower) to category labels.
# Order matters: first match wins.
CATEGORY_RULES: list[tuple[str, str]] = [
    (r"5150|mentally ill",              "mental health"),
    (r"welfare check",                  "welfare check"),
    (r"person down|perdown",            "person down"),
    (r"415f|family disturbance",        "family disturbance"),
    (r"415e|noise disturbance|noise",   "noise"),
    (r"415\b|disturbance",              "disturbance"),
    (r"encampment|encamp",              "encampment"),
    (r"trespass|602",                   "trespassing"),
    (r"susper|susp.*person|suspicious person", "suspicious person"),
    (r"susveh|susp.*vehicle|suspicious vehicle", "suspicious vehicle"),
    (r"suscir|susp.*circ",              "suspicious activity"),
    (r"robbery|211\b",                  "robbery"),
    (r"assault|245\b",                  "assault"),
    (r"battery|242\b",                  "battery"),
    (r"fight",                          "fight"),
    (r"vandalism|594\b",                "vandalism"),
    (r"theft|484\b|487\b|grand theft",  "theft"),
    (r"burglary|459\b",                 "burglary"),
    (r"stolen vehicle|10851",           "stolen vehicle"),
    (r"pcvio|pc violation|bmcvio|bmcviolation|parole|probation", "PC/court violation"),
]


def categorize(call_type_lower: str) -> str | None:
    for pattern, label in CATEGORY_RULES:
        if re.search(pattern, call_type_lower):
            return label
    return None


def site_calls(calls: gpd.GeoDataFrame, lat: float, lon: float) -> gpd.GeoDataFrame:
    pt = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=CRS_GEO).to_crs(CRS_PROJ)
    zone = pt.geometry.buffer(BUFFER_M).iloc[0]
    return calls[calls.geometry.within(zone)].copy()


def period_rates(subset: gpd.GeoDataFrame, months: float) -> pd.Series:
    """Return calls-per-month by category for a slice of calls."""
    if months <= 0 or subset.empty:
        return pd.Series(dtype=float)
    counts = subset["category"].value_counts()
    return (counts / months).round(3)


def main() -> None:
    ensure_dirs()

    # Study sites + monitored incumbents (monitor_only=True entries from incumbents.yml)
    sites = load_sites()
    incumbents_cfg = load_config("incumbents.yml")["incumbents"]
    monitor_sites = [i for i in incumbents_cfg if i.get("monitor_only") or i.get("include_in_shift")]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()
    df_nt["category"] = df_nt["call_type_lower"].apply(categorize)
    df_nt = df_nt[df_nt["category"].notna()]  # drop uncategorized (traffic adjacent, etc.)

    calls = gpd.GeoDataFrame(
        df_nt, geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)

    data_start = df_nt["event_date"].min()
    data_end = df_nt["event_date"].max()
    log(f"Categorized non-traffic calls: {len(calls):,}  ({data_start.date()} – {data_end.date()})")

    all_categories = sorted({label for _, label in CATEGORY_RULES})

    def process(site_id, label, address, lat, lon, opening_date_str) -> list[dict]:
        sc = site_calls(calls, lat, lon)
        log(f"  {address}: {len(sc)} categorized calls in 100m zone")

        rows = []

        if opening_date_str:
            opening = pd.Timestamp(opening_date_str)
            pre_start = opening - pd.DateOffset(months=PRE_WINDOW_MONTHS)
            pre_start = max(pre_start, data_start)
            pre_months = max(0.0, (opening - pre_start).days / 30.44)
            post_months = max(0.0, (data_end - opening).days / 30.44)

            pre_calls = sc[(sc["event_date"] >= pre_start) & (sc["event_date"] < opening)]
            post_calls = sc[sc["event_date"] >= opening]

            pre_rates = period_rates(pre_calls, pre_months)
            post_rates = period_rates(post_calls, post_months)

            for cat in all_categories:
                pre_r = pre_rates.get(cat, 0.0)
                post_r = post_rates.get(cat, 0.0)
                pre_n = int(pre_calls[pre_calls["category"] == cat].shape[0])
                post_n = int(post_calls[post_calls["category"] == cat].shape[0])
                if pre_n == 0 and post_n == 0:
                    continue
                rows.append({
                    "site_id": site_id,
                    "label": label,
                    "address": address,
                    "opening_date": opening_date_str,
                    "category": cat,
                    "pre_count": pre_n,
                    "post_count": post_n,
                    "pre_months": round(pre_months, 1),
                    "post_months": round(post_months, 1),
                    "pre_rate": pre_r,
                    "post_rate": post_r,
                    "rate_change": round(post_r - pre_r, 3),
                    "rate_change_pct": round((post_r - pre_r) / pre_r * 100, 1) if pre_r > 0 else None,
                    "has_pre_post": True,
                })
        else:
            # No opening date — show all-period distribution only
            all_months = max(0.0, (data_end - data_start).days / 30.44)
            all_rates = period_rates(sc, all_months)
            for cat in all_categories:
                n = int(sc[sc["category"] == cat].shape[0])
                if n == 0:
                    continue
                rows.append({
                    "site_id": site_id,
                    "label": label,
                    "address": address,
                    "opening_date": None,
                    "category": cat,
                    "pre_count": None,
                    "post_count": None,
                    "pre_months": None,
                    "post_months": None,
                    "pre_rate": None,
                    "post_rate": all_rates.get(cat, 0.0),
                    "rate_change": None,
                    "rate_change_pct": None,
                    "has_pre_post": False,
                })

        return rows

    all_rows = []

    log("Study sites:")
    for s in sites:
        all_rows.extend(process(
            s["id"], s["label"], s["address"],
            s["lat"], s["lon"], s["opening_date"]
        ))

    log("Monitored incumbents:")
    for inc in monitor_sites:
        all_rows.extend(process(
            inc["id"], inc["label"], inc["address"],
            inc["lat"], inc["lon"], inc.get("opening_date")
        ))

    long_df = pd.DataFrame(all_rows)
    long_df.to_csv(CHARTS_DIR / "call_type_shift.csv", index=False)
    log(f"Wrote call_type_shift.csv ({len(long_df)} rows)")

    # Wide form: one row per site × category, pre_rate and post_rate as columns
    wide_df = long_df[long_df["has_pre_post"]].pivot_table(
        index=["site_id", "label", "address", "opening_date", "category"],
        values=["pre_rate", "post_rate", "rate_change", "rate_change_pct",
                "pre_count", "post_count"],
        aggfunc="first",
    ).reset_index()
    wide_df = wide_df.sort_values(["site_id", "rate_change"], ascending=[True, False])
    wide_df.to_csv(CHARTS_DIR / "call_type_shift_wide.csv", index=False)
    log(f"Wrote call_type_shift_wide.csv ({len(wide_df)} rows)")


if __name__ == "__main__":
    main()
