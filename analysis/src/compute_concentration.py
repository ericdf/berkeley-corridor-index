"""Compute call concentration metrics within immediate site zones.

Answers: what share of calls occur within 100m of each site?
Did that share change after openings? Are sites hotspots?

Outputs:
  concentration_share.csv   — overall and per-site share, pre vs post
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dateutil.relativedelta import relativedelta
from shapely.geometry import Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import CHARTS_DIR, INTERIM_DIR, MAPS_DIR, ensure_dirs, load_sites, load_study_params, log

CRS_GEO = "EPSG:4326"
CRS_PROJ = "EPSG:32610"


def calls_in_poly(calls_gdf: gpd.GeoDataFrame, poly) -> gpd.GeoDataFrame:
    return calls_gdf[calls_gdf.geometry.within(poly)]


def main() -> pd.DataFrame:
    ensure_dirs()
    sites = load_sites()
    params = load_study_params()
    radius_m = params["immediate_zone_m"]
    window = params["pre_post_window_months"]

    df = pd.read_parquet(INTERIM_DIR / "calls_staged.parquet")
    df_nt = df[df["is_non_traffic"]].copy()
    geometry = gpd.points_from_xy(df_nt["lon"], df_nt["lat"])
    calls_gdf = gpd.GeoDataFrame(df_nt, geometry=geometry, crs=CRS_GEO).to_crs(CRS_PROJ)

    # Build per-site 100m zone polys
    site_zones = {}
    for s in sites:
        pt = gpd.GeoDataFrame(geometry=[Point(s["lon"], s["lat"])], crs=CRS_GEO).to_crs(CRS_PROJ)
        site_zones[s["id"]] = (s, pt.geometry.buffer(radius_m).iloc[0])

    # Two reference totals:
    #   total_all = all geocoded non-traffic calls (citywide context)
    #   total_cluster = calls within the university core + san pablo polygons combined
    #     (the meaningful denominator for "share of study-area calls")
    total_all = len(calls_gdf)

    core_gdf = gpd.read_file(MAPS_DIR / "university_core_cluster.geojson").to_crs(CRS_PROJ)
    sp_gdf = gpd.read_file(MAPS_DIR / "san_pablo_node.geojson").to_crs(CRS_PROJ)
    study_area_poly = unary_union([core_gdf.geometry.iloc[0], sp_gdf.geometry.iloc[0]])
    total_study = len(calls_in_poly(calls_gdf, study_area_poly))

    rows = []
    all_zone_polys = [poly for _, poly in site_zones.values()]
    union_poly = unary_union(all_zone_polys)

    # Overall concentration — two denominators
    in_any_zone = calls_in_poly(calls_gdf, union_poly)
    rows.append({
        "site_id": "all_sites",
        "address": "All site zones combined",
        "period": "all",
        "calls_in_zone": len(in_any_zone),
        "calls_total_citywide": total_all,
        "calls_total_study_area": total_study,
        "share_of_citywide_pct": round(len(in_any_zone) / total_all * 100, 2) if total_all else None,
        "share_of_study_area_pct": round(len(in_any_zone) / total_study * 100, 2) if total_study else None,
        "zone_area_m2": round(union_poly.area),
    })

    # Per-site, all time + pre/post split
    for sid, (site, zone_poly) in site_zones.items():
        opening = pd.Timestamp(site["opening_date"])
        pre_start = opening - relativedelta(months=window)
        post_end = opening + relativedelta(months=window)
        data_max = calls_gdf["event_date"].max()

        in_zone_all = calls_in_poly(calls_gdf, zone_poly)

        pre_mask = (calls_gdf["event_date"] >= pre_start) & (calls_gdf["event_date"] < opening)
        post_mask = (calls_gdf["event_date"] >= opening) & (calls_gdf["event_date"] < min(data_max, post_end))

        pre_all = calls_gdf[pre_mask]
        post_all = calls_gdf[post_mask]
        pre_zone = calls_in_poly(calls_gdf[pre_mask], zone_poly)
        post_zone = calls_in_poly(calls_gdf[post_mask], zone_poly)

        area_m2 = round(zone_poly.area)

        rows.append({
            "site_id": sid,
            "address": site["address"],
            "period": "all",
            "calls_in_zone": len(in_zone_all),
            "calls_total_citywide": total_all,
            "calls_total_study_area": total_study,
            "share_of_citywide_pct": round(len(in_zone_all) / total_all * 100, 2) if total_all else None,
            "share_of_study_area_pct": round(len(in_zone_all) / total_study * 100, 2) if total_study else None,
            "zone_area_m2": area_m2,
        })
        rows.append({
            "site_id": sid,
            "address": site["address"],
            "period": "pre",
            "calls_in_zone": len(pre_zone),
            "calls_total_citywide": len(pre_all),
            "calls_total_study_area": None,
            "share_of_citywide_pct": round(len(pre_zone) / len(pre_all) * 100, 2) if len(pre_all) else None,
            "share_of_study_area_pct": None,
            "zone_area_m2": area_m2,
        })
        rows.append({
            "site_id": sid,
            "address": site["address"],
            "period": "post",
            "calls_in_zone": len(post_zone),
            "calls_total_citywide": len(post_all),
            "calls_total_study_area": None,
            "share_of_citywide_pct": round(len(post_zone) / len(post_all) * 100, 2) if len(post_all) else None,
            "share_of_study_area_pct": None,
            "zone_area_m2": area_m2,
        })

    result = pd.DataFrame(rows)
    result.to_csv(CHARTS_DIR / "concentration_share.csv", index=False)
    log(f"Concentration share written ({len(result)} rows)")

    # Summary for operator
    overall = result[(result["site_id"] == "all_sites") & (result["period"] == "all")].iloc[0]
    log(f"All 100m zones: {overall['calls_in_zone']:,} of {overall['calls_total_study_area']:,} study-area calls = {overall['share_of_study_area_pct']:.1f}% (of citywide {overall['calls_total_citywide']:,}: {overall['share_of_citywide_pct']:.1f}%)")

    return result


if __name__ == "__main__":
    main()
