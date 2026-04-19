"""Compute active site count by month.

A site is 'active' when its opening_date <= the first day of that month.
Also produces cumulative_openings_effects.csv (corridor calls + active sites).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, ensure_dirs, load_sites, log


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()

    monthly = pd.read_csv(CHARTS_DIR / "university_cluster_monthly.csv", parse_dates=["date"])

    openings = {s["id"]: pd.Timestamp(s["opening_date"]) for s in sites}

    def active_count(row_date: pd.Timestamp) -> int:
        return sum(1 for d in openings.values() if d <= row_date)

    def newly_opened(row_date: pd.Timestamp) -> str:
        month_end = row_date + pd.offsets.MonthEnd(0)
        opened = [s["address"] for s in sites
                  if row_date <= pd.Timestamp(s["opening_date"]) <= month_end]
        return "; ".join(opened) if opened else ""

    monthly["active_sites"] = monthly["date"].apply(active_count)
    monthly["newly_opened"] = monthly["date"].apply(newly_opened)

    monthly.to_csv(CHARTS_DIR / "active_sites_by_month.csv", index=False)
    log("Wrote active_sites_by_month.csv")

    # Merged file for dual-axis / overlay charts
    monthly.to_csv(CHARTS_DIR / "cumulative_openings_effects.csv", index=False)
    log("Wrote cumulative_openings_effects.csv")

    return monthly


if __name__ == "__main__":
    main()
