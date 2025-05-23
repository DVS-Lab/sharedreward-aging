#!/usr/bin/env bash



# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
maindir="$(dirname "$scriptdir")"

# make output directory
mainoutput=${maindir}/derivatives/deepbrain
mkdir -p $mainoutput

DATA_PATH=/ZPOOL/data/projects/sharedreward-aging/derivatives/deepbrain/data/
OUT_PATH=${mainoutput}
MODEL=/ZPOOL/data/tools/DeepBrainNet/Models/DeepBrainNet_VGG16.h5


#python /ZPOOL/data/tools/DeepBrainNet/Script/Model_Test.py ${mainoutput}/tmp/ ${OUT_PATH}pred.csv $MODEL

bash /ZPOOL/data/tools/DeepBrainNet/Script/test.sh -d $DATA_PATH -o $OUT_PATH -m $MODEL
