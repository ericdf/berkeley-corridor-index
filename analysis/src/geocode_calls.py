"""Geocode block-level call addresses using the Census batch geocoder.

Extracts unique Block_Address values from staged calls, submits them to the
Census Geocoding API in batches, caches results to data/interim/, then joins
coordinates back into calls_staged.parquet.

Cache is keyed by address string — re-runs only geocode new addresses.
"""

import io
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import INTERIM_DIR, ensure_dirs, log

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
BENCHMARK = "Public_AR_Current"
BATCH_SIZE = 9_000          # Census limit is 10k; stay under
CACHE_FILE = INTERIM_DIR / "address_coords_cache.parquet"
RETRY_WAIT = 5              # seconds between retries
MAX_RETRIES = 3


def load_cache() -> pd.DataFrame:
    if CACHE_FILE.exists():
        return pd.read_parquet(CACHE_FILE)
    return pd.DataFrame(columns=["block_address", "lat", "lon", "match_status"])


def save_cache(cache: pd.DataFrame) -> None:
    cache.to_parquet(CACHE_FILE, index=False)


def build_input_csv(addresses: list[tuple[int, str]]) -> str:
    """Format address list as Census batch input CSV.
    Each row: ID, street, city, state, zip
    Block addresses are already street-only; city and state are fixed.
    """
    lines = []
    for uid, addr in addresses:
        lines.append(f'{uid},"{addr}","BERKELEY","CA",""')
    return "\n".join(lines)


def parse_response(text: str) -> pd.DataFrame:
    """Parse Census batch geocoder response CSV (properly quoted)."""
    import csv
    rows = []
    reader = csv.reader(io.StringIO(text.strip()))
    for parts in reader:
        if len(parts) < 3:
            continue
        try:
            uid = int(parts[0].strip())
        except ValueError:
            continue
        status = parts[2].strip()
        coords = parts[5].strip() if len(parts) > 5 else ""
        lat, lon = None, None
        if coords and "," in coords:
            try:
                lon_str, lat_str = coords.split(",")
                lon = float(lon_str)
                lat = float(lat_str)
            except ValueError:
                pass
        rows.append({"_uid": uid, "match_status": status, "lat": lat, "lon": lon})
    return pd.DataFrame(rows)


def geocode_batch(batch: list[tuple[int, str]]) -> pd.DataFrame:
    csv_data = build_input_csv(batch)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                CENSUS_URL,
                files={"addressFile": ("addresses.csv", csv_data.encode(), "text/csv")},
                data={"benchmark": BENCHMARK},
                timeout=120,
            )
            resp.raise_for_status()
            return parse_response(resp.text)
        except Exception as e:
            log(f"  Batch attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_WAIT)
    log("  Batch failed after all retries — coordinates will be null for this batch")
    return pd.DataFrame([{"_uid": uid, "match_status": "Error", "lat": None, "lon": None}
                         for uid, _ in batch])


def main() -> None:
    ensure_dirs()

    calls = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")

    if "Block_Address" not in calls.columns:
        log("No Block_Address column found — skipping geocoding")
        return

    cache = load_cache()
    cached_addrs = set(cache["block_address"].str.upper())

    unique_addrs = calls["Block_Address"].dropna().str.upper().unique()
    to_geocode = [a for a in unique_addrs if a not in cached_addrs]
    log(f"Unique addresses: {len(unique_addrs):,} | cached: {len(cached_addrs):,} | to geocode: {len(to_geocode):,}")

    if to_geocode:
        new_rows = []
        batches = [to_geocode[i:i + BATCH_SIZE] for i in range(0, len(to_geocode), BATCH_SIZE)]
        for i, batch in enumerate(batches, 1):
            log(f"  Geocoding batch {i}/{len(batches)} ({len(batch):,} addresses)…")
            indexed = list(enumerate(batch))
            result = geocode_batch(indexed)
            addr_map = {idx: addr for idx, addr in enumerate(batch)}
            result["block_address"] = result["_uid"].map(addr_map)
            new_rows.append(result[["block_address", "lat", "lon", "match_status"]])

        new_cache = pd.concat([cache] + new_rows, ignore_index=True)
        save_cache(new_cache)
        cache = new_cache

    matched = cache[cache["lat"].notna()]
    match_rate = len(matched) / max(len(cache), 1) * 100
    log(f"Cache match rate: {match_rate:.1f}% ({len(matched):,}/{len(cache):,})")

    # Join coordinates back to calls
    coord_map = cache.set_index("block_address")[["lat", "lon"]]
    calls_upper = calls["Block_Address"].str.upper()
    calls["lat"] = calls_upper.map(coord_map["lat"])
    calls["lon"] = calls_upper.map(coord_map["lon"])

    calls = calls.dropna(subset=["lat", "lon"])
    log(f"Calls with coordinates after geocoding: {len(calls):,}")

    calls.to_parquet(INTERIM_DIR / "calls_staged.parquet", index=False)
    log("Updated calls_staged.parquet with geocoded coordinates")


if __name__ == "__main__":
    main()
