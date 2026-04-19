"""Compute rolling averages for each treatment geography.

Outputs:
  university_cluster_rolling.csv  — University core 3-month rolling avg
  san_pablo_rolling.csv           — San Pablo node 3-month rolling avg
  corridor_rolling_3mo_avg.csv    — legacy alias (university cluster, for backwards compat)
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, ensure_dirs, log


def rolling_avg(src_csv: str, dest_csv: str) -> pd.DataFrame:
    monthly = pd.read_csv(CHARTS_DIR / src_csv, parse_dates=["date"])
    monthly = monthly.sort_values("date").reset_index(drop=True)

    monthly["rolling_3mo_avg"] = (
        monthly["non_traffic_count"].rolling(window=3, min_periods=1).mean().round(1)
    )

    monthly["month_key"] = monthly["date"].dt.month
    monthly["year"] = monthly["date"].dt.year
    prior = monthly[["year", "month_key", "non_traffic_count"]].copy()
    prior["year"] = prior["year"] + 1
    prior = prior.rename(columns={"non_traffic_count": "prior_year_count"})

    monthly = monthly.merge(prior, on=["year", "month_key"], how="left")
    monthly["yoy_pct_change"] = (
        (monthly["non_traffic_count"] - monthly["prior_year_count"])
        / monthly["prior_year_count"] * 100
    ).round(1)

    monthly.drop(columns=["month_key"]).to_csv(CHARTS_DIR / dest_csv, index=False)
    log(f"Wrote {dest_csv}")
    return monthly


def main() -> None:
    ensure_dirs()
    rolling_avg("university_cluster_monthly.csv", "university_cluster_rolling.csv")
    rolling_avg("san_pablo_monthly.csv", "san_pablo_rolling.csv")
    # Legacy alias consumed by chart-hero.js and older chart code
    import shutil
    shutil.copy(CHARTS_DIR / "university_cluster_rolling.csv",
                CHARTS_DIR / "corridor_rolling_3mo_avg.csv")
    log("Wrote corridor_rolling_3mo_avg.csv (legacy alias of university_cluster_rolling.csv)")


if __name__ == "__main__":
    main()
