"""Main pipeline orchestrator.

Run: python analysis/run_pipeline.py

Primary analysis: two independent treatment geographies —
  University core cluster (1461, 1619, 1761 University Ave)
  San Pablo node (1620 San Pablo Ave)

Secondary outputs: per-site descriptive data for site profile pages.

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
    # Geography — primary
    build_university_cluster,
    build_san_pablo_node,
    build_combined_corridor,
    # Geography — secondary / site-level
    build_immediate_site_zones,
    build_zones,
    build_control_corridors,
    # Cluster-level analysis
    compute_cluster_monthly,
    compute_corridor_timeseries,   # legacy alias: copies university cluster outputs
    compute_active_sites,
    compute_rolling_metrics,
    compute_indexed_comparisons,
    compute_concentration,
    # Per-site descriptive
    compute_property_local_effects,
    compute_pre_post,
    compute_spillover,
    compute_rolling_yoy,
    compute_data_sufficiency,
    compute_citywide_benchmark,
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

    # --- Primary geographies ---
    step("4. Build University core cluster",    build_university_cluster.main)
    step("5. Build San Pablo node",             build_san_pablo_node.main)
    step("6. Build combined corridor (appendix)", build_combined_corridor.main)

    # --- Secondary geographies ---
    step("7. Build control corridors",          build_control_corridors.main)
    step("8. Build immediate site zones",       build_immediate_site_zones.main)
    step("9. Build legacy zone polygons",       build_zones.main)

    # --- Cluster-level analysis ---
    step("10. Cluster monthly time series",     compute_cluster_monthly.main)
    step("11. Legacy corridor alias",           compute_corridor_timeseries.main)
    step("12. Active sites by month",           compute_active_sites.main)
    step("13. Rolling metrics",                 compute_rolling_metrics.main)
    step("14. Indexed comparisons",             compute_indexed_comparisons.main)
    step("15. Concentration metrics",           compute_concentration.main)

    # --- Per-site descriptive ---
    step("16. Property local effects",          compute_property_local_effects.main)
    step("17. Compute pre/post (site)",         compute_pre_post.main)
    step("18. Compute spillover (site)",        compute_spillover.main)
    step("19. Compute rolling YoY (site)",      compute_rolling_yoy.main)
    step("20. Data sufficiency flags",          compute_data_sufficiency.main)
    step("21. Citywide benchmark",              compute_citywide_benchmark.main)

    # --- Export ---
    step("22. Export site data",               export_site_data.main)

    print("\nPipeline complete. (22 steps)")


if __name__ == "__main__":
    main()
