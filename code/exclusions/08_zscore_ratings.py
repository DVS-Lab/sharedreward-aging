#!/usr/bin/env python3
"""
zscore_ratings.py

Load ratings data, pivot to wide format, and Z-score within each subject's row.

Usage: python zscore_ratings.py [usable_subjects_csv] [output_tsv]

Output: TSV with one row per subject, columns for each partner/trait (raw and Z-scored)
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
from scipy import stats

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
RATINGS_DIR = f"{BASE_DIR}/stimuli/Scan-Card_Guessing_Game/logs-reformatted"

# --- Input/Output ---
USABLE_CSV = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/exclusions/usable_subjects.csv"
OUTPUT_TSV = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/ratings_zscored.tsv"

os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)


def load_ratings_data(subject_id):
    """
    Load ratings data for a subject.
    Returns combined DataFrame or None if no data found.
    """
    # Look for ratings files
    pattern = os.path.join(RATINGS_DIR, subject_id, f"sub{subject_id}_SR-Ratings-*.csv")
    pattern2 = os.path.join(RATINGS_DIR, subject_id, f"sub-{subject_id}_SR-Ratings-*.csv")
    
    file_paths = glob.glob(pattern) + glob.glob(pattern2)
    
    if not file_paths:
        return None
    
    # Load and combine all ratings files for this subject
    dfs = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            if len(df) == 0:
                continue
            dfs.append(df)
        except Exception as e:
            print(f"  WARNING: Error reading {file_path}: {e}")
            continue
    
    if not dfs:
        return None
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Handle subjects with more than 6 rows (remove first 6)
    if len(combined) > 6:
        combined = combined.iloc[6:].reset_index(drop=True)
    
    if len(combined) == 0:
        return None
    
    return combined


def pivot_ratings(df, subject_id):
    """
    Pivot ratings data to wide format.
    Returns dict with partner_X_trait_Y as keys and response values.
    """
    try:
        df = df.copy()
        df['response'] = pd.to_numeric(df['response'], errors='coerce')
        
        if 'partner' not in df.columns or 'trait' not in df.columns or 'response' not in df.columns:
            return None
        
        # Add dummy index for pivoting
        df['_idx'] = 0
        
        # Pivot
        pivoted = df.pivot_table(index='_idx', columns=['partner', 'trait'], values='response', aggfunc='mean')
        
        if pivoted.empty:
            return None
        
        # Flatten column names
        pivoted.columns = [f'partner_{col[0]}_trait_{col[1]}' for col in pivoted.columns]
        
        # Convert to dict
        return pivoted.iloc[0].to_dict()
    
    except Exception as e:
        print(f"  WARNING: Error pivoting subject {subject_id}: {e}")
        return None


def zscore_row(row_values):
    """
    Z-score a list/array of values.
    Returns array of Z-scores (NaN if std=0).
    """
    arr = np.array(row_values, dtype=float)
    
    # Handle case where all values are the same (std=0)
    if np.nanstd(arr) == 0:
        return np.full_like(arr, np.nan)
    
    return stats.zscore(arr, nan_policy='omit')


def main():
    print("Z-scoring ratings data...")
    
    # Read usable subjects
    df_usable = pd.read_csv(USABLE_CSV, dtype=str)
    subjects = df_usable["subject_id"].astype(str).str.strip().str.replace("sub-", "", regex=False).tolist()
    
    print(f"  Processing {len(subjects)} subjects from {USABLE_CSV}")
    
    # Collect all data
    all_rows = []
    rating_columns = None
    
    for subject_id in subjects:
        # Load ratings data
        df = load_ratings_data(subject_id)
        
        if df is None:
            continue
        
        # Pivot to wide format
        pivoted = pivot_ratings(df, subject_id)
        
        if pivoted is None:
            continue
        
        # Store column order from first successful subject
        if rating_columns is None:
            rating_columns = sorted(pivoted.keys())
        
        # Build row
        row = {'subject_id': subject_id}
        
        # Add raw values
        raw_values = []
        for col in rating_columns:
            val = pivoted.get(col, np.nan)
            row[f'{col}_raw'] = val
            raw_values.append(val)
        
        # Z-score across the row
        z_values = zscore_row(raw_values)
        
        # Add Z-scored values
        for i, col in enumerate(rating_columns):
            row[f'{col}_z'] = z_values[i]
        
        all_rows.append(row)
    
    # Create DataFrame
    df_out = pd.DataFrame(all_rows)
    
    # Sort by subject_id
    df_out['subject_id'] = df_out['subject_id'].astype(str)
    df_out = df_out.sort_values('subject_id').reset_index(drop=True)
    
    # Reorder columns: subject_id, then raw columns, then z columns
    raw_cols = [c for c in df_out.columns if c.endswith('_raw')]
    z_cols = [c for c in df_out.columns if c.endswith('_z')]
    ordered_cols = ['subject_id'] + sorted(raw_cols) + sorted(z_cols)
    df_out = df_out[ordered_cols]
    
    # --- Add difference columns (z-scored) ---
    # FminS (Friend minus Stranger)
    if 'partner_3_trait_0_z' in df_out.columns and 'partner_2_trait_0_z' in df_out.columns:
        df_out['FminS_win_z'] = df_out['partner_3_trait_0_z'] - df_out['partner_2_trait_0_z']
    if 'partner_3_trait_1_z' in df_out.columns and 'partner_2_trait_1_z' in df_out.columns:
        df_out['FminS_loss_z'] = df_out['partner_3_trait_1_z'] - df_out['partner_2_trait_1_z']
    
    # FminC (Friend minus Computer)
    if 'partner_3_trait_0_z' in df_out.columns and 'partner_1_trait_0_z' in df_out.columns:
        df_out['FminC_win_z'] = df_out['partner_3_trait_0_z'] - df_out['partner_1_trait_0_z']
    if 'partner_3_trait_1_z' in df_out.columns and 'partner_1_trait_1_z' in df_out.columns:
        df_out['FminC_loss_z'] = df_out['partner_3_trait_1_z'] - df_out['partner_1_trait_1_z']
    
    # --- Add contrast columns (z-scored) ---
    # (F_win - F_loss) - (S_win - S_loss)
    if all(c in df_out.columns for c in ['partner_3_trait_0_z', 'partner_3_trait_1_z', 'partner_2_trait_0_z', 'partner_2_trait_1_z']):
        df_out['Fwin_minus_Floss_minus_Swin_minus_Sloss_z'] = (
            (df_out['partner_3_trait_0_z'] - df_out['partner_3_trait_1_z']) - 
            (df_out['partner_2_trait_0_z'] - df_out['partner_2_trait_1_z'])
        )
    
    # (F_win - F_loss) - (C_win - C_loss)
    if all(c in df_out.columns for c in ['partner_3_trait_0_z', 'partner_3_trait_1_z', 'partner_1_trait_0_z', 'partner_1_trait_1_z']):
        df_out['Fwin_minus_Floss_minus_Cwin_minus_Closs_z'] = (
            (df_out['partner_3_trait_0_z'] - df_out['partner_3_trait_1_z']) - 
            (df_out['partner_1_trait_0_z'] - df_out['partner_1_trait_1_z'])
        )
    
    # (F_win + S_win + C_win) - (F_loss + S_loss + C_loss)
    if all(c in df_out.columns for c in ['partner_3_trait_0_z', 'partner_2_trait_0_z', 'partner_1_trait_0_z', 
                                          'partner_3_trait_1_z', 'partner_2_trait_1_z', 'partner_1_trait_1_z']):
        df_out['FSC_win_minus_FSC_loss_z'] = (
            (df_out['partner_3_trait_0_z'] + df_out['partner_2_trait_0_z'] + df_out['partner_1_trait_0_z']) - 
            (df_out['partner_3_trait_1_z'] + df_out['partner_2_trait_1_z'] + df_out['partner_1_trait_1_z'])
        )
    
    # --- Rename columns to readable names ---
    rename_map = {
        # Raw columns
        "partner_1_trait_0_raw": "C_win_raw",
        "partner_1_trait_1_raw": "C_loss_raw",
        "partner_2_trait_0_raw": "S_win_raw",
        "partner_2_trait_1_raw": "S_loss_raw",
        "partner_3_trait_0_raw": "F_win_raw",
        "partner_3_trait_1_raw": "F_loss_raw",
        # Z-scored columns
        "partner_1_trait_0_z": "C_win_z",
        "partner_1_trait_1_z": "C_loss_z",
        "partner_2_trait_0_z": "S_win_z",
        "partner_2_trait_1_z": "S_loss_z",
        "partner_3_trait_0_z": "F_win_z",
        "partner_3_trait_1_z": "F_loss_z",
    }
    df_out = df_out.rename(columns=rename_map)
    
    # Save
    df_out.to_csv(OUTPUT_TSV, sep='\t', index=False)
    
    # Summary
    n_processed = len(df_out)
    n_total = len(subjects)
    
    print()
    print("Z-scoring complete")
    print(f"  Output: {OUTPUT_TSV}")
    print(f"  Subjects processed: {n_processed} of {n_total}")
    print(f"  Rating columns: {len(rating_columns) if rating_columns else 0}")
    print(f"  Contrast columns added: FminS, FminC, FSC contrasts")


if __name__ == "__main__":
    main()
