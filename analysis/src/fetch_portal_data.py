"""Fetch raw data from Berkeley open data portal.

Saves raw files to data/raw/current/ and records fetch metadata.
Run only when you want to refresh source data.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import (
    RAW_CURRENT, RAW_METADATA, RAW_SNAPSHOTS,
    ensure_dirs, load_data_sources, log, write_json,
)

SOCRATA_LIMIT = 50_000
APP_TOKEN = None  # set SOCRATA_APP_TOKEN env var if you have one


def fetch_json(url: str, limit: int = SOCRATA_LIMIT) -> list[dict]:
    import os
    params = {"$limit": limit, "$offset": 0}
    headers = {}
    token = os.environ.get("SOCRATA_APP_TOKEN", APP_TOKEN)
    if token:
        headers["X-App-Token"] = token

    rows = []
    while True:
        r = requests.get(url, params={**params, "$offset": len(rows)}, headers=headers, timeout=60)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < limit:
            break
    return rows


def fetch_geojson(url: str) -> dict:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> None:
    ensure_dirs()
    sources = load_data_sources()
    fetch_time = datetime.now(timezone.utc).isoformat()
    meta = {"fetched_at": fetch_time, "sources": {}}

    for key, src in sources.items():
        log(f"Fetching {src['label']} ...")
        try:
            if src["format"] == "geojson":
                data = fetch_geojson(src["url"])
                out_path = RAW_CURRENT / src["staged_filename"]
                with open(out_path, "w") as f:
                    json.dump(data, f)
            else:
                rows = fetch_json(src["url"])
                import csv
                out_path = RAW_CURRENT / src["staged_filename"]
                if rows:
                    with open(out_path, "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()
                        writer.writerows(rows)
            meta["sources"][key] = {"status": "ok", "rows": len(rows) if src["format"] != "geojson" else "geojson", "file": src["staged_filename"]}
            log(f"  -> saved {out_path.name}")
        except Exception as e:
            log(f"  ERROR: {e}")
            meta["sources"][key] = {"status": "error", "error": str(e)}

    write_json(RAW_METADATA / "fetch_meta.json", meta)
    log("Fetch complete.")


if __name__ == "__main__":
    main()
