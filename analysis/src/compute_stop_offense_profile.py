"""Categorize stop offenses near shelter sites vs citywide baseline.

Uses offense_raw field (SuspectedViolation for old format; best available
charge for new format) to classify pedestrian stops into meaningful categories.

Useful for understanding *why* police are stopping people near shelter sites
and whether the composition differs from the citywide pattern.

Outputs:
  data/processed/charts/stop_offense_profile.csv   — counts/rates by site × category
  data/processed/charts/stop_offense_citywide.csv  — citywide baseline for comparison
"""

import re
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

# Order matters: first match wins
OFFENSE_CATEGORIES = [
    ("drug – paraphernalia",    r"11364"),
    ("drug – possession",       r"11377|11350|11351|11352|11357|11358|11359"),
    ("drug – dealing/sales",    r"11360|11378|11379|11380|11383"),
    ("alcohol",                 r"25620|647\(f\)|647f|23152|23153"),
    ("theft / robbery",         r"484|487|211\b|459\b|10851"),
    ("trespass",                r"602\b"),
    ("violence / weapons",      r"242\b|243\b|245\b|273|417\b|422\b"),
    ("disorder / disturbance",  r"415\b|647\(e\)|647e|647\(g\)|375"),
    ("warrant",                 r"warrant"),
    ("mental health / welfare", r"5150|community caretaking|caretaking"),
    ("vandalism",               r"594\b"),
    ("other / unknown",         r".+"),   # catch-all for non-empty offense
]


def categorize_offense(raw: str) -> str:
    if not raw or not raw.strip():
        return "no offense recorded"
    r = raw.lower()
    for label, pattern in OFFENSE_CATEGORIES:
        if re.search(pattern, r):
            return label
    return "other / unknown"


def site_zone(lat, lon):
    return (
        gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=CRS_GEO)
        .to_crs(CRS_PROJ).geometry.buffer(BUFFER_M).iloc[0]
    )


def profile(subset: pd.DataFrame) -> pd.Series:
    return subset["offense_category"].value_counts(normalize=True).mul(100).round(1)


def main() -> None:
    ensure_dirs()
    sites = load_sites()

    df = pd.read_parquet(INTERIM_DIR / "stops_staged.parquet")
    df = df[df["is_pedestrian"] & df["lat"].notna() & df["lon"].notna()].copy()
    df["offense_category"] = df["offense_raw"].fillna("").apply(categorize_offense)

    stops = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)

    # Citywide baseline
    citywide_pct = profile(stops)
    citywide_n   = stops["offense_category"].value_counts()

    log("Citywide pedestrian stop offense profile:")
    for cat, pct in citywide_pct.items():
        log(f"  {cat:<30s} {pct:5.1f}%  (n={citywide_n[cat]})")

    citywide_df = pd.DataFrame({
        "category": citywide_pct.index,
        "citywide_pct": citywide_pct.values,
        "citywide_n": citywide_n.reindex(citywide_pct.index).values,
    })
    citywide_df.to_csv(CHARTS_DIR / "stop_offense_citywide.csv", index=False)

    # Per-site profile
    rows = []
    all_cats = [c for c, _ in OFFENSE_CATEGORIES] + ["no offense recorded"]

    for s in sites:
        zone = site_zone(s["lat"], s["lon"])
        zs = stops[stops.geometry.within(zone)]
        if len(zs) == 0:
            continue

        site_pct = profile(zs)
        site_n   = zs["offense_category"].value_counts()

        log(f"\n{s['address']} (n={len(zs)}):")
        for cat in all_cats:
            sp  = site_pct.get(cat, 0.0)
            cp  = citywide_pct.get(cat, 0.0)
            n   = site_n.get(cat, 0)
            if sp == 0 and cp == 0:
                continue
            diff = sp - cp
            flag = " **" if abs(diff) >= 5 and n >= 3 else ""
            log(f"  {cat:<30s} {sp:5.1f}% vs {cp:5.1f}% citywide  ({diff:+.1f}){flag}")

            rows.append({
                "site_id":       s["id"],
                "label":         s["label"],
                "address":       s["address"],
                "category":      cat,
                "site_n":        int(n),
                "site_pct":      sp,
                "citywide_pct":  cp,
                "diff_pct":      round(diff, 1),
                "total_stops":   len(zs),
            })

    pd.DataFrame(rows).to_csv(CHARTS_DIR / "stop_offense_profile.csv", index=False)
    log("\nWrote stop_offense_profile.csv and stop_offense_citywide.csv")


if __name__ == "__main__":
    main()
