#!/usr/bin/env python3
"""
combine_exclusions.py

Combine all exclusion files into a single master exclusion sheet.

Keeps:
  - Run-level exclusion flags for each step
  - usable_runs column
  - all_reasons column (collapsed)

Usage: python combine_exclusions.py [exclusions_dir]

Output: final_exclusions.tsv
"""

import os
import sys
import pandas as pd

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
EXCL_DIR = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/exclusions"

# Input files
RATINGS_EXCL = os.path.join(EXCL_DIR, "ratings_exclusions.tsv")
BIDS_EXCL = os.path.join(EXCL_DIR, "bids_exclusions.tsv")
MASK_EXCL = os.path.join(EXCL_DIR, "mask_exclusions.tsv")
TRIALS_EXCL = os.path.join(EXCL_DIR, "trials_exclusions.tsv")
MRIQC_EXCL = os.path.join(EXCL_DIR, "mriqc_exclusions.tsv")

# Output
OUTPUT_FILE = os.path.join(EXCL_DIR, "final_exclusions.tsv")


def load_exclusions(filepath, prefix):
    """Load an exclusion TSV and rename run columns with prefix."""
    if not os.path.exists(filepath):
        print(f"  WARNING: {filepath} not found")
        return None

    df = pd.read_csv(filepath, sep="\t", dtype=str)
    df["subject_id"] = df["subject_id"].astype(str).str.strip()

    rename_map = {
        "run01_excluded": f"{prefix}_run01",
        "run02_excluded": f"{prefix}_run02",
        "exclusion_reason": f"{prefix}_reason",
    }
    df = df.rename(columns=rename_map)

    return df


def is_excluded(value):
    """Return True if value indicates exclusion."""
    val = str(value).strip()
    return val in ["1", "NA", "nan", ""]


def determine_usable_runs(row, step_order):
    """Determine final usable run status."""
    run01_ok = True
    run02_ok = True

    for step in step_order:
        col01 = f"{step}_run01"
        col02 = f"{step}_run02"

        if col01 in row.index and is_excluded(row[col01]):
            run01_ok = False
        if col02 in row.index and is_excluded(row[col02]):
            run02_ok = False

    if run01_ok and run02_ok:
        return "both"
    elif run01_ok:
        return "run01_only"
    elif run02_ok:
        return "run02_only"
    else:
        return "both_excluded"


def collect_all_reasons(row, step_order):
    """Collapse all step-level reasons into one column."""
    reasons = []
    for step in step_order:
        col = f"{step}_reason"
        if col in row.index:
            val = str(row[col]).strip()
            if val and val != "nan":
                reasons.append(val)
    return "; ".join(reasons)


def main():
    print("Combining exclusion files...")

    # Load files
    ratings_df = load_exclusions(RATINGS_EXCL, "ratings")
    bids_df = load_exclusions(BIDS_EXCL, "bids")
    mask_df = load_exclusions(MASK_EXCL, "mask")
    trials_df = load_exclusions(TRIALS_EXCL, "trials")
    mriqc_df = load_exclusions(MRIQC_EXCL, "mriqc")

    if bids_df is None:
        print("ERROR: BIDS exclusions file is required as base.")
        sys.exit(1)

    combined = bids_df.copy()
    print(f"  Loaded {len(combined)} subjects from BIDS")

    # Merge remaining steps
    for df in [ratings_df, mask_df, trials_df, mriqc_df]:
        if df is not None:
            combined = combined.merge(df, on="subject_id", how="left")

    step_order = ["bids", "ratings", "mask", "trials", "mriqc"]

    # Fill missing run flags as NA
    for col in combined.columns:
        if col.endswith("_run01") or col.endswith("_run02"):
            combined[col] = combined[col].fillna("NA")

    # Create all_reasons BEFORE dropping step-specific reason columns
    combined["all_reasons"] = combined.apply(
        lambda row: collect_all_reasons(row, step_order), axis=1
    )

    # Determine usable runs
    combined["usable_runs"] = combined.apply(
        lambda row: determine_usable_runs(row, step_order), axis=1
    )

    # Drop step-specific reason columns
    combined = combined.drop(
        columns=[c for c in combined.columns if c.endswith("_reason")]
    )

    # Reorder columns cleanly
    run_cols = ["subject_id"]
    for step in step_order:
        for suffix in ["_run01", "_run02"]:
            col = f"{step}{suffix}"
            if col in combined.columns:
                run_cols.append(col)

    run_cols += ["usable_runs", "all_reasons"]
    combined = combined[run_cols]

    # Sort by subject
    combined = combined.sort_values("subject_id").reset_index(drop=True)

    # Save
    combined.to_csv(OUTPUT_FILE, sep="\t", index=False)

    # ---- Simple Summary ----
    n = len(combined)
    n_both = (combined["usable_runs"] == "both").sum()
    n_run01_only = (combined["usable_runs"] == "run01_only").sum()
    n_run02_only = (combined["usable_runs"] == "run02_only").sum()
    n_both_excluded = (combined["usable_runs"] == "both_excluded").sum()
    n_any = n_both + n_run01_only + n_run02_only

    print("\nFINAL SUMMARY")
    print("-" * 40)
    print(f"Total subjects: {n}")
    print(f"Both runs usable: {n_both}")
    print(f"Run01 only:       {n_run01_only}")
    print(f"Run02 only:       {n_run02_only}")
    print(f"Both excluded:    {n_both_excluded}")
    print(f"Any usable data:  {n_any}")
    print("-" * 40)
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

