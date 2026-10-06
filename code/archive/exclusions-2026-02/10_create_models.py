#!/usr/bin/env python3
"""
create_model_files.py

Create individual FSL model CSV files:
- Baseline model (ones + covariates, no age)
- Baseline model with age (ones + covariates + age)
- One file per contrast (ones + covariates + age + contrast + age*contrast interaction)

Usage: python create_model_files.py [fsl_model_tsv] [output_dir]

Output: CSV files in models/ directory
"""

import os
import sys
import pandas as pd

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"

# --- Input/Output ---
FSL_MODEL_TSV = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/exclusions/fsl_model.tsv"
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/models"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Base columns (always included)
BASE_COLS = [
    "sub", "path", "ones",
    "age_demeaned", "study_demeaned", "flip_demeaned", 
    "tsnr_demeaned", "fd_mean_demeaned",
    "gender_M_demeaned", "gender_F_demeaned"
]

# Base columns WITHOUT age
BASE_COLS_NO_AGE = [
    "sub", "path", "ones",
    "study_demeaned", "flip_demeaned", 
    "tsnr_demeaned", "fd_mean_demeaned",
    "gender_M_demeaned", "gender_F_demeaned"
]

# Contrasts to create model files for
CONTRASTS = [
    "FminS_win_z",
    "FminS_loss_z",
    "FminC_win_z",
    "FminC_loss_z",
    "Fwin_minus_Floss_minus_Swin_minus_Sloss_z",
    "Fwin_minus_Floss_minus_Cwin_minus_Closs_z",
    "FSC_win_minus_FSC_loss_z"
]


def main():
    print("Creating model files...")
    
    # Load the full model TSV
    if not os.path.exists(FSL_MODEL_TSV):
        print(f"ERROR: {FSL_MODEL_TSV} not found")
        sys.exit(1)
    
    df = pd.read_csv(FSL_MODEL_TSV, sep="\t")
    print(f"  Loaded {len(df)} subjects from {FSL_MODEL_TSV}")
    
    # --- Create baseline model WITHOUT age ---
    df_baseline_no_age = df[BASE_COLS_NO_AGE].copy()
    output_file = os.path.join(OUTPUT_DIR, "model_baseline.csv")
    df_baseline_no_age.to_csv(output_file, index=False)
    print(f"  Created: {output_file}")
    
    # --- Create baseline model WITH age ---
    df_baseline_age = df[BASE_COLS].copy()
    output_file = os.path.join(OUTPUT_DIR, "model_baseline_age.csv")
    df_baseline_age.to_csv(output_file, index=False)
    print(f"  Created: {output_file}")
    
    # --- Create a model file for each contrast ---
    for contrast in CONTRASTS:
        contrast_col = f"{contrast}_demeaned"
        interaction_col = f"age_x_{contrast}_demeaned"
        
        # Check columns exist
        if contrast_col not in df.columns:
            print(f"  WARNING: {contrast_col} not found, skipping")
            continue
        if interaction_col not in df.columns:
            print(f"  WARNING: {interaction_col} not found, skipping")
            continue
        
        # Select columns for this model
        model_cols = BASE_COLS + [contrast_col, interaction_col]
        df_model = df[model_cols].copy()
        
        # Output filename
        output_file = os.path.join(OUTPUT_DIR, f"model_{contrast}.csv")
        df_model.to_csv(output_file, index=False)
        print(f"  Created: {output_file}")
    
    print()
    print(f"Model files complete: {len(CONTRASTS) + 2} files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
