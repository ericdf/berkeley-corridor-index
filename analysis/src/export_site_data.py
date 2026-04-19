"""Export final downloadable tables and build metadata."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    CHARTS_DIR, DOWNLOADS_DIR, METADATA_DIR, RAW_METADATA,
    ensure_dirs, load_sites, load_study_params, log, write_json,
)


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


def main() -> None:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()

    # site_summary.csv — one row per site with opening date + program type
    summary_rows = [{
        "site_id": s["id"],
        "address": s["address"],
        "opening_date": s["opening_date"],
        "program_type": s["program_type"],
        "notes": s.get("notes", ""),
    } for s in sites]
    pd.DataFrame(summary_rows).to_csv(DOWNLOADS_DIR / "site_summary.csv", index=False)

    # opening_dates.csv
    dates_rows = [{"site_id": s["id"], "address": s["address"], "opening_date": s["opening_date"]} for s in sites]
    pd.DataFrame(dates_rows).to_csv(DOWNLOADS_DIR / "opening_dates.csv", index=False)

    # site_level_results.csv — copy of pre/post chart CSV
    pre_post_src = CHARTS_DIR / "pre_post_site_nontraffic_calls.csv"
    if pre_post_src.exists():
        import shutil
        shutil.copy(pre_post_src, DOWNLOADS_DIR / "site_level_results.csv")

    # methodology_inputs.csv — study parameters as table
    method_rows = [
        {"parameter": "pre_post_window_months", "value": params["pre_post_window_months"]},
        {"parameter": "site_block_radius_m", "value": params["zones"]["site_block_m"]},
        {"parameter": "adjacent_blocks_radius_m", "value": params["zones"]["adjacent_blocks_m"]},
        {"parameter": "wider_nearby_radius_m", "value": params["zones"]["wider_nearby_m"]},
        {"parameter": "rolling_yoy_window_months", "value": params["rolling_yoy_window_months"]},
    ]
    pd.DataFrame(method_rows).to_csv(DOWNLOADS_DIR / "methodology_inputs.csv", index=False)

    # build.json metadata
    fetch_meta = {}
    fetch_meta_path = RAW_METADATA / "fetch_meta.json"
    if fetch_meta_path.exists():
        with open(fetch_meta_path) as f:
            fetch_meta = json.load(f)

    build_meta = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "data_refresh_date": fetch_meta.get("fetched_at", "unknown"),
        "study_period_months": params["pre_post_window_months"],
        "sites": [s["id"] for s in sites],
        "source_notes": "Berkeley open data portal; see data_sources.yml",
    }
    write_json(METADATA_DIR / "build.json", build_meta)

    log("Download CSVs and build metadata written.")


if __name__ == "__main__":
    main()
