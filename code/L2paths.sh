#!/bin/bash

#Add flag for activation/ppi {type} and model number

# Path to the subject list file
sublist="/work/rf1-sra-trust/code/sublist_all.txt"

# Loop through each subject in the list
while IFS= read -r subject; do

    if [ -z "$files" ]; then
        files=$(ls -1 "/work/rf1-sra-trust/derivatives/fsl/sub-$subject/L1_task-trust_model-1_type-act_run-2_sm-5.feat/stats/cope1.nii.gz" 2>/dev/null)
    fi

    if [ -n "$files" ]; then
        echo "$files"
    fi
    
done < "$sublist"
