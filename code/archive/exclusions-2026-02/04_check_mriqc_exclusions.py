#!/usr/bin/env python3
"""
check_mriqc_exclusions.py

Extract tSNR and FD metrics from MRIQC and apply IQR-based exclusions.
Runs independently (checks all subjects in sublist).

Applies: IQR exclusion on fd_mean (high end) and tSNR (low end)

Usage: python check_mriqc_exclusions.py [sublist] [output_tsv] [metrics_tsv]

Output:
  - mriqc_exclusions.tsv: Wide format with exclusion flags
  - mriqc_metrics.tsv: Run-level metrics for reference
"""

import os
import sys
import json
import glob
import numpy as np
import pandas as pd

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
MRIQC_DIR = f"{BASE_DIR}/derivatives/mriqc"
IQR_MULTIPLIER = 1.5

# --- Input/Output ---
SUBLIST = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/sublist-all.txt"
OUTPUT_TSV = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/mriqc_exclusions.tsv"
METRICS_TSV = sys.argv[3] if len(sys.argv) > 3 else f"{BASE_DIR}/code/exclusions/mriqc_metrics.tsv"

os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)


def get_mriqc_json(subject_id, run):
    """Find and return path to MRIQC JSON for a subject/run."""
    if len(subject_id) == 5:
        # 5-digit subject format
        pattern = f"{MRIQC_DIR}/sub-{subject_id}/ses-01/func/sub-{subject_id}_ses-01_task-sharedreward_run-{run}_echo-2_part-mag_bold.json"
    elif len(subject_id) == 3:
        # 3-digit subject format (run is zero-padded)
        run_fmt = f"{int(run):02d}"
        pattern = f"{MRIQC_DIR}/sub-{subject_id}/func/sub-{subject_id}_task-sharedreward_run-{run_fmt}_bold.json"
    else:
        return None
    
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def extract_metrics(json_path):
    """Extract tSNR and fd_mean from MRIQC JSON."""
    if json_path is None or not os.path.exists(json_path):
        return None, None
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        tsnr = data.get('tsnr')
        fd_mean = data.get('fd_mean')
        return tsnr, fd_mean
    except Exception as e:
        print(f"WARNING: Error reading {json_path}: {e}")
        return None, None


def calculate_iqr_thresholds(values, direction="low"):
    """
    Calculate IQR threshold for outlier detection.
    
    direction: "low" for tSNR (exclude below Q1 - 1.5*IQR)
               "high" for fd_mean (exclude above Q3 + 1.5*IQR)
    """
    values = np.array([v for v in values if v is not None and not np.isnan(v)])
    if len(values) < 4:
        return None, None, None, None
    
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    
    if direction == "low":
        threshold = q1 - (IQR_MULTIPLIER * iqr)
    else:  # high
        threshold = q3 + (IQR_MULTIPLIER * iqr)
    
    return threshold, q1, q3, iqr


def main():
    print("Extracting MRIQC metrics...")
    
    # Read subject list
    with open(SUBLIST, 'r') as f:
        subjects = [line.strip().replace('sub-', '') for line in f if line.strip() and not line.startswith('#')]
    
    print(f"  Checking {len(subjects)} subjects from {SUBLIST}")
    
    # Collect run-level data
    run_data = []
    
    for subject_id in subjects:
        for run_num in ["1", "2"]:
            run_fmt = f"{int(run_num):02d}"
            
            json_path = get_mriqc_json(subject_id, run_num)
            tsnr, fd_mean = extract_metrics(json_path)
            
            run_data.append({
                "subject_id": subject_id,
                "run": run_fmt,
                "tsnr": tsnr,
                "fd_mean": fd_mean,
                "json_found": json_path is not None
            })
    
    df_runs = pd.DataFrame(run_data)
    
    # Count how many JSONs were found
    n_found = df_runs["json_found"].sum()
    print(f"  Found MRIQC data for {n_found} of {len(df_runs)} subject-runs")
    
    # --- Calculate IQR thresholds ---
    valid_tsnr = df_runs.loc[df_runs["tsnr"].notna(), "tsnr"].tolist()
    valid_fd = df_runs.loc[df_runs["fd_mean"].notna(), "fd_mean"].tolist()
    
    print("\nCalculating IQR thresholds...")
    
    tsnr_threshold, tsnr_q1, tsnr_q3, tsnr_iqr = calculate_iqr_thresholds(valid_tsnr, direction="low")
    fd_threshold, fd_q1, fd_q3, fd_iqr = calculate_iqr_thresholds(valid_fd, direction="high")
    
    if tsnr_threshold is not None:
        print(f"  tSNR: Q1={tsnr_q1:.2f}, Q3={tsnr_q3:.2f}, IQR={tsnr_iqr:.2f}, threshold={tsnr_threshold:.2f} (exclude below)")
    else:
        print("  tSNR: Not enough data for IQR calculation")
    
    if fd_threshold is not None:
        print(f"  fd_mean: Q1={fd_q1:.4f}, Q3={fd_q3:.4f}, IQR={fd_iqr:.4f}, threshold={fd_threshold:.4f} (exclude above)")
    else:
        print("  fd_mean: Not enough data for IQR calculation")
    
    # --- Apply IQR exclusions ---
    df_runs["tsnr_excluded"] = False
    df_runs["fd_excluded"] = False
    
    if tsnr_threshold is not None:
        df_runs.loc[df_runs["tsnr"].notna() & (df_runs["tsnr"] < tsnr_threshold), "tsnr_excluded"] = True
    
    if fd_threshold is not None:
        df_runs.loc[df_runs["fd_mean"].notna() & (df_runs["fd_mean"] > fd_threshold), "fd_excluded"] = True
    
    # Build exclusion reason per run
    def get_reason(row):
        reasons = []
        if row["tsnr_excluded"]:
            reasons.append("low_tsnr")
        if row["fd_excluded"]:
            reasons.append("high_fd")
        return ";".join(reasons)
    
    df_runs["exclusion_reason"] = df_runs.apply(get_reason, axis=1)
    df_runs["excluded"] = df_runs["tsnr_excluded"] | df_runs["fd_excluded"]
    
    # --- Output 1: Run-level metrics ---
    df_metrics = df_runs[["subject_id", "run", "tsnr", "fd_mean", "tsnr_excluded", "fd_excluded", "excluded", "exclusion_reason"]]
    df_metrics.to_csv(METRICS_TSV, sep="\t", index=False)
    print(f"\nRun-level metrics: {METRICS_TSV}")
    
    # --- Output 2: Wide-format exclusions TSV ---
    exclusion_rows = []
    
    for subject_id in subjects:
        subj_data = df_runs[df_runs["subject_id"] == subject_id]
        
        run01 = subj_data[subj_data["run"] == "01"]
        run02 = subj_data[subj_data["run"] == "02"]
        
        reasons = []
        
        # Run 01
        if len(run01) > 0 and pd.notna(run01.iloc[0]["tsnr"]):
            if run01.iloc[0]["excluded"]:
                run01_excl = 1
                if run01.iloc[0]["exclusion_reason"]:
                    reasons.append(f"run01_{run01.iloc[0]['exclusion_reason']}")
            else:
                run01_excl = 0
        else:
            run01_excl = "NA"
        
        # Run 02
        if len(run02) > 0 and pd.notna(run02.iloc[0]["tsnr"]):
            if run02.iloc[0]["excluded"]:
                run02_excl = 1
                if run02.iloc[0]["exclusion_reason"]:
                    reasons.append(f"run02_{run02.iloc[0]['exclusion_reason']}")
            else:
                run02_excl = 0
        else:
            run02_excl = "NA"
        
        exclusion_rows.append({
            "subject_id": subject_id,
            "run01_excluded": run01_excl,
            "run02_excluded": run02_excl,
            "exclusion_reason": ";".join(reasons)
        })
    
    df_excl = pd.DataFrame(exclusion_rows).sort_values("subject_id").reset_index(drop=True)
    df_excl.to_csv(OUTPUT_TSV, sep="\t", index=False)
    print(f"Exclusions TSV: {OUTPUT_TSV}")
    
    # --- Summary ---
    n_subjects = len(df_excl)
    n_run01_excl = (df_excl["run01_excluded"] == 1).sum()
    n_run02_excl = (df_excl["run02_excluded"] == 1).sum()
    n_both_excl = ((df_excl["run01_excluded"] == 1) & (df_excl["run02_excluded"] == 1)).sum()
    n_run01_na = (df_excl["run01_excluded"] == "NA").sum()
    n_run02_na = (df_excl["run02_excluded"] == "NA").sum()
    
    print()
    print("MRIQC exclusion check complete")
    print(f"  Total subjects: {n_subjects}")
    print(f"  Run 01 excluded: {n_run01_excl}")
    print(f"  Run 02 excluded: {n_run02_excl}")
    print(f"  Both runs excluded: {n_both_excl}")
    print(f"  Run 01 missing data: {n_run01_na}")
    print(f"  Run 02 missing data: {n_run02_na}")


if __name__ == "__main__":
    main()
