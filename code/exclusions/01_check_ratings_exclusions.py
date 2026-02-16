#!/usr/bin/env python3
"""
check_ratings_exclusions.py

Check ratings files for:
1. Missing or empty ratings files
2. Identical ratings across all conditions
3. Losing rated better than winning (trait_1 sum > trait_0 sum)

Subject-level exclusion (applies to both runs).

Usage: python check_ratings_exclusions.py [sublist] [output_tsv]

Output: TSV with columns: subject_id, run01_excluded, run02_excluded, exclusion_reason
"""

import os
import sys
import re
import glob
import pandas as pd

# --- Configuration ---
BASE_DIR = "/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
RATINGS_DIR = f"{BASE_DIR}/stimuli/logs-reformatted"

# --- Input/Output ---
SUBLIST = sys.argv[1] if len(sys.argv) > 1 else f"{BASE_DIR}/code/sublist-all.txt"
OUTPUT_TSV = sys.argv[2] if len(sys.argv) > 2 else f"{BASE_DIR}/code/exclusions/ratings_exclusions.tsv"

os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)


def load_ratings_data(subject_id):
    """
    Load ratings data for a subject.
    Returns combined DataFrame or None if no data found.
    """
    # Look for ratings files
    pattern = os.path.join(RATINGS_DIR, subject_id, f"sub{subject_id}_SR-Ratings-*.csv")
    # Also try with hyphen
    pattern2 = os.path.join(RATINGS_DIR, subject_id, f"sub-{subject_id}_SR-Ratings-*.csv")
    
    file_paths = glob.glob(pattern) + glob.glob(pattern2)
    
    if not file_paths:
        return None, "missing_ratings_file"
    
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
        return None, "empty_ratings_file"
    
    combined = pd.concat(dfs, ignore_index=True)
    
    # Handle subjects with more than 6 rows (remove first 6)
    if len(combined) > 6:
        combined = combined.iloc[6:].reset_index(drop=True)
    
    if len(combined) == 0:
        return None, "empty_ratings_after_trim"
    
    return combined, None


def check_ratings_quality(df):
    """
    Check ratings quality:
    1. Identical ratings across all conditions
    2. Losing rated better than winning (trait_1 sum > trait_0 sum)
    
    Returns: (is_excluded, reason)
    """
    reasons = []
    
    try:
        # Ensure 'response' column is numeric
        df['response'] = pd.to_numeric(df['response'], errors='coerce')
        
        # Check for required columns
        if 'partner' not in df.columns or 'trait' not in df.columns or 'response' not in df.columns:
            return True, "missing_required_columns"
        
        # Add a dummy index column for pivoting
        df = df.copy()
        df['_idx'] = 0
        
        # Pivot the dataframe
        pivoted = df.pivot_table(index='_idx', columns=['partner', 'trait'], values='response', aggfunc='mean')
        
        if pivoted.empty:
            return True, "empty_pivot"
        
        # Flatten column names
        pivoted.columns = [f'partner_{col[0]}_trait_{col[1]}' for col in pivoted.columns]
        
        # Get partner columns
        partner_columns = [col for col in pivoted.columns if col.startswith('partner_')]
        
        if not partner_columns:
            return True, "no_partner_columns"
        
        # Check 1: Identical ratings (all partner ratings are the same value)
        unique_values = pivoted[partner_columns].iloc[0].nunique()
        if unique_values == 1:
            reasons.append("identical_ratings")
        
        # Check 2: Losing rated better than winning (trait_1 sum > trait_0 sum)
        trait_0_cols = [col for col in pivoted.columns if 'trait_0' in col]
        trait_1_cols = [col for col in pivoted.columns if 'trait_1' in col]
        
        if trait_0_cols and trait_1_cols:
            trait_0_sum = pivoted[trait_0_cols].iloc[0].sum()
            trait_1_sum = pivoted[trait_1_cols].iloc[0].sum()
            
            if trait_1_sum > trait_0_sum:
                reasons.append("losing_rated_better")
        
    except Exception as e:
        return True, f"processing_error: {str(e)}"
    
    if reasons:
        return True, ";".join(reasons)
    
    return False, ""


def main():
    print("Checking ratings exclusions...")
    
    # Read subject list
    with open(SUBLIST, 'r') as f:
        subjects = [line.strip().replace('sub-', '') for line in f if line.strip() and not line.startswith('#')]
    
    print(f"  Checking {len(subjects)} subjects from {SUBLIST}")
    
    # Check each subject
    results = []
    
    for subject_id in subjects:
        # Load ratings data
        df, load_error = load_ratings_data(subject_id)
        
        if load_error:
            # No data found
            results.append({
                "subject_id": subject_id,
                "run01_excluded": 1,
                "run02_excluded": 1,
                "exclusion_reason": load_error
            })
            continue
        
        # Check ratings quality
        is_excluded, quality_reason = check_ratings_quality(df)
        
        if is_excluded:
            results.append({
                "subject_id": subject_id,
                "run01_excluded": 1,
                "run02_excluded": 1,
                "exclusion_reason": quality_reason
            })
        else:
            results.append({
                "subject_id": subject_id,
                "run01_excluded": 0,
                "run02_excluded": 0,
                "exclusion_reason": ""
            })
    
    # Write output
    with open(OUTPUT_TSV, 'w') as f:
        f.write("subject_id\trun01_excluded\trun02_excluded\texclusion_reason\n")
        for row in sorted(results, key=lambda x: x["subject_id"]):
            f.write(f"{row['subject_id']}\t{row['run01_excluded']}\t{row['run02_excluded']}\t{row['exclusion_reason']}\n")
    
    # Summary
    n_subjects = len(results)
    n_excluded = sum(1 for r in results if r["run01_excluded"] == 1)
    
    # Count by reason
    reason_counts = {}
    for r in results:
        if r["exclusion_reason"]:
            for reason in r["exclusion_reason"].split(";"):
                reason = reason.strip()
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    print()
    print("Ratings exclusion check complete")
    print(f"  Output: {OUTPUT_TSV}")
    print(f"  Total subjects: {n_subjects}")
    print(f"  Both runs excluded: {n_excluded}")
    
    if reason_counts:
        print()
        print("  Exclusion reasons breakdown:")
        for reason, count in sorted(reason_counts.items()):
            print(f"    {reason}: {count}")


if __name__ == "__main__":
    main()
