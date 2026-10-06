#!/usr/bin/env python3
"""
summarize_exclusions.py

Combine all exclusion files and output:
1. exclusions_only.csv - Only excluded runs with reasons
2. usable_subjects.csv - Subjects with usable runs and which runs are usable

Usage: python summarize_exclusions.py [exclusions_dir]
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

# Output files
OUTPUT_EXCLUSIONS = os.path.join(EXCL_DIR, "exclusions_only.csv")
OUTPUT_USABLE = os.path.join(EXCL_DIR, "usable_subjects.csv")


def load_exclusions(filepath, step_name):
    """Load an exclusion TSV and return as DataFrame with step name."""
    if not os.path.exists(filepath):
        print(f"  WARNING: {filepath} not found")
        return None
    
    df = pd.read_csv(filepath, sep="\t", dtype=str)
    df["subject_id"] = df["subject_id"].astype(str).str.strip()
    df["step"] = step_name
    return df


def is_excluded(value):
    """Check if a value indicates exclusion (1 or NA)."""
    val_str = str(value).strip()
    return val_str == "1" or val_str == "NA" or val_str == "nan" or val_str == ""


def main():
    print("Summarizing exclusions...")
    
    # Load all exclusion files
    excl_files = [
        (BIDS_EXCL, "bids"),
        (RATINGS_EXCL, "ratings"),
        (MASK_EXCL, "mask"),
        (TRIALS_EXCL, "trials"),
        (MRIQC_EXCL, "mriqc"),
    ]
    
    all_dfs = []
    for filepath, step_name in excl_files:
        df = load_exclusions(filepath, step_name)
        if df is not None:
            all_dfs.append(df)
            print(f"  Loaded {step_name}")
    
    if not all_dfs:
        print("ERROR: No exclusion files found")
        sys.exit(1)
    
    # Get all unique subjects from BIDS (primary list)
    bids_df = load_exclusions(BIDS_EXCL, "bids")
    if bids_df is None:
        print("ERROR: BIDS exclusions required")
        sys.exit(1)
    
    all_subjects = bids_df["subject_id"].unique()
    print(f"  Total subjects: {len(all_subjects)}")
    
    # --- Build exclusions list ---
    exclusion_rows = []
    
    for df in all_dfs:
        step = df["step"].iloc[0]
        
        for _, row in df.iterrows():
            subject_id = row["subject_id"]
            reason = row.get("exclusion_reason", "")
            
            # Check run 01
            if str(row["run01_excluded"]).strip() == "1":
                exclusion_rows.append({
                    "subject_id": subject_id,
                    "run": "01",
                    "step": step,
                    "reason": reason
                })
            
            # Check run 02
            if str(row["run02_excluded"]).strip() == "1":
                exclusion_rows.append({
                    "subject_id": subject_id,
                    "run": "02",
                    "step": step,
                    "reason": reason
                })
    
    df_exclusions = pd.DataFrame(exclusion_rows)
    df_exclusions = df_exclusions.sort_values(["subject_id", "run", "step"]).reset_index(drop=True)
    df_exclusions.to_csv(OUTPUT_EXCLUSIONS, index=False)
    print(f"\n  Exclusions saved: {OUTPUT_EXCLUSIONS}")
    print(f"  Total exclusion records: {len(df_exclusions)}")
    
    # --- Build usable subjects list ---
    usable_rows = []
    
    for subject_id in all_subjects:
        run01_usable = True
        run02_usable = True
        
        # Check each exclusion file
        for df in all_dfs:
            subj_row = df[df["subject_id"] == subject_id]
            if len(subj_row) == 0:
                continue
            
            row = subj_row.iloc[0]
            
            # Run 01
            if is_excluded(row["run01_excluded"]):
                run01_usable = False
            
            # Run 02
            if is_excluded(row["run02_excluded"]):
                run02_usable = False
        
        # Determine usable runs
        if run01_usable and run02_usable:
            usable_runs = "both"
        elif run01_usable:
            usable_runs = "1"
        elif run02_usable:
            usable_runs = "2"
        else:
            usable_runs = None  # Will be excluded from output
        
        if usable_runs:
            usable_rows.append({
                "subject_id": subject_id,
                "usable_runs": usable_runs
            })
    
    df_usable = pd.DataFrame(usable_rows)
    df_usable = df_usable.sort_values("subject_id").reset_index(drop=True)
    df_usable.to_csv(OUTPUT_USABLE, index=False)
    print(f"\n  Usable subjects saved: {OUTPUT_USABLE}")
    
    # --- Summary ---
    n_both = (df_usable["usable_runs"] == "both").sum()
    n_run01 = (df_usable["usable_runs"] == "1").sum()
    n_run02 = (df_usable["usable_runs"] == "2").sum()
    n_excluded = len(all_subjects) - len(df_usable)
    
    # Count exclusions by step
    step_counts = df_exclusions.groupby("step").size().to_dict()
    
    # Count unique subjects excluded by step
    step_subject_counts = df_exclusions.groupby("step")["subject_id"].nunique().to_dict()
    
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total subjects:         {len(all_subjects)}")
    print(f"Usable subjects:        {len(df_usable)}")
    print(f"  Both runs:            {n_both}")
    print(f"  Run 1 only:           {n_run01}")
    print(f"  Run 2 only:           {n_run02}")
    print(f"Fully excluded:         {n_excluded}")
    print()
    print("Exclusions by step (runs / subjects):")
    for step in ["bids", "ratings", "mask", "trials", "mriqc"]:
        runs = step_counts.get(step, 0)
        subs = step_subject_counts.get(step, 0)
        print(f"  {step:12s}:  {runs:3d} runs  /  {subs:3d} subjects")
    print("=" * 50)


if __name__ == "__main__":
    main()
