#!/bin/bash

# Set the number of cores to use
NCORES=20

# Ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
datadir=/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep
tasks=("sharedreward")

# Print header
echo -e "sub\t task\t run\t vsmean_stan"

# Define a function to process a single subject
process_subject() {
    sub=$1
    for task in "${tasks[@]}"; do
        for run in 1 2; do
            # Zero-pad run number if subject is 3 digits
            if [[ ${#sub} -eq 3 ]]; then
                run=$(printf "%02d" $run)
            fi

            # Set file paths based on subject number length
            if [[ ${#sub} -eq 3 ]]; then
                stan_file="/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz"
                coreg_file="/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_desc-coreg_boldref.nii.gz"
            else
                stan_file="/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_part-mag_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz"
                coreg_file="/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_part-mag_desc-coreg_boldref.nii.gz"
            fi

            if [ -e "$stan_file" ]; then
                # Apply transformation using antsApplyTransforms
                antsApplyTransforms \
                -i /ZPOOL/data/projects/sharedreward-aging/masks/VS-Imanova_2mm.nii \
                -r "$coreg_file" \
                -t /ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/anat/sub-${sub}_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.h5 \
                -t [/ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_from-boldref_to-T1w_mode-image_desc-coreg_xfm.txt, 1] \
                -n Linear \
                -o /ZPOOL/data/projects/sharedreward-aging/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_space-native_roi-vs_mask.nii.gz

                fslmaths "$stan_file" -Tmean tmp_mean
                fslmaths "$stan_file" -Tstd tmp_std
                fslmaths tmp_mean -div tmp_std tmp_tsnr
                fslmaths tmp_tsnr -thr 2 thr_tmp_tsnr
                vsmean_stan=$(fslstats thr_tmp_tsnr -k /ZPOOL/data/projects/sharedreward-aging/masks/VS-Imanova_2mm.nii -M)
            else
                vsmean_stan="NA"
            fi

            echo -e "$sub\t $task\t $run\t $vsmean_stan"

        done
    done
}

# Read the subject list and process subjects one at a time
while IFS= read -r sub; do
    process_subject "$sub"
done < /ZPOOL/data/projects/sharedreward-aging/code/sublist-sr.txt
