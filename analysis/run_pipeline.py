"""Main pipeline orchestrator.

Run: python analysis/run_pipeline.py

Expects staged raw data in data/raw/current/.
To refresh source data first, run fetch_portal_data.py and stage_inputs.py.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import (
    build_zones,
    compute_controls,
    compute_pre_post,
    compute_rolling_yoy,
    compute_spillover,
    export_site_data,
    geocode_calls,
    stage_inputs,
    validate_inputs,
)
from src.utils import ensure_dirs, log


def step(name: str, fn):
    print(f"\n[{name}]")
    t = time.time()
    result = fn()
    print(f"  done in {time.time() - t:.1f}s")
    return result


def main() -> None:
    ensure_dirs()

    step("1. Stage inputs", stage_inputs.main)
    step("2. Geocode calls", geocode_calls.main)
    step("3. Validate inputs", validate_inputs.main)
    step("4. Build zones", build_zones.main)
    step("5. Compute pre/post", compute_pre_post.main)
    step("6. Compute spillover", compute_spillover.main)
    step("7. Compute rolling YoY", compute_rolling_yoy.main)
    step("8. Compute controls", compute_controls.main)
    step("9. Export site data", export_site_data.main)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
