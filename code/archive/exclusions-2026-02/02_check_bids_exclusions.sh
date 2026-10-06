#!/bin/bash
#
# check_bids_exclusions.sh
# 
# Check for missing BOLD files in BIDS directory and output run-level exclusions
# in wide format (one row per subject)
#
# Usage: ./check_bids_exclusions.sh [sublist] [output_tsv]
#
# Output: TSV with columns: subject_id, run01_excluded, run02_excluded, exclusion_reason

set -euo pipefail

# --- Configuration ---
basedir="/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
bidsdir="$basedir/bids"

# --- Input/Output ---
sublist="${1:-${basedir}/code/sublist-all.txt}"
outfile="${2:-${basedir}/code/exclusions/bids_exclusions.tsv}"

# Create output directory if needed
mkdir -p "$(dirname "$outfile")"

# --- Write header ---
echo -e "subject_id\trun01_excluded\trun02_excluded\texclusion_reason" > "$outfile"

# --- Main loop ---
while read -r sub || [[ -n "$sub" ]]; do
    # Skip empty lines or comments
    [[ -z "$sub" || "$sub" =~ ^# ]] && continue

    # Clean subject ID (remove 'sub-' prefix if present)
    sub_clean="${sub#sub-}"
    subject_num="sub-${sub_clean}"
    subject_dir="$bidsdir/$subject_num"

    # Determine format based on ID length
    if [[ ${#sub_clean} -eq 3 ]]; then
        format="three"
    elif [[ ${#sub_clean} -eq 5 ]]; then
        format="five"
    else
        echo "WARNING: Skipping $sub (ID not 3 or 5 digits)" >&2
        continue
    fi

    # Initialize exclusion tracking
    run01_excluded=0
    run02_excluded=0
    reasons=()

    # Check run 1
    if [[ "$format" == "three" ]]; then
        expected_run01="$subject_dir/func/${subject_num}_task-sharedreward_run-01_bold.nii.gz"
    else
        expected_run01="$subject_dir/ses-01/func/${subject_num}_ses-01_task-sharedreward_run-1_echo-4_part-mag_bold.nii.gz"
    fi

    if [[ ! -f "$expected_run01" ]]; then
        run01_excluded=1
        reasons+=("run01_missing_bold")
    fi

    # Check run 2
    if [[ "$format" == "three" ]]; then
        expected_run02="$subject_dir/func/${subject_num}_task-sharedreward_run-02_bold.nii.gz"
    else
        expected_run02="$subject_dir/ses-01/func/${subject_num}_ses-01_task-sharedreward_run-2_echo-4_part-mag_bold.nii.gz"
    fi

    if [[ ! -f "$expected_run02" ]]; then
        run02_excluded=1
        reasons+=("run02_missing_bold")
    fi

    # Combine reasons with semicolon separator (handle empty array)
    if [[ ${#reasons[@]} -gt 0 ]]; then
        reason_str=$(IFS=';'; echo "${reasons[*]}")
    else
        reason_str=""
    fi

    # Write row
    echo -e "${sub_clean}\t${run01_excluded}\t${run02_excluded}\t${reason_str}" >> "$outfile"

done < "$sublist"

# --- Summary ---
n_subjects=$(tail -n +2 "$outfile" | wc -l)
n_run01_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$2==1' | wc -l)
n_run02_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$3==1' | wc -l)
n_both_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$2==1 && $3==1' | wc -l)

echo "BIDS exclusion check complete"
echo "  Output: $outfile"
echo "  Total subjects: $n_subjects"
echo "  Run 01 excluded: $n_run01_excluded"
echo "  Run 02 excluded: $n_run02_excluded"
echo "  Both runs excluded: $n_both_excluded"
