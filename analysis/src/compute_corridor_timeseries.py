"""Legacy alias: corridor monthly calls = University core cluster monthly calls.

The primary time series computation is now in compute_cluster_monthly.py.
This module copies outputs so that chart-hero.js and other legacy consumers
continue to work without changes.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, ensure_dirs, log


def main() -> None:
    ensure_dirs()
    shutil.copy(CHARTS_DIR / "university_cluster_monthly.csv",
                CHARTS_DIR / "corridor_monthly_calls.csv")
    shutil.copy(CHARTS_DIR / "cluster_opening_events.csv",
                CHARTS_DIR / "corridor_opening_events.csv")
    log("corridor_monthly_calls.csv + corridor_opening_events.csv written (from university cluster)")


if __name__ == "__main__":
    main()
