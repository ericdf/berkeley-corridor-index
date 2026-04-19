"""Main pipeline orchestrator.

Run: python analysis/run_pipeline.py

Primary analysis: corridor-level model (University Ave cluster).
Secondary analysis: per-site descriptive outputs for site profile pages.

Expects staged raw data in data/raw/current/.
To refresh source data first: fetch_portal_data.py then stage_inputs.py.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import (
    # Inputs
    stage_inputs,
    geocode_calls,
    validate_inputs,
    # Corridor geography (primary)
    build_corridor_polygon,
    build_control_corridors,
    build_immediate_site_zones,
    # Corridor analysis (primary)
    compute_corridor_timeseries,
    compute_active_sites,
    compute_rolling_metrics,
    compute_indexed_comparisons,
    # Per-site descriptive (secondary)
    compute_property_local_effects,
    build_zones,
    compute_pre_post,
    compute_spillover,
    compute_rolling_yoy,
    # Export
    export_site_data,
)
from src.utils import ensure_dirs


def step(name: str, fn):
    print(f"\n[{name}]")
    t = time.time()
    result = fn()
    print(f"  done in {time.time() - t:.1f}s")
    return result


def main() -> None:
    ensure_dirs()

    # --- Inputs ---
    step("1. Stage inputs",    stage_inputs.main)
    step("2. Geocode calls",   geocode_calls.main)
    step("3. Validate inputs", validate_inputs.main)

    # --- Geography ---
    step("4. Build corridor polygon",       build_corridor_polygon.main)
    step("5. Build control corridors",      build_control_corridors.main)
    step("6. Build immediate site zones",   build_immediate_site_zones.main)
    step("7. Build legacy zone polygons",   build_zones.main)

    # --- Corridor analysis (primary) ---
    step("8. Corridor time series",         compute_corridor_timeseries.main)
    step("9. Active sites by month",        compute_active_sites.main)
    step("10. Rolling metrics",             compute_rolling_metrics.main)
    step("11. Indexed comparisons",         compute_indexed_comparisons.main)

    # --- Per-site descriptive (secondary) ---
    step("12. Property local effects",      compute_property_local_effects.main)
    step("13. Compute pre/post (site)",     compute_pre_post.main)
    step("14. Compute spillover (site)",    compute_spillover.main)
    step("15. Compute rolling YoY (site)",  compute_rolling_yoy.main)

    # --- Export ---
    step("16. Export site data",            export_site_data.main)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
