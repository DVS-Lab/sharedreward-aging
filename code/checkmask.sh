#!/bin/bash

# Set path to standard brain mask (use brain *mask* instead of full T1 image for correct voxel count)
standard_img="$FSLDIR/data/standard/MNI152_T1_2mm_brain_mask_dil.nii.gz"
standard_voxels=$(fslstats "$standard_img" -V | awk '{print $1}')

# Output file
echo "Subject,MaskVoxels,StandardVoxels,CoveragePercent" > mask_coverage_metrics.csv

# Loop over all masks
for mask in /gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging/derivatives/fsl/sub-*/L1_task-sharedreward_model-1_type-act_run-*_sm-4.feat/mask.nii.gz; do
    # Extract subject ID
    sub=$(echo "$mask" | grep -o 'sub-[^/]*')

    # Binarize mask to /tmp
    #tmp_mask="/tmp/${sub}_temp_mask.nii.gz"
    #fslmaths "$mask" -thr 0.5 -bin "$tmp_mask"

    # Count voxels in the binarized mask
    mask_voxels=$(fslstats "$mask" -V | awk '{print $1}')

    # Calculate coverage
    coverage=$(echo "scale=2; $mask_voxels / $standard_voxels" | bc)

    # Append results
    echo "$sub,$mask_voxels,$standard_voxels,$coverage" >> mask_coverage_metrics.csv
done

echo "Done. Results saved to mask_coverage_metrics.csv"
