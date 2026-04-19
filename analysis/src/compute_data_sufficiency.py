"""Compute and export post-period data sufficiency flags for all sites.

A site's post window is sufficient when >= 50% of the 12-month window
falls within the available data range. Exports a standalone CSV so the
frontend can suppress overconfident claims without re-deriving thresholds.

Output: insufficient_post_period_flags.csv
"""

import sys
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, ensure_dirs, load_sites, load_study_params, log

POST_COVERAGE_THRESHOLD = 0.50


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    window = params["pre_post_window_months"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    data_max = df["event_date"].max()

    rows = []
    for s in sites:
        opening = pd.Timestamp(s["opening_date"])
        post_end = opening + relativedelta(months=window)
        post_days_total = (post_end - opening).days
        post_days_available = max((min(data_max, post_end) - opening).days, 0)
        coverage = post_days_available / post_days_total if post_days_total > 0 else 0
        sufficient = coverage >= POST_COVERAGE_THRESHOLD
        rows.append({
            "site_id": s["id"],
            "address": s["address"],
            "opening_date": s["opening_date"],
            "geography_group": s.get("geography_group", ""),
            "post_end": post_end.date().isoformat(),
            "data_through": data_max.date().isoformat(),
            "post_coverage_pct": round(coverage * 100, 1),
            "post_sufficient": str(sufficient).lower(),
        })
        log(f"{s['address']}: {coverage:.0%} post coverage — {'sufficient' if sufficient else 'INSUFFICIENT'}")

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "insufficient_post_period_flags.csv", index=False)
    log("Wrote insufficient_post_period_flags.csv")
    return result


if __name__ == "__main__":
    main()
