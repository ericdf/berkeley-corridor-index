"""Benchmark study sites against incumbent overnight homeless services facilities.

Loads incumbents.yml, counts non-traffic calls within 100m of each facility,
and ranks study sites against the incumbent peer distribution.

Facilities with fewer than MIN_OPERATING_MONTHS of data in the call dataset
(or flagged monitor_only) are excluded from the comparison distribution but
still appear in the output with an is_excluded flag so they can be tracked.

Outputs:
  data/processed/charts/incumbent_benchmark.csv
"""

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
MIN_OPERATING_MONTHS = 12


def load_incumbents() -> list[dict]:
    return load_config("incumbents.yml")["incumbents"]


def calls_in_zone(calls: gpd.GeoDataFrame, lat: float, lon: float) -> gpd.GeoDataFrame:
    pt = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs=CRS_GEO).to_crs(CRS_PROJ)
    zone = pt.geometry.buffer(BUFFER_M).iloc[0]
    return calls[calls.geometry.within(zone)]


def count_in_window(calls: gpd.GeoDataFrame, start: pd.Timestamp, end: pd.Timestamp) -> int:
    return int(calls[(calls["event_date"] >= start) & (calls["event_date"] < end)].shape[0])


def percentile_of(value: float, dist: list[float]) -> float | None:
    if not dist:
        return None
    return round(sum(v < value for v in dist) / len(dist) * 100, 1)


def main() -> None:
    ensure_dirs()
    incumbents = load_incumbents()
    sites = load_sites()

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"] & df["lon"].notna() & df["lat"].notna()].copy()
    calls = gpd.GeoDataFrame(
        df_nt, geometry=gpd.points_from_xy(df_nt["lon"], df_nt["lat"]), crs=CRS_GEO
    ).to_crs(CRS_PROJ)

    data_start = df_nt["event_date"].min()
    data_end = df_nt["event_date"].max()
    full_months = (data_end - data_start).days / 30.44
    log(f"Call data: {data_start.date()} – {data_end.date()} ({full_months:.1f} months)")
    log(f"Non-traffic calls with coords: {len(calls):,}")

    rows = []
    for inc in incumbents:
        monitor_only = inc.get("monitor_only", False)

        # Determine how many months this facility has been operating within the data window
        if inc["opening_date"] is None:
            operating_start = data_start
            operating_months = full_months
        else:
            opening = pd.Timestamp(inc["opening_date"])
            operating_start = max(opening, data_start)
            operating_months = max(0.0, (data_end - operating_start).days / 30.44)

        insufficient = operating_months < MIN_OPERATING_MONTHS
        is_excluded = monitor_only or insufficient

        zone_calls = calls_in_zone(calls, inc["lat"], inc["lon"])
        total_count = count_in_window(zone_calls, operating_start, data_end)
        rate_per_month = round(total_count / operating_months, 2) if operating_months > 0 else None

        rows.append({
            "id": inc["id"],
            "label": inc["label"],
            "address": inc["address"],
            "operator": inc.get("operator"),
            "program_type": inc.get("program_type"),
            "opening_date": inc["opening_date"],
            "operating_months": round(operating_months, 1),
            "call_count": total_count,
            "rate_per_month": rate_per_month,
            "monitor_only": monitor_only,
            "insufficient_history": insufficient,
            "is_excluded": is_excluded,
        })

        status = "EXCLUDED" if is_excluded else "included"
        log(f"{inc['label']}: {total_count} calls over {operating_months:.1f} mo "
            f"({rate_per_month}/mo) [{status}]")

    result = pd.DataFrame(rows)

    # Distribution for ranking: incumbents with sufficient history only
    peer_rates = result.loc[~result["is_excluded"], "rate_per_month"].dropna().tolist()
    peer_counts = result.loc[~result["is_excluded"], "call_count"].dropna().tolist()
    log(f"Peer distribution: {len(peer_rates)} facilities — "
        f"rates {[round(r,1) for r in sorted(peer_rates)]}")

    # Rank each incumbent against the peer distribution
    result["percentile_among_peers"] = result["rate_per_month"].apply(
        lambda r: percentile_of(r, peer_rates) if pd.notna(r) else None
    )

    # Rank study sites against the same peer distribution
    first_opening = min(pd.Timestamp(s["opening_date"]) for s in sites)
    calls_pre = calls[calls["event_date"] < first_opening]
    pre_months = max(0.0, (first_opening - data_start).days / 30.44)
    post_months = max(0.0, (data_end - first_opening).days / 30.44)

    site_rows = []
    for s in sites:
        site_opening = pd.Timestamp(s["opening_date"])
        zone_calls_all = calls_in_zone(calls, s["lat"], s["lon"])
        zone_calls_pre = calls_in_zone(calls_pre, s["lat"], s["lon"])

        count_all = count_in_window(zone_calls_all, data_start, data_end)
        count_pre = count_in_window(zone_calls_pre, data_start, first_opening)
        count_post = count_in_window(zone_calls_all, site_opening, data_end)
        site_post_months = max(0.0, (data_end - site_opening).days / 30.44)

        rate_all = round(count_all / full_months, 2) if full_months > 0 else None
        rate_pre = round(count_pre / pre_months, 2) if pre_months > 0 else None
        rate_post = round(count_post / site_post_months, 2) if site_post_months > 0 else None

        site_rows.append({
            "id": s["id"],
            "label": s["label"],
            "address": s["address"],
            "opening_date": s["opening_date"],
            "rate_per_month_all": rate_all,
            "rate_per_month_pre": rate_pre,
            "rate_per_month_post": rate_post,
            "percentile_pre_vs_peers": percentile_of(rate_pre, peer_rates) if rate_pre is not None else None,
            "percentile_post_vs_peers": percentile_of(rate_post, peer_rates) if rate_post is not None else None,
            "percentile_all_vs_peers": percentile_of(rate_all, peer_rates) if rate_all is not None else None,
        })
        log(f"  {s['address']}: pre {rate_pre}/mo "
            f"(peer {site_rows[-1]['percentile_pre_vs_peers']}th pct) → "
            f"post {rate_post}/mo "
            f"(peer {site_rows[-1]['percentile_post_vs_peers']}th pct)")

    result.to_csv(CHARTS_DIR / "incumbent_benchmark.csv", index=False)
    pd.DataFrame(site_rows).to_csv(CHARTS_DIR / "site_vs_incumbents.csv", index=False)
    log("Wrote incumbent_benchmark.csv and site_vs_incumbents.csv")


if __name__ == "__main__":
    main()
