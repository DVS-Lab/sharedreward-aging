#!/usr/bin/env python3
"""
check_trials_exclusions.py

Check for excessive missed trials and flag runs with >25% missing.
Only checks runs that passed BIDS exclusions.

Usage: python check_trials_exclusions.py [bids_exclusions] [output_tsv] [detailed_csv]

Output:
  - Main TSV: subject_id, run01_excluded, run02_excluded, exclusion_reason
  - Detailed CSV: All EV file counts for debugging
"""

import os
import sys
import glob
import pandas as pd
from collections import defaultdict

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
EV_DIR = f"{BASE_DIR}/derivatives/fsl/EVfiles"
EXCLUSION_THRESHOLD = 0.25  # Exclude if missed trials > 25% of total

# --- Input/Output ---
BIDS_EXCL = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/exclusions/bids_exclusions.tsv"
OUTPUT_TSV = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/trials_exclusions.tsv"
DETAILED_CSV = sys.argv[3] if len(sys.argv) > 3 else f"{BASE_DIR}/code/exclusions/trials_exclusions_detailed.csv"

# Create output directory if needed
os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)


def count_file_rows(filepath):
    """Count non-empty lines in a file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r') as f:
        return sum(1 for line in f if line.strip())


def process_run(subject_id, run_num):
    """
    Process a single run's EV files.
    Only counts files matching run-{run}_event_*.txt
    
    Returns:
        dict with: total_rows, missed_trials, ev_counts, pct_missed
    """
    # Determine run format and session path based on subject ID length
    if len(subject_id) == 3:
        run_fmt = f"{int(run_num):02d}"
        subject_dir = os.path.join(EV_DIR, f"sub-{subject_id}", "sharedreward")
    else:
        run_fmt = str(run_num)
        subject_dir = os.path.join(EV_DIR, f"sub-{subject_id}", "ses-01", "sharedreward")
    
    result = {"total_rows": 0, "missed_trials": 0, "ev_counts": {}, "pct_missed": None}
    
    if not os.path.exists(subject_dir):
        return result
    
    # Find only event files: run-{run}_event_*.txt
    event_pattern = os.path.join(subject_dir, f"run-{run_fmt}_event_*.txt")
    event_files = glob.glob(event_pattern)
    
    # Find missed trial file
    missed_pattern = os.path.join(subject_dir, f"run-{run_fmt}_missed_trial.txt")
    missed_files = glob.glob(missed_pattern)
    
    # Count rows in event files
    for filepath in event_files:
        filename = os.path.basename(filepath)
        row_count = count_file_rows(filepath)
        
        # Clean filename for column naming
        clean_name = filename.replace(f"run-{run_fmt}_", "").replace(".txt", "")
        
        result["total_rows"] += row_count
        result["ev_counts"][clean_name] = row_count
    
    # Count missed trials
    for filepath in missed_files:
        result["missed_trials"] = count_file_rows(filepath)
    
    # Calculate percentage missed
    # Include missed trials in total count
    total_trials = result["total_rows"] + result["missed_trials"]

    if total_trials > 0:
        result["pct_missed"] = (result["missed_trials"] / total_trials) * 100
        result["total_rows"] = total_trials  # redefine total as all trials
    
    return result


def main():
    print("Checking for missing trials...")
    
    # Load BIDS exclusions
    if not os.path.exists(BIDS_EXCL):
        print(f"ERROR: BIDS exclusions file not found: {BIDS_EXCL}")
        sys.exit(1)
    
    bids_df = pd.read_csv(BIDS_EXCL, sep="\t", dtype={"subject_id": str})
    print(f"  Loaded {len(bids_df)} subjects from BIDS exclusions")
    
    # Process each subject/run
    detailed_rows = []
    exclusion_rows = []
    
    for _, row in bids_df.iterrows():
        subject_id = str(row["subject_id"])
        bids_run01 = row["run01_excluded"]
        bids_run02 = row["run02_excluded"]
        
        run01_excl = "NA"
        run02_excl = "NA"
        reasons = []
        
        # Process run 01
        if bids_run01 == 0:
            run01_data = process_run(subject_id, 1)
            detailed_rows.append({
                "subject_id": subject_id,
                "run": "01",
                "total_ev_rows": run01_data["total_rows"],
                "missed_trials": run01_data["missed_trials"],
                "pct_missed": run01_data["pct_missed"],
                "bids_excluded": False,
                **run01_data["ev_counts"]
            })
            
            if run01_data["pct_missed"] is not None:
                if run01_data["pct_missed"] > (EXCLUSION_THRESHOLD * 100):
                    run01_excl = 1
                    reasons.append("run01_excess_missed_trials")
                else:
                    run01_excl = 0
        else:
            detailed_rows.append({
                "subject_id": subject_id,
                "run": "01",
                "total_ev_rows": None,
                "missed_trials": None,
                "pct_missed": None,
                "bids_excluded": True
            })
        
        # Process run 02
        if bids_run02 == 0:
            run02_data = process_run(subject_id, 2)
            detailed_rows.append({
                "subject_id": subject_id,
                "run": "02",
                "total_ev_rows": run02_data["total_rows"],
                "missed_trials": run02_data["missed_trials"],
                "pct_missed": run02_data["pct_missed"],
                "bids_excluded": False,
                **run02_data["ev_counts"]
            })
            
            if run02_data["pct_missed"] is not None:
                if run02_data["pct_missed"] > (EXCLUSION_THRESHOLD * 100):
                    run02_excl = 1
                    reasons.append("run02_excess_missed_trials")
                else:
                    run02_excl = 0
        else:
            detailed_rows.append({
                "subject_id": subject_id,
                "run": "02",
                "total_ev_rows": None,
                "missed_trials": None,
                "pct_missed": None,
                "bids_excluded": True
            })
        
        exclusion_rows.append({
            "subject_id": subject_id,
            "run01_excluded": run01_excl,
            "run02_excluded": run02_excl,
            "exclusion_reason": ";".join(reasons)
        })
    
    # Save detailed CSV
    df_detailed = pd.DataFrame(detailed_rows)
    fixed_cols = ["subject_id", "run", "total_ev_rows", "missed_trials", "pct_missed", "bids_excluded"]
    ev_cols = sorted([c for c in df_detailed.columns if c not in fixed_cols])
    df_detailed = df_detailed.reindex(columns=fixed_cols + ev_cols)
    df_detailed.to_csv(DETAILED_CSV, index=False)
    print(f"  Detailed output: {DETAILED_CSV}")
    
    # Save exclusions TSV
    df_exclusions = pd.DataFrame(exclusion_rows).sort_values("subject_id").reset_index(drop=True)
    df_exclusions.to_csv(OUTPUT_TSV, sep="\t", index=False)
    
    # Summary
    n_subjects = len(df_exclusions)
    n_run01_excluded = (df_exclusions["run01_excluded"] == 1).sum()
    n_run02_excluded = (df_exclusions["run02_excluded"] == 1).sum()
    n_both_excluded = ((df_exclusions["run01_excluded"] == 1) & (df_exclusions["run02_excluded"] == 1)).sum()
    n_skipped = (df_exclusions["run01_excluded"] == "NA").sum()
    
    print()
    print("Trials exclusion check complete")
    print(f"  Output: {OUTPUT_TSV}")
    print(f"  Total subjects: {n_subjects}")
    print(f"  Skipped (prior exclusions): {n_skipped}")
    print(f"  Run 01 excluded: {n_run01_excluded}")
    print(f"  Run 02 excluded: {n_run02_excluded}")
    print(f"  Both runs excluded: {n_both_excluded}")


if __name__ == "__main__":
    main()
