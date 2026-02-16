#!/bin/bash
#
# run_pipeline.sh
#
# Master script to run the full exclusion and model building pipeline.
#
# Pipeline order:
#   01. Check ratings exclusions
#   02. Check BIDS exclusions
#   03. Check trials exclusions
#   04. Check MRIQC exclusions
#   05. Check mask exclusions
#   06. Combine exclusions
#   07. Summarize exclusions (creates usable_subjects.csv)
#   08. Z-score ratings
#   09. Build FSL model
#   10. Create individual model files
#
# Usage: ./run_pipeline.sh

set -euo pipefail

# --- Configuration ---
basedir="/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging"
codedir="$basedir/code/exclusions"
modelsdir="$codedir/models"

echo "EXCLUSION & MODEL BUILDING PIPELINE"
echo ""
echo "Base directory: $basedir"
echo "Code directory: $codedir"
echo ""

# --- Step 0: Clear previous outputs ---
echo "[0/10] Clearing previous output files..."
rm -f "$codedir"/*.tsv
rm -f "$codedir"/*.csv
rm -rf "$modelsdir"
mkdir -p "$modelsdir"
echo "  Cleared .tsv and .csv files from $codedir"
echo "  Cleared and recreated $modelsdir"
echo ""

# --- Step 1: Ratings exclusions ---
echo "[1/10] Checking ratings exclusions..."
python "$codedir/01_check_ratings_exclusions.py"
echo ""

# --- Step 2: BIDS exclusions ---
echo "[2/10] Checking BIDS exclusions..."
bash "$codedir/02_check_bids_exclusions.sh"
echo ""

# --- Step 3: Trials exclusions ---
echo "[3/10] Checking trials exclusions..."
python "$codedir/03_check_trials_exclusions.py"
echo ""

# --- Step 4: MRIQC exclusions ---
echo "[4/10] Checking MRIQC exclusions..."
python "$codedir/04_check_mriqc_exclusions.py"
echo ""

# --- Step 5: Mask exclusions ---
echo "[5/10] Checking mask exclusions..."
bash "$codedir/05_check_mask_exclusions.sh"
echo ""

# --- Step 6: Combine exclusions ---
echo "[6/10] Combining exclusions..."
python "$codedir/06_combine_exclusions.py"
echo ""

# --- Step 7: Summarize exclusions ---
echo "[7/10] Summarizing exclusions..."
python "$codedir/07_summarize_exclusions.py"
echo ""

# --- Step 8: Z-score ratings ---
echo "[8/10] Z-scoring ratings..."
python "$codedir/08_zscore_ratings.py"
echo ""

# --- Step 9: Build FSL model ---
echo "[9/10] Building FSL model..."
python "$codedir/09_build_fsl_model.py"
echo ""

# --- Step 10: Create model files ---
echo "[10/10] Creating individual model files..."
python "$codedir/10_create_models.py"
echo ""

# --- Done ---
echo "Pipeline complete!"
echo ""
echo "Output files in: $codedir"
echo ""
echo "Exclusion files:"
ls -la "$codedir"/*.tsv 2>/dev/null || echo "  (none)"
echo ""
echo "Summary files:"
ls -la "$codedir"/*.csv 2>/dev/null || echo "  (none)"
echo ""
echo "Model files:"
ls -la "$modelsdir"/*.csv 2>/dev/null || echo "  (none)"
echo ""
