#!/bin/bash
#
# check_mask_exclusions.sh
#
# Check mask coverage and flag low-end IQR outliers (per study)
# Only checks runs that were not excluded in BIDS check
#
# Usage: ./check_mask_exclusions.sh [bids_exclusions_tsv] [output_tsv]
#
# Output: TSV with columns: subject_id, run01_excluded, run02_excluded, run01_coverage, run02_coverage, run01_vmpfc_coverage, run02_vmpfc_coverage, exclusion_reason

set -euo pipefail

# --- Configuration ---
basedir="/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
derivdir="$basedir/derivatives/fsl"
standard_img="$FSLDIR/data/standard/MNI152_T1_2mm_brain_mask_dil.nii.gz"
cerebellum_mask="$basedir/masks/cerebellum-brainstem_mask.nii.gz"
vmpfc_mask="$basedir/masks/VMPFC-mask-neurovault-resliced-bin.nii.gz"
tmpdir="$basedir/scratch/tmp"
iqr_multiplier=1.5

# --- Input/Output ---
bids_exclusions="${1:-${basedir}/code/exclusions/bids_exclusions.tsv}"
outfile="${2:-${basedir}/code/exclusions/mask_exclusions.tsv}"

# Verify BIDS exclusions file exists
if [[ ! -f "$bids_exclusions" ]]; then
    echo "ERROR: BIDS exclusions file not found: $bids_exclusions" >&2
    exit 1
fi

# Create directories if needed
mkdir -p "$(dirname "$outfile")" "$tmpdir"

# Get standard voxel count
standard_voxels=$(fslstats "$standard_img" -V | awk '{print $1}')

# Get VMPFC mask voxel count
vmpfc_voxels=$(fslstats "$vmpfc_mask" -V | awk '{print $1}')

# --- Step 1: Collect coverage metrics for non-excluded BIDS runs ---
metrics_tmp=$(mktemp)
echo "subject_id,run,study,coverage,vmpfc_coverage,bids_excluded" > "$metrics_tmp"

echo "Collecting mask coverage metrics..."

# Read BIDS exclusions and process each subject
tail -n +2 "$bids_exclusions" | while IFS=$'\t' read -r sub_id run01_excl run02_excl _; do
    # Determine study and file format
    if [[ ${#sub_id} -eq 3 ]]; then
        study="SRNDNA"
        run01_fmt="01"
        run02_fmt="02"
    elif [[ ${#sub_id} -eq 5 ]]; then
        study="RF1"
        run01_fmt="1"
        run02_fmt="2"
    else
        echo "WARNING: Skipping $sub_id (ID not 3 or 5 digits)" >&2
        continue
    fi

    # Process run 01
    if [[ "$run01_excl" == "0" ]]; then
        mask="$derivdir/sub-${sub_id}/L1_task-sharedreward_model-1_type-act_run-${run01_fmt}_sm-5.feat/mask.nii.gz"
        if [[ -f "$mask" ]]; then
            # Whole brain coverage (with cerebellum added back)
            tmp_mask="$tmpdir/${sub_id}_run01_temp_mask.nii.gz"
            fslmaths "$mask" -add "$cerebellum_mask" "$tmp_mask"
            mask_voxels=$(fslstats "$tmp_mask" -V | awk '{print $1}')
            coverage=$(echo "scale=6; $mask_voxels / $standard_voxels * 100" | bc)
            rm -f "$tmp_mask"
            
            # VMPFC coverage (intersection of functional mask with VMPFC mask)
            tmp_vmpfc="$tmpdir/${sub_id}_run01_vmpfc_overlap.nii.gz"
            fslmaths "$mask" -mas "$vmpfc_mask" "$tmp_vmpfc"
            vmpfc_overlap=$(fslstats "$tmp_vmpfc" -V | awk '{print $1}')
            vmpfc_cov=$(echo "scale=6; $vmpfc_overlap / $vmpfc_voxels * 100" | bc)
            rm -f "$tmp_vmpfc"
            
            echo "$sub_id,01,$study,$coverage,$vmpfc_cov,0" >> "$metrics_tmp"
        else
            echo "WARNING: Mask not found for sub-${sub_id} run-01 (but BIDS exists)" >&2
            echo "$sub_id,01,$study,NA,NA,0" >> "$metrics_tmp"
        fi
    else
        echo "$sub_id,01,$study,NA,NA,1" >> "$metrics_tmp"
    fi

    # Process run 02
    if [[ "$run02_excl" == "0" ]]; then
        mask="$derivdir/sub-${sub_id}/L1_task-sharedreward_model-1_type-act_run-${run02_fmt}_sm-5.feat/mask.nii.gz"
        if [[ -f "$mask" ]]; then
            # Whole brain coverage (with cerebellum added back)
            tmp_mask="$tmpdir/${sub_id}_run02_temp_mask.nii.gz"
            fslmaths "$mask" -add "$cerebellum_mask" "$tmp_mask"
            mask_voxels=$(fslstats "$tmp_mask" -V | awk '{print $1}')
            coverage=$(echo "scale=6; $mask_voxels / $standard_voxels * 100" | bc)
            rm -f "$tmp_mask"
            
            # VMPFC coverage (intersection of functional mask with VMPFC mask)
            tmp_vmpfc="$tmpdir/${sub_id}_run02_vmpfc_overlap.nii.gz"
            fslmaths "$mask" -mas "$vmpfc_mask" "$tmp_vmpfc"
            vmpfc_overlap=$(fslstats "$tmp_vmpfc" -V | awk '{print $1}')
            vmpfc_cov=$(echo "scale=6; $vmpfc_overlap / $vmpfc_voxels * 100" | bc)
            rm -f "$tmp_vmpfc"
            
            echo "$sub_id,02,$study,$coverage,$vmpfc_cov,0" >> "$metrics_tmp"
        else
            echo "WARNING: Mask not found for sub-${sub_id} run-02 (but BIDS exists)" >&2
            echo "$sub_id,02,$study,NA,NA,0" >> "$metrics_tmp"
        fi
    else
        echo "$sub_id,02,$study,NA,NA,1" >> "$metrics_tmp"
    fi

done

# --- Step 2: Calculate IQR thresholds and flag outliers ---
echo "Calculating IQR thresholds per study..."

# AWK script to:
# 1. Calculate Q1, Q3, IQR per study (only for non-NA values)
# 2. Flag outliers below Q1 - 1.5*IQR
# 3. Output in wide format (NA for BIDS-excluded runs)

awk -F',' -v iqr_mult="$iqr_multiplier" '
BEGIN {
    OFS = "\t"
}
NR == 1 { next }  # Skip header

{
    sub_id = $1
    run = $2
    study = $3
    coverage = $4
    vmpfc_coverage = $5
    bids_excluded = $6

    # Store data
    data[sub_id][run]["coverage"] = coverage
    data[sub_id][run]["vmpfc_coverage"] = vmpfc_coverage
    data[sub_id][run]["bids_excluded"] = bids_excluded
    studies[sub_id] = study
    
    # Only include in IQR calculation if not NA
    if (coverage != "NA") {
        study_values[study][++study_n[study]] = coverage
    }
}

END {
    # Calculate Q1, Q3, IQR for each study
    for (s in study_values) {
        n = study_n[s]
        
        # Sort values
        for (i = 1; i <= n; i++) {
            for (j = i + 1; j <= n; j++) {
                if (study_values[s][i] > study_values[s][j]) {
                    tmp = study_values[s][i]
                    study_values[s][i] = study_values[s][j]
                    study_values[s][j] = tmp
                }
            }
        }
        
        # Q1 (25th percentile)
        q1_pos = (n + 1) * 0.25
        q1_low = int(q1_pos)
        q1_high = q1_low + 1
        if (q1_high > n) q1_high = n
        q1_frac = q1_pos - q1_low
        if (q1_low < 1) q1_low = 1
        Q1[s] = study_values[s][q1_low] + q1_frac * (study_values[s][q1_high] - study_values[s][q1_low])
        
        # Q3 (75th percentile)
        q3_pos = (n + 1) * 0.75
        q3_low = int(q3_pos)
        q3_high = q3_low + 1
        if (q3_high > n) q3_high = n
        q3_frac = q3_pos - q3_low
        if (q3_low < 1) q3_low = 1
        Q3[s] = study_values[s][q3_low] + q3_frac * (study_values[s][q3_high] - study_values[s][q3_low])
        
        # IQR and threshold
        IQR[s] = Q3[s] - Q1[s]
        threshold[s] = Q1[s] - (iqr_mult * IQR[s])
        
        printf "  %s: Q1=%.2f, Q3=%.2f, IQR=%.2f, threshold=%.2f (n=%d)\n", s, Q1[s], Q3[s], IQR[s], threshold[s], n > "/dev/stderr"
    }
    
    # Output header
    print "subject_id", "run01_excluded", "run02_excluded", "run01_coverage", "run02_coverage", "run01_vmpfc_coverage", "run02_vmpfc_coverage", "exclusion_reason"
    
    # Process each subject
    for (sub_id in studies) {
        s = studies[sub_id]
        run01_excl = "NA"
        run02_excl = "NA"
        run01_cov = "NA"
        run02_cov = "NA"
        run01_vmpfc = "NA"
        run02_vmpfc = "NA"
        reasons = ""
        
        # Check run 01
        if ("01" in data[sub_id]) {
            if (data[sub_id]["01"]["bids_excluded"] == 1) {
                run01_excl = "NA"
                run01_cov = "NA"
                run01_vmpfc = "NA"
            } else if (data[sub_id]["01"]["coverage"] == "NA") {
                run01_excl = "NA"
                run01_cov = "NA"
                run01_vmpfc = "NA"
            } else {
                run01_cov = sprintf("%.2f", data[sub_id]["01"]["coverage"])
                run01_vmpfc = sprintf("%.2f", data[sub_id]["01"]["vmpfc_coverage"])
                if (data[sub_id]["01"]["coverage"] < threshold[s]) {
                    run01_excl = 1
                    reasons = "run01_low_coverage"
                } else {
                    run01_excl = 0
                }
            }
        }
        
        # Check run 02
        if ("02" in data[sub_id]) {
            if (data[sub_id]["02"]["bids_excluded"] == 1) {
                run02_excl = "NA"
                run02_cov = "NA"
                run02_vmpfc = "NA"
            } else if (data[sub_id]["02"]["coverage"] == "NA") {
                run02_excl = "NA"
                run02_cov = "NA"
                run02_vmpfc = "NA"
            } else {
                run02_cov = sprintf("%.2f", data[sub_id]["02"]["coverage"])
                run02_vmpfc = sprintf("%.2f", data[sub_id]["02"]["vmpfc_coverage"])
                if (data[sub_id]["02"]["coverage"] < threshold[s]) {
                    run02_excl = 1
                    if (reasons != "") reasons = reasons ";"
                    reasons = reasons "run02_low_coverage"
                } else {
                    run02_excl = 0
                }
            }
        }
        
        print sub_id, run01_excl, run02_excl, run01_cov, run02_cov, run01_vmpfc, run02_vmpfc, reasons
    }
}
' "$metrics_tmp" | (read -r header; echo "$header"; sort -t$'\t' -k1,1) > "$outfile"

# Clean up
rm -f "$metrics_tmp"

# --- Summary ---
n_subjects=$(tail -n +2 "$outfile" | wc -l)
n_run01_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$2==1' | wc -l)
n_run02_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$3==1' | wc -l)
n_both_excluded=$(tail -n +2 "$outfile" | awk -F'\t' '$2==1 && $3==1' | wc -l)

echo ""
echo "Mask exclusion check complete"
echo "  Output: $outfile"
echo "  Total subjects: $n_subjects"
echo "  Run 01 excluded: $n_run01_excluded"
echo "  Run 02 excluded: $n_run02_excluded"
echo "  Both runs excluded: $n_both_excluded"
