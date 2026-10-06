#!/usr/bin/env python3
"""
build_fsl_model.py

Build FSL model files with subject paths based on usable runs.

Usage: python build_fsl_model.py [usable_subjects_csv] [output_tsv]

Output: TSV with sub, path, ones, age, tsnr, fd_mean columns
"""

import os
import sys
import pandas as pd
import numpy as np

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
FSL_DIR = f"{BASE_DIR}/derivatives/fsl"

# Participants files
PARTICIPANTS_RF1 = f"{BASE_DIR}/participants-rf1.tsv"
PARTICIPANTS_SRNDNA = f"{BASE_DIR}/participants-srndna.tsv"

# Flip angles file
FLIP_ANGLES = f"{BASE_DIR}/code/flip-angles.csv"

# Z-scored ratings file
RATINGS_ZSCORED = f"{BASE_DIR}/code/exclusions/ratings_zscored.tsv"

# MRIQC metrics file
MRIQC_METRICS = f"{BASE_DIR}/code/exclusions/mriqc_metrics.tsv"

# Path templates
L2_TEMPLATE = f"{FSL_DIR}/sub-{{sub}}/L2_task-sharedreward_model-1_type-REPLACEME_sm-5.gfeat/copeCOPENUM.feat/stats/cope1.nii.gz"
L1_TEMPLATE = f"{FSL_DIR}/sub-{{sub}}/L1_task-sharedreward_model-1_type-REPLACEME_run-{{run}}_sm-5.feat/stats/copeCOPENUM.nii.gz"

# --- Input/Output ---
USABLE_CSV = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/exclusions/usable_subjects.csv"
OUTPUT_TSV = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/fsl_model.tsv"

os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)


def load_participants():
    """Load and combine participants files, return dict of subject_id -> {age, sex}."""
    data_dict = {}
    
    for filepath in [PARTICIPANTS_RF1, PARTICIPANTS_SRNDNA]:
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found")
            continue
        
        df = pd.read_csv(filepath, sep="\t", dtype=str)
        
        # Find subject ID column (could be 'participant_id', 'sub', 'subject_id', etc.)
        id_col = None
        for col in ["participant_id", "sub", "subject_id", "id"]:
            if col in df.columns:
                id_col = col
                break
        
        if id_col is None:
            print(f"  WARNING: No subject ID column found in {filepath}")
            continue
        
        # Find age column
        age_col = None
        for col in ["age", "Age", "AGE"]:
            if col in df.columns:
                age_col = col
                break
        
        if age_col is None:
            print(f"  WARNING: No age column found in {filepath}")
        
        # Find sex column
        sex_col = None
        for col in ["sex", "Sex", "SEX", "gender", "Gender", "GENDER"]:
            if col in df.columns:
                sex_col = col
                break
        
        if sex_col is None:
            print(f"  WARNING: No sex column found in {filepath}")
        
        # Build dict
        for _, row in df.iterrows():
            sub_id = str(row[id_col]).replace("sub-", "").strip()
            
            data_dict[sub_id] = {
                "age": row[age_col] if age_col else "",
                "sex": row[sex_col].strip().upper() if sex_col and pd.notna(row[sex_col]) else ""
            }
        
        print(f"  Loaded {len(df)} subjects from {os.path.basename(filepath)}")
    
    return data_dict


def load_mriqc_metrics():
    """Load MRIQC metrics, return dict of subject_id -> {run -> {tsnr, fd_mean}}."""
    metrics_dict = {}
    
    if not os.path.exists(MRIQC_METRICS):
        print(f"  WARNING: {MRIQC_METRICS} not found")
        return metrics_dict
    
    df = pd.read_csv(MRIQC_METRICS, sep="\t", dtype=str)
    df["subject_id"] = df["subject_id"].astype(str).str.strip()
    
    for _, row in df.iterrows():
        sub_id = row["subject_id"]
        run = row["run"]
        
        if sub_id not in metrics_dict:
            metrics_dict[sub_id] = {}
        
        try:
            tsnr = float(row["tsnr"]) if pd.notna(row["tsnr"]) and row["tsnr"] != "" else None
        except:
            tsnr = None
        
        try:
            fd_mean = float(row["fd_mean"]) if pd.notna(row["fd_mean"]) and row["fd_mean"] != "" else None
        except:
            fd_mean = None
        
        metrics_dict[sub_id][run] = {"tsnr": tsnr, "fd_mean": fd_mean}
    
    print(f"  Loaded MRIQC metrics for {len(metrics_dict)} subjects")
    
    return metrics_dict


def load_flip_angles():
    """Load flip angles, return dict of subject_id -> coded value."""
    flip_dict = {}
    
    if not os.path.exists(FLIP_ANGLES):
        print(f"  WARNING: {FLIP_ANGLES} not found")
        return flip_dict
    
    df = pd.read_csv(FLIP_ANGLES, dtype=str)
    
    # Find subject column
    sub_col = None
    for col in ["sub", "subject_id", "participant_id", "id"]:
        if col in df.columns:
            sub_col = col
            break
    
    if sub_col is None:
        print(f"  WARNING: No subject column found in {FLIP_ANGLES}")
        return flip_dict
    
    if "coded" not in df.columns:
        print(f"  WARNING: No 'coded' column found in {FLIP_ANGLES}")
        return flip_dict
    
    for _, row in df.iterrows():
        sub_id = str(row[sub_col]).replace("sub-", "").strip()
        coded = row["coded"]
        flip_dict[sub_id] = coded
    
    print(f"  Loaded flip angles for {len(flip_dict)} subjects")
    
    return flip_dict


def load_ratings():
    """Load z-scored ratings, return dict of subject_id -> {column: value}."""
    ratings_dict = {}
    
    if not os.path.exists(RATINGS_ZSCORED):
        print(f"  WARNING: {RATINGS_ZSCORED} not found")
        return ratings_dict
    
    df = pd.read_csv(RATINGS_ZSCORED, sep="\t", dtype=str)
    df["subject_id"] = df["subject_id"].astype(str).str.strip()
    
    for _, row in df.iterrows():
        sub_id = row["subject_id"]
        ratings_dict[sub_id] = row.to_dict()
    
    print(f"  Loaded ratings for {len(ratings_dict)} subjects")
    
    return ratings_dict


def get_metrics_for_subject(sub, usable_runs, metrics_dict):
    """
    Get tsnr and fd_mean for a subject based on usable runs.
    - both: average across runs
    - 1: use run 01
    - 2: use run 02
    """
    if sub not in metrics_dict:
        return None, None
    
    sub_metrics = metrics_dict[sub]
    
    if usable_runs == "both":
        # Average across both runs
        tsnr_vals = []
        fd_vals = []
        
        for run in ["01", "02", "1", "2"]:
            if run in sub_metrics:
                if sub_metrics[run]["tsnr"] is not None:
                    tsnr_vals.append(sub_metrics[run]["tsnr"])
                if sub_metrics[run]["fd_mean"] is not None:
                    fd_vals.append(sub_metrics[run]["fd_mean"])
        
        tsnr = np.mean(tsnr_vals) if tsnr_vals else None
        fd_mean = np.mean(fd_vals) if fd_vals else None
        
    elif usable_runs == "1":
        # Use run 1 only
        for run in ["01", "1"]:
            if run in sub_metrics:
                tsnr = sub_metrics[run]["tsnr"]
                fd_mean = sub_metrics[run]["fd_mean"]
                break
        else:
            tsnr, fd_mean = None, None
            
    elif usable_runs == "2":
        # Use run 2 only
        for run in ["02", "2"]:
            if run in sub_metrics:
                tsnr = sub_metrics[run]["tsnr"]
                fd_mean = sub_metrics[run]["fd_mean"]
                break
        else:
            tsnr, fd_mean = None, None
    else:
        tsnr, fd_mean = None, None
    
    return tsnr, fd_mean


def get_run_format(subject_id):
    """Get run format based on subject ID length."""
    if len(str(subject_id)) == 3:
        return {"1": "01", "2": "02"}
    else:
        return {"1": "1", "2": "2"}


def main():
    print("Building FSL model file...")
    
    # Load participants data
    participants_dict = load_participants()
    
    # Load MRIQC metrics
    metrics_dict = load_mriqc_metrics()
    
    # Load flip angles
    flip_dict = load_flip_angles()
    
    # Load ratings
    ratings_dict = load_ratings()
    
    # Read usable subjects
    df = pd.read_csv(USABLE_CSV, dtype=str)
    print(f"  Loaded {len(df)} usable subjects")
    
    # Sort by subject_id ascending
    df["subject_id"] = df["subject_id"].astype(str)
    df = df.sort_values("subject_id").reset_index(drop=True)
    
    # Build output rows
    rows = []
    missing_age = []
    missing_metrics = []
    missing_sex = []
    missing_ratings = []
    
    for _, row in df.iterrows():
        sub = row["subject_id"]
        usable = row["usable_runs"]
        run_fmt = get_run_format(sub)
        
        if usable == "both":
            # Use L2 path
            path = L2_TEMPLATE.format(sub=sub)
        elif usable == "1":
            # Use L1 path with run 1
            path = L1_TEMPLATE.format(sub=sub, run=run_fmt["1"])
        elif usable == "2":
            # Use L1 path with run 2
            path = L1_TEMPLATE.format(sub=sub, run=run_fmt["2"])
        else:
            continue
        
        # Get study (0 = 3-digit/SRNDNA, 1 = 5-digit/RF1)
        study = 0 if len(sub) == 3 else 1
        
        # Get age and sex from participants data
        pdata = participants_dict.get(sub, {})
        age = pdata.get("age", "")
        sex = pdata.get("sex", "")
        
        if age == "":
            missing_age.append(sub)
        
        # Create gender dummy variables
        if sex in ["M", "MALE"]:
            gender_M = 1
            gender_F = 0
        elif sex in ["F", "FEMALE"]:
            gender_M = 0
            gender_F = 1
        elif sex in ["O", "OTHER"]:
            gender_M = 0
            gender_F = 0
        else:
            gender_M = ""
            gender_F = ""
            missing_sex.append(sub)
        
        # Get MRIQC metrics
        tsnr, fd_mean = get_metrics_for_subject(sub, usable, metrics_dict)
        if tsnr is None or fd_mean is None:
            missing_metrics.append(sub)
        
        # Get flip angle (default to 0 if not in file)
        flip = flip_dict.get(sub, "0")
        
        rows.append({
            "sub": sub,
            "path": path,
            "ones": 1,
            "age": age,
            "tsnr": tsnr if tsnr is not None else "",
            "fd_mean": fd_mean if fd_mean is not None else "",
            "study": study,
            "gender_M": gender_M,
            "gender_F": gender_F,
            "flip": flip
        })
        
        # Get ratings data
        ratings_data = ratings_dict.get(sub, {})
        if not ratings_data:
            missing_ratings.append(sub)
        
        # Add raw ratings
        raw_rating_cols = ["C_win_raw", "C_loss_raw", "S_win_raw", "S_loss_raw", "F_win_raw", "F_loss_raw"]
        for col in raw_rating_cols:
            rows[-1][col] = ratings_data.get(col, "")
        
        # Add contrast columns (z-scored)
        contrast_cols = [
            "FminS_win_z", "FminS_loss_z", "FminC_win_z", "FminC_loss_z",
            "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
            "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
            "FSC_win_minus_FSC_loss_z"
        ]
        for col in contrast_cols:
            rows[-1][col] = ratings_data.get(col, "")
    
    # Create DataFrame
    df_out = pd.DataFrame(rows)
    
    # Reorder columns: sub, path, ones, then raw values, then contrasts at end
    col_order = [
        "sub", "path", "ones", 
        "age", "tsnr", "fd_mean", "study", "flip", "gender_M", "gender_F",
        "C_win_raw", "C_loss_raw", "S_win_raw", "S_loss_raw", "F_win_raw", "F_loss_raw",
        "FminS_win_z", "FminS_loss_z", "FminC_win_z", "FminC_loss_z",
        "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
        "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
        "FSC_win_minus_FSC_loss_z"
    ]
    df_out = df_out[col_order]
    
    # Demean columns after "ones" and add as new columns
    demean_cols = [
        "age", "tsnr", "fd_mean", "study", "flip", "gender_M", "gender_F",
        "FminS_win_z", "FminS_loss_z", "FminC_win_z", "FminC_loss_z",
        "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
        "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
        "FSC_win_minus_FSC_loss_z"
    ]
    for col in demean_cols:
        # Convert to numeric, coercing errors to NaN
        numeric_col = pd.to_numeric(df_out[col], errors='coerce')
        # Demean (subtract mean of non-NaN values)
        col_mean = numeric_col.mean()
        df_out[f"{col}_demeaned"] = numeric_col - col_mean
    
    # Add age*contrast interaction columns
    contrast_cols = [
        "FminS_win_z", "FminS_loss_z", "FminC_win_z", "FminC_loss_z",
        "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
        "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
        "FSC_win_minus_FSC_loss_z"
    ]
    for col in contrast_cols:
        df_out[f"age_x_{col}_demeaned"] = df_out["age_demeaned"] * df_out[f"{col}_demeaned"]
    
    # Reorder columns to put interactions next to their contrasts
    final_col_order = [
        "sub", "path", "ones",
        # Raw demographics/metrics
        "age", "tsnr", "fd_mean", "study", "flip", "gender_M", "gender_F",
        # Raw ratings
        "C_win_raw", "C_loss_raw", "S_win_raw", "S_loss_raw", "F_win_raw", "F_loss_raw",
        # Z-scored contrasts (raw)
        "FminS_win_z", "FminS_loss_z", "FminC_win_z", "FminC_loss_z",
        "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
        "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
        "FSC_win_minus_FSC_loss_z",
        # Demeaned demographics/metrics
        "age_demeaned", "tsnr_demeaned", "fd_mean_demeaned", "study_demeaned", "flip_demeaned", "gender_M_demeaned", "gender_F_demeaned",
        # Demeaned contrasts with interactions
        "FminS_win_z_demeaned", "age_x_FminS_win_z_demeaned",
        "FminS_loss_z_demeaned", "age_x_FminS_loss_z_demeaned",
        "FminC_win_z_demeaned", "age_x_FminC_win_z_demeaned",
        "FminC_loss_z_demeaned", "age_x_FminC_loss_z_demeaned",
        "Fwin_minus_Floss_minus_Swin_minus_Sloss_z_demeaned", "age_x_Fwin_minus_Floss_minus_Swin_minus_Sloss_z_demeaned",
        "Fwin_minus_Floss_minus_Cwin_minus_Closs_z_demeaned", "age_x_Fwin_minus_Floss_minus_Cwin_minus_Closs_z_demeaned",
        "FSC_win_minus_FSC_loss_z_demeaned", "age_x_FSC_win_minus_FSC_loss_z_demeaned"
    ]
    df_out = df_out[final_col_order]
    
    # Sort by subject ID (as numeric)
    df_out["sub"] = pd.to_numeric(df_out["sub"], errors='coerce')
    df_out = df_out.sort_values("sub").reset_index(drop=True)
    
    # Save
    df_out.to_csv(OUTPUT_TSV, sep="\t", index=False)
    
    # Summary
    n_l2 = sum(1 for r in rows if "L2_" in r["path"])
    n_l1 = sum(1 for r in rows if "L1_" in r["path"])
    n_srndna = sum(1 for r in rows if r["study"] == 0)
    n_rf1 = sum(1 for r in rows if r["study"] == 1)
    n_male = sum(1 for r in rows if r["gender_M"] == 1)
    n_female = sum(1 for r in rows if r["gender_F"] == 1)
    n_flip = sum(1 for r in rows if str(r["flip"]) == "1")
    
    print()
    print("FSL model file complete")
    print(f"  Output: {OUTPUT_TSV}")
    print(f"  Total subjects: {len(rows)}")
    print(f"  L2 (both runs): {n_l2}")
    print(f"  L1 (single run): {n_l1}")
    print(f"  SRNDNA (study=0): {n_srndna}")
    print(f"  RF1 (study=1): {n_rf1}")
    print(f"  Male: {n_male}")
    print(f"  Female: {n_female}")
    print(f"  Flip=1: {n_flip}")
    
    if missing_age:
        print(f"  Missing age: {len(missing_age)} subjects")
    if missing_metrics:
        print(f"  Missing MRIQC metrics: {len(missing_metrics)} subjects")
    if missing_sex:
        print(f"  Missing sex: {len(missing_sex)} subjects")
    if missing_ratings:
        print(f"  Missing ratings: {len(missing_ratings)} subjects")


if __name__ == "__main__":
    main()
