"""Shared utilities for the motel conversions analysis pipeline."""

import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = ROOT / "analysis"
CONFIG_DIR = ANALYSIS_DIR / "config"
DATA_DIR = ROOT / "data"
RAW_CURRENT = DATA_DIR / "raw" / "current"
RAW_SNAPSHOTS = DATA_DIR / "raw" / "source_snapshots"
RAW_METADATA = DATA_DIR / "raw" / "metadata"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
CHARTS_DIR = PROCESSED_DIR / "charts"
MAPS_DIR = PROCESSED_DIR / "maps"
DOWNLOADS_DIR = PROCESSED_DIR / "downloads"
METADATA_DIR = PROCESSED_DIR / "metadata"


def load_config(filename: str) -> dict:
    with open(CONFIG_DIR / filename) as f:
        return yaml.safe_load(f)


def load_sites() -> list[dict]:
    return load_config("sites.yml")["sites"]


def load_study_params() -> dict:
    return load_config("study_parameters.yml")


def load_data_sources() -> dict:
    return load_config("data_sources.yml")["sources"]


def ensure_dirs() -> None:
    for d in [
        RAW_CURRENT, RAW_SNAPSHOTS, RAW_METADATA,
        INTERIM_DIR, CHARTS_DIR, MAPS_DIR, DOWNLOADS_DIR, METADATA_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def log(msg: str) -> None:
    print(f"  {msg}")
