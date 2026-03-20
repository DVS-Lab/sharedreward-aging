#!/bin/bash
#PBS -l walltime=1:00:00
#PBS -N tedana-sr
#PBS -q normal
#PBS -m ae
#PBS -M cooper.sharp@temple.edu
#PBS -l nodes=1:ppn=28

set -euo pipefail
cd "$PBS_O_WORKDIR"

# ensure paths are correct irrespective of where the user runs the script
maindir=/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging
scriptdir="$maindir/code"
logdir="$maindir/logs"
mkdir -p "$logdir"

cmdfile="$logdir/cmd_tedana_${PBS_JOBID}.txt"
missinglog="$scriptdir/missing-tedanaInput.log"
dummylog="$logdir/tedana_dummy_scans_${PBS_JOBID}.tsv"

rm -f "$cmdfile"
touch "$cmdfile"

echo -e "subject\ttask\trun\tdummy_scans" > "$dummylog"

# subjects is expected to be defined by the caller, e.g.:
# subjects=(001 002 003)
: "${subjects:?subjects array must be defined before submitting this PBS script}"

for sub in ${subjects[@]}; do
    for task in sharedreward; do
        for run in 1 2; do

            funcdir="$maindir/derivatives/fmriprep/sub-${sub}/ses-01/func"
            echo1="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_echo-1_part-mag_desc-preproc_bold.nii.gz"
            echo2="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_echo-2_part-mag_desc-preproc_bold.nii.gz"
            echo3="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_echo-3_part-mag_desc-preproc_bold.nii.gz"
            echo4="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_echo-4_part-mag_desc-preproc_bold.nii.gz"
            mask="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_desc-brain_mask.nii.gz"
            confounds="$funcdir/sub-${sub}_ses-01_task-${task}_run-${run}_desc-confounds_timeseries.tsv"

            outdir="$maindir/derivatives/tedana/sub-${sub}/ses-01"
            prefix="sub-${sub}_ses-01_task-${task}_run-${run}"

            # Check required inputs
            if [[ ! -e "$echo1" || ! -e "$echo2" || ! -e "$echo3" || ! -e "$echo4" || ! -e "$mask" || ! -e "$confounds" ]]; then
                echo "Missing one or more files for sub-${sub}, task-${task}, run-${run}" >> "$missinglog"
                echo "Skipping sub-${sub}, task-${task}, run-${run}" >> "$cmdfile"
                continue
            fi

            mkdir -p "$outdir"

            # Count consecutive non-steady-state volumes at the start of the run.
            # tedana's --dummy-scans expects an integer count from the beginning,
            # not arbitrary spike regressors later in the run.
            n_dummy=$(python - "$confounds" <<'PY'
import sys
import pandas as pd

confounds_file = sys.argv[1]
df = pd.read_csv(confounds_file, sep='\t')
nss_cols = [c for c in df.columns if c.startswith('non_steady_state_outlier')]
if not nss_cols:
    print(0)
    raise SystemExit

flag = df[nss_cols].fillna(0).astype(float).gt(0).any(axis=1).to_numpy()
n_dummy = 0
for val in flag:
    if val:
        n_dummy += 1
    else:
        break
print(n_dummy)
PY
)

            echo -e "sub-${sub}\t${task}\t${run}\t${n_dummy}" >> "$dummylog"

            # We use robustica because TEDANA developers recommend it when PCA
            # dimensionality estimation appears unstable across runs.
            echo "bash -lc 'tedana -d \"$echo1\" \"$echo2\" \"$echo3\" \"$echo4\" \
                -e 0.0138 0.03154 0.04928 0.06702 \
                --mask \"$mask\" \
                --dummy-scans $n_dummy \
                --out-dir \"$outdir\" \
                --prefix \"$prefix\" \
                --convention bids \
                --fittype curvefit \
                --ica-method robustica \
                --n-robust-runs 30 \
                --n-threads 1 \
                --overwrite'" >> "$cmdfile"

        done
    done
done

torque-launch -p "$logdir/chk_tedana_${PBS_JOBID}.txt" "$cmdfile"
