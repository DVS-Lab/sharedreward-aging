#!/bin/bash
# load modules and go to workdir
# source $FSLDIR/etc/fslconf/fsl.sh
cd $PBS_O_WORKDIR

# ensure paths are correct
projectdir=/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging
scriptdir=$projectdir/code
bidsdir=$projectdir/bids
logdir=$projectdir/logs
mkdir -p $logdir

rm -f L1stats-aging*.o*
rm -f L1stats-aging*.e*

rm -f $logdir/cmd_feat_${PBS_JOBID}.txt
touch $logdir/cmd_feat_${PBS_JOBID}.txt

sub=$1
task=$2
run=$3
ppi=$4
sm=5

# need to change this to a more targetted list of subjects
# also should only run this if the inputs exist. add if statements.

# set inputs and general outputs (should not need to chage across studies in Smith Lab)
MAINOUTPUT=${projectdir}/derivatives/fsl/sub-${sub}
mkdir -p $MAINOUTPUT

# Conditional setting of DATA variable based on the length of sub
if [ ${#sub} -eq 3 ]; then
    DATA=${projectdir}/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${task}_run-${run}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
elif [ ${#sub} -eq 5 ]; then
    DATA=${projectdir}/derivatives/fmriprep/sub-${sub}/ses-01/func/sub-${sub}_ses-01_task-${task}_run-${run}_part-mag_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
fi

# Conditional setting of CONFOUNDEVS based on the length of sub
if [ ${#sub} -eq 3 ]; then
    CONFOUNDEVS=${projectdir}/derivatives/fsl/confounds/sub-${sub}/sub-${sub}_task-${task}_run-${run}_desc-fslConfounds.tsv
elif [ ${#sub} -eq 5 ]; then
    CONFOUNDEVS=${projectdir}/derivatives/fsl/confounds_tedana/sub-${sub}/ses-01/sub-${sub}_ses-01_task-${task}_run-${run}_desc-TedanaPlusConfounds.tsv
fi

if [ ! -e $CONFOUNDEVS ]; then
    echo "missing: $CONFOUNDEVS " >> ${projectdir}/re-runL1.log
    exit # exiting/continuing to ensure nothing gets run without confounds
fi

# Add session path for 5-digit subject IDs
if [ ${#sub} -eq 5 ]; then
    ses="ses-01"
    EVDIR=${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${ses}/${task}/run-${run}
    evcheck=${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${ses}/${task}
else
    ses=""
    EVDIR=${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${task}/run-${run}
    evcheck=${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${task}
fi

# check for empty EVs (extendable to other studies)
if [ ! -d ${evcheck} ]; then
    echo "missing EVfiles: $EVDIR " >> ${projectdir}/re-runL1.log
    exit
fi


MISSED_TRIAL=${EVDIR}_missed_trial.txt
if [ -e $MISSED_TRIAL ]; then
    EV_SHAPE=3
else
    EV_SHAPE=10
fi

# Dynamically pull nvols since two different tasks
NVOLUMES=$(fslnvols $DATA)
TR_INFO=$(fslval $DATA pixdim4)

# if network (ecn or dmn), do nppi; otherwise, do activation or seed-based ppi
if [ "$ppi" == "ecn" -o  "$ppi" == "dmn" ]; then

    # check for output and skip existing
    OUTPUT=${MAINOUTPUT}/L1_task-${task}_model-1_type-melodic-nppi-${ppi}_run-${run}_sm-${sm}
    if [ -e ${OUTPUT}.feat/cluster_mask_zstat1.nii.gz ]; then
        continue
    else
        echo "missing: $OUTPUT " >> ${projectdir}/re-runL1.log
        rm -rf ${OUTPUT}.feat
    fi

    # network extraction. need to ensure you have run Level 1 activation
    MASK=${MAINOUTPUT}/L1_task-${task}_model-1_type-act_run-${run}_sm-${sm}.feat/mask
    if [ ! -e ${MASK}.nii.gz ]; then
        echo "cannot run nPPI because you're missing $MASK"
        continue
    fi

    for net in `seq 0 9`; do
	NET=${projectdir}/masks/PNAS_2mm_net000${net}.nii.gz
	TSFILE=${MAINOUTPUT}/ts_task-${task}_PNAS_net${net}_nppi-${ppi}_run-${run}.txt
	fsl_glm -i $DATA -d $NET -o $TSFILE --demean -m $MASK
	eval INPUT${net}=$TSFILE
    done

    # set names for network ppi (we generally only care about ECN and DMN)
    DMN=$INPUT3
    ECN=$INPUT7

    if [ "$ppi" == "dmn" ]; then
        MAINNET=$DMN
        OTHERNET=$ECN
    else
        MAINNET=$ECN
        OTHERNET=$DMN
    fi

    # create template and run analyses
    ITEMPLATE=${projectdir}/templates/L1_task-${task}_model-1_type-nppi.fsf
    OTEMPLATE=${MAINOUTPUT}/L1_task-${task}_model-1_seed-${ppi}_run-${run}.fsf
    sed -e 's@OUTPUT@'$OUTPUT'@g' \
    -e 's@DATA@'$DATA'@g' \
    -e 's@EVDIR@'$EVDIR'@g' \
    -e 's@MISSED_TRIAL@'$MISSED_TRIAL'@g' \
    -e 's@EV_SHAPE@'$EV_SHAPE'@g' \
    -e 's@CONFOUNDEVS@'$CONFOUNDEVS'@g' \
    -e 's@MAINNET@'$MAINNET'@g' \
    -e 's@OTHERNET@'$OTHERNET'@g' \
    -e 's@INPUT0@'$INPUT0'@g' \
    -e 's@INPUT1@'$INPUT1'@g' \
    -e 's@INPUT2@'$INPUT2'@g' \
    -e 's@INPUT4@'$INPUT4'@g' \
    -e 's@INPUT5@'$INPUT5'@g' \
    -e 's@INPUT6@'$INPUT6'@g' \
    -e 's@INPUT8@'$INPUT8'@g' \
    -e 's@INPUT9@'$INPUT9'@g' \
    -e 's@NVOLUMES@'$NVOLUMES'@g' \
    -e 's@TR_INFO@'"$TR_INFO"'@g' \
    <$ITEMPLATE> $OTEMPLATE
    feat $OTEMPLATE

else # otherwise, do activation and seed-based ppi

    # set output based in whether it is activation or ppi
    if [ "$ppi" == "0" ]; then
        TYPE=act
        OUTPUT=${MAINOUTPUT}/L1_task-${task}_model-1_type-${TYPE}_run-${run}_sm-${sm}
    else
        TYPE=ppi
        OUTPUT=${MAINOUTPUT}/L1_task-${task}_model-1_type-${TYPE}_seed-${ppi}_run-${run}_sm-${sm}
    fi

    # check for output and skip existing
    if [ -e ${OUTPUT}.feat/cluster_mask_zstat1.nii.gz ]; then
        continue
    else
        echo "missing: $OUTPUT " >> ${projectdir}/re-runL1.log
        rm -rf ${OUTPUT}.feat
    fi

    # create template and run analyses
    ITEMPLATE=${projectdir}/templates/L1_task-${task}_model-1_type-${TYPE}_seed-${ppi}_HPC.fsf
    OTEMPLATE=${MAINOUTPUT}/L1_sub-${sub}_task-${task}_model-1_seed-${ppi}_run-${run}.fsf
    if [ "$ppi" == "0" ]; then
        sed -e 's@OUTPUT@'$OUTPUT'@g' \
        -e 's@DATA@'$DATA'@g' \
        -e 's@EVDIR@'$EVDIR'@g' \
        -e 's@MISSED_TRIAL@'$MISSED_TRIAL'@g' \
        -e 's@EV_SHAPE@'$EV_SHAPE'@g' \
        -e 's@SMOOTH@'$sm'@g' \
        -e 's@NVOLUMES@'$NVOLUMES'@g' \
	-e 's@TR_INFO@'"$TR_INFO"'@g' \
        -e 's@CONFOUNDEVS@'$CONFOUNDEVS'@g' \
        <$ITEMPLATE> $OTEMPLATE
	feat $OTEMPLATE
    else
        PHYS=${MAINOUTPUT}/ts_task-${task}_mask-${ppi}_run-${run}.txt
        MASK=${projectdir}/masks/seed-${ppi}.nii.gz
        fslmeants -i $DATA -o $PHYS -m $MASK
        sed -e 's@OUTPUT@'$OUTPUT'@g' \
        -e 's@DATA@'$DATA'@g' \
        -e 's@EVDIR@'$EVDIR'@g' \
        -e 's@MISSED_TRIAL@'$MISSED_TRIAL'@g' \
        -e 's@EV_SHAPE@'$EV_SHAPE'@g' \
        -e 's@PHYS@'$PHYS'@g' \
        -e 's@SMOOTH@'$sm'@g' \
        -e 's@NVOLUMES@'$NVOLUMES'@g' \
        -e 's@TR_INFO@'"$TR_INFO"'@g' \
        -e 's@CONFOUNDEVS@'$CONFOUNDEVS'@g' \
        <$ITEMPLATE> $OTEMPLATE
	feat $OTEMPLATE
    fi
fi

# fix registration as per NeuroStars post:
# https://neurostars.org/t/performing-full-glm-analysis-with-fsl-on-the-bold-images-preprocessed-by-fmriprep-without-re-registering-the-data-to-the-mni-space/784/3
mkdir -p ${OUTPUT}.feat/reg
cp $FSLDIR/etc/flirtsch/ident.mat ${OUTPUT}.feat/reg/example_func2standard.mat
cp $FSLDIR/etc/flirtsch/ident.mat ${OUTPUT}.feat/reg/standard2example_func.mat
cp ${OUTPUT}.feat/mean_func.nii.gz ${OUTPUT}.feat/reg/standard.nii.gz

# delete unused files
rm -rf ${OUTPUT}.feat/stats/res4d.nii.gz
rm -rf ${OUTPUT}.feat/stats/corrections.nii.gz
rm -rf ${OUTPUT}.feat/stats/threshac1.nii.gz
rm -rf ${OUTPUT}.feat/filtered_func_data.nii.gz
