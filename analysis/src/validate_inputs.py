"""Validate staged inputs before running analysis."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import INTERIM_DIR, log


REQUIRED_COLS = {"event_date", "lat", "lon", "call_type", "is_non_traffic"}


def validate_calls(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in staged calls: {missing}")
    null_geo = df[["lat", "lon"]].isna().any(axis=1).sum()
    if null_geo > 0:
        log(f"Warning: {null_geo} rows have null lat/lon (will be excluded from spatial joins)")
    null_date = df["event_date"].isna().sum()
    if null_date > 0:
        log(f"Warning: {null_date} rows have null event_date")
    date_range = f"{df['event_date'].min().date()} to {df['event_date'].max().date()}"
    log(f"Calls date range: {date_range}")
    log(f"Calls validated: {len(df):,} rows")


def main() -> pd.DataFrame:
    path = INTERIM_DIR / "calls_staged.parquet"
    if not path.exists():
        raise FileNotFoundError("Staged calls not found. Run stage_inputs.py first.")
    df = pd.read_parquet(path)
    validate_calls(df)
    return df


if __name__ == "__main__":
    main()
