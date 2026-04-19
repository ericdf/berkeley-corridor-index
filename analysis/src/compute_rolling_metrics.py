"""Compute corridor rolling averages and same-season YoY comparisons.

Outputs:
  corridor_rolling_3mo_avg.csv  — monthly calls + 3-month rolling average
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, ensure_dirs, log


def main() -> pd.DataFrame:
    ensure_dirs()

    monthly = pd.read_csv(CHARTS_DIR / "corridor_monthly_calls.csv", parse_dates=["date"])
    monthly = monthly.sort_values("date").reset_index(drop=True)

    monthly["rolling_3mo_avg"] = (
        monthly["non_traffic_count"].rolling(window=3, min_periods=1).mean().round(1)
    )

    # Same-season YoY: compare each month to the same month previous year
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

    monthly.drop(columns=["month_key"]).to_csv(
        CHARTS_DIR / "corridor_rolling_3mo_avg.csv", index=False
    )
    log("Wrote corridor_rolling_3mo_avg.csv")
    return monthly


if __name__ == "__main__":
    main()
