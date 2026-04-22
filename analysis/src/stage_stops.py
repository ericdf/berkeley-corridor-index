"""Stage RIPA stop data from two formats into a single normalized parquet.

Old format: RIPAData.csv (Oct 2020 – Mar 2024)
New format: Berkeley_PD_Stop_Data_2024-Current.csv (Jan 2024 – present)

Overlap period (Jan–Mar 2024) is deduplicated by preferring the new format.
One row per person-stop (PersonNum is a within-stop person counter).

Key output fields:
  stop_id            — original LEA record ID
  person_num         — person number within stop (1 = first/only)
  stop_datetime      — normalized datetime
  is_pedestrian      — True for pedestrian stops, False for vehicular
  lat, lon
  city_of_residence
  perceived_unhoused — True/False/None (None = old format, field not collected)
  basis_of_suspicion
  result_of_stop
  actions_taken
  source             — 'old' or 'new'
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.utils import INTERIM_DIR, RAW_CURRENT, ensure_dirs, log


def stage_old() -> pd.DataFrame:
    path = RAW_CURRENT / "RIPAData.csv"
    df = pd.read_csv(path, low_memory=False)
    log(f"Old format: {len(df):,} rows")

    df["stop_datetime"] = pd.to_datetime(df["DateTimeOfStop"], errors="coerce")
    df["is_pedestrian"] = df["TypeOfStop"].str.lower().str.contains("pedestrian", na=False)
    df["perceived_unhoused"] = None

    return pd.DataFrame({
        "stop_id":             df["LEA_RecordID"].astype(str),
        "person_num":          df["PersonNum"],
        "stop_datetime":       df["stop_datetime"],
        "is_pedestrian":       df["is_pedestrian"],
        "lat":                 pd.to_numeric(df["Latitude"], errors="coerce"),
        "lon":                 pd.to_numeric(df["Longitude"], errors="coerce"),
        "city_of_residence":   df["CityOfResidence"].str.strip().str.upper(),
        "perceived_unhoused":  df["perceived_unhoused"],
        "basis_of_suspicion":  df["BasisOfSuspicion"].fillna("").str.strip(),
        "result_of_stop":      df["ResultOfStop"].fillna("").str.strip(),
        "actions_taken":       df["ActionsTaken"].fillna("").str.strip(),
        "offense_raw":         df["SuspectedViolation"].fillna("").str.strip(),
        "source":              "old",
    })


def stage_new() -> pd.DataFrame:
    path = RAW_CURRENT / "Berkeley_PD_Stop_Data_2024-Current.csv"
    df = pd.read_csv(path, low_memory=False)
    log(f"New format: {len(df):,} rows")

    df["stop_datetime"] = pd.to_datetime(
        df["StopDate"].astype(str) + " " + df["StopTime"].astype(str),
        errors="coerce"
    )
    df["is_pedestrian"] = df["TypeOfStopDesc"].str.lower().str.contains("pedestrian", na=False)
    df["perceived_unhoused"] = df["PerceivedPersonUnhoused"].map({"Y": True, "N": False})

    actions = df["NonForceActionsTaken"].fillna("") + "|" + df["ForceActionsTaken"].fillna("")

    # Best available offense: custodial arrest > in-field cite > written warning > verbal warning
    offense = (
        df["CustodialArrestNoWarrantOffense"].fillna("")
        .where(df["CustodialArrestNoWarrantOffense"].notna(), df["InfieldCiteRelOffense"].fillna(""))
        .where(df["InfieldCiteRelOffense"].notna() | df["CustodialArrestNoWarrantOffense"].notna(),
               df["WrittenWarningOffense"].fillna(""))
        .where(df["WrittenWarningOffense"].notna() | df["InfieldCiteRelOffense"].notna() | df["CustodialArrestNoWarrantOffense"].notna(),
               df["VerbalWarningOffense"].fillna(""))
    )

    return pd.DataFrame({
        "stop_id":             df["LEA_Record_ID"].astype(str),
        "person_num":          df["PersonNum"],
        "stop_datetime":       df["stop_datetime"],
        "is_pedestrian":       df["is_pedestrian"],
        "lat":                 pd.to_numeric(df["Latitude"], errors="coerce"),
        "lon":                 pd.to_numeric(df["Longitude"], errors="coerce"),
        "city_of_residence":   df["CityOfResidence"].str.strip().str.upper(),
        "perceived_unhoused":  df["perceived_unhoused"],
        "basis_of_suspicion":  df["BasisOfSuspicion"].fillna("").str.strip(),
        "result_of_stop":      df["ResultOfStop"].fillna("").str.strip(),
        "actions_taken":       actions.str.strip("|"),
        "offense_raw":         offense.str.strip(),
        "source":              "new",
    })


def main() -> pd.DataFrame:
    ensure_dirs()

    old = stage_old()
    new = stage_new()

    # Remove overlap: drop old-format rows from Jan 2024 onward
    old = old[old["stop_datetime"] < pd.Timestamp("2024-01-01")]
    log(f"Old format after overlap trim: {len(old):,} rows")

    combined = pd.concat([old, new], ignore_index=True)
    combined = combined.dropna(subset=["stop_datetime", "lat", "lon"])
    combined = combined.sort_values("stop_datetime").reset_index(drop=True)

    ped = combined["is_pedestrian"].sum()
    veh = (~combined["is_pedestrian"]).sum()
    unhoused = combined["perceived_unhoused"].sum()
    log(f"Combined: {len(combined):,} stops  "
        f"({ped:,} pedestrian, {veh:,} vehicular, {int(unhoused):,} perceived unhoused)")
    log(f"Date range: {combined['stop_datetime'].min().date()} – {combined['stop_datetime'].max().date()}")

    combined.to_parquet(INTERIM_DIR / "stops_staged.parquet", index=False)
    log("Wrote stops_staged.parquet")
    return combined


if __name__ == "__main__":
    main()
