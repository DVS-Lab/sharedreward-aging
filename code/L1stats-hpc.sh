#!/bin/bash
#PBS -l walltime=12:00:00
#PBS -N L1stats-trust-all
#PBS -q normal
#PBS -m ae
#PBS -M cooper.sharp@temple.edu
#PBS -l nodes=1:ppn=2

# load modules and go to workdir
module load fsl/6.0.2
source $FSLDIR/etc/fslconf/fsl.sh
cd $PBS_O_WORKDIR

# ensure paths are correct
datadir=~/work/sharedreward-aging #this should be the only line that has to change if the rest of the script is set up correctly
projectdir=~/work/sharedreward-aging
scriptdir=/$projectdir/code
bidsdir=/$datadir/ds003745
logdir=/$datadir/logs
mkdir -p $logdir

rm -f $logdir/cmd_feat_${PBS_JOBID}.txt
touch $logdir/cmd_feat_${PBS_JOBID}.txt

TASK=sharedreward
ppi=0
sm=4

# need to change this to a more targeted list of subjects
# also should only run this if the inputs exist. add if statements.
for sub in ${subjects[@]}; do
    for run in 1 2; do

        # Zero-padding for run variable in inputs if sub is three characters
        if [ ${#sub} -eq 3 ]; then
            run_padded=$(printf "%02d" $run)
        else
            run_padded=$run
        fi

        # set inputs and general outputs (should not need to change across studies in Smith Lab)
        MAINOUTPUT=${projectdir}/derivatives/fsl/sub-${sub}
        mkdir -p $MAINOUTPUT

        # Conditional setting of DATA variable based on the length of sub
        if [ ${#sub} -eq 3 ]; then
            DATA=${datadir}/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${TASK}_run-${run_padded}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
        elif [ ${#sub} -eq 5 ]; then
            DATA=${datadir}/derivatives/fmriprep/sub-${sub}/func/sub-${sub}_task-${TASK}_run-${run_padded}_part-mag_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
        fi

        # Conditional setting of CONFOUNDEVS based on the length of sub
        if [ ${#sub} -eq 3 ]; then
            CONFOUNDEVS=${datadir}/derivatives/fsl/confounds/sub-${sub}/sub-${sub}_task-${TASK}_run-${run_padded}_desc-fslConfounds.tsv
        elif [ ${#sub} -eq 5 ]; then
            CONFOUNDEVS=${datadir}/derivatives/fsl/confounds_tedana/sub-${sub}/sub-${sub}_task-${TASK}_run-${run_padded}_desc-TedanaPlusConfounds.tsv
        fi

        if [ ! -e $CONFOUNDEVS ]; then
            echo "missing: $CONFOUNDEVS " >> ${projectdir}/re-runL1.log
            continue # exiting/continuing to ensure nothing gets run without confounds
        fi
        
        EVDIR=${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${TASK}/run-${run} # don't zero-pad here since only 2 runs at most
        if [ ! -d ${projectdir}/derivatives/fsl/EVfiles/sub-${sub}/${TASK} ]; then
            echo "missing EVfiles: $EVDIR " >> ${projectdir}/re-runL1.log
            continue # skip these since some won't exist yet
        fi

        # check for empty EVs (extendable to other studies)
        MISSED_TRIAL=${EVDIR}_missed_trial.txt
        if [ -e $MISSED_TRIAL ]; then
            EV_SHAPE=3
        else
            EV_SHAPE=10
        fi

        # if network (ecn or dmn), do nppi; otherwise, do activation or seed-based ppi
        if [ "$ppi" == "ecn" -o  "$ppi" == "dmn" ]; then

            # check for output and skip existing
            OUTPUT=${MAINOUTPUT}/L1_task-${TASK}_model-1_type-melodic-nppi-${ppi}_run-${run}_sm-${sm}
            if [ -e ${OUTPUT}.feat/cluster_mask_zstat1.nii.gz ]; then
                continue
            else
                echo "missing: $OUTPUT " >> ${projectdir}/re-runL1.log
                rm -rf ${OUTPUT}.feat
            fi

            # network extraction. need to ensure you have run Level 1 activation
            MASK=${MAINOUTPUT}/L1_task-${TASK}_model-1_type-act_run-${run}_sm-${sm}.feat/mask
            if [ ! -e ${MASK}.nii.gz ]; then
                echo "cannot run nPPI because you're missing $MASK"
                continue
            fi
            for net in `seq 0 9`; do
                NET=${projectdir}/masks/melodic-114_smith09_net${net}.nii.gz
                TSFILE=${MAINOUTPUT}/ts_task-${TASK}_melodic-114_net${net}_nppi-${ppi}_run-${run}.txt
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
            ITEMPLATE=${projectdir}/templates/L1_task-${TASK}_model-1_type-nppi.fsf
            OTEMPLATE=${MAINOUTPUT}/L1_task-${TASK}_model-1_seed-${ppi}_run-${run}.fsf
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
            -e 's@INPUT9@'$INPUT9'@g' 
            <$ITEMPLATE> $OTEMPLATE

        else # otherwise, do activation and seed-based ppi

            # set output based in whether it is activation or ppi
            if [ "$ppi" == "0" ]; then
                TYPE=act
                OUTPUT=${MAINOUTPUT}/L1_task-${TASK}_model-1_type-${TYPE}_run-${run_padded}_sm-${sm}
                REPLACE_NVOLS=$(fslnvols $DATA)
                REPLACE_TR=$(fslval $DATA pixdim4)
            else
                TYPE=ppi
                OUTPUT=${MAINOUTPUT}/L1_task-${TASK}_model-1_type-${TYPE}_seed-${ppi}_run-${run_padded}_sm-${sm}
            fi

            # check for output and skip existing
            if [ -e ${OUTPUT}.feat/cluster_mask_zstat1.nii.gz]; then
                continue
            else
                echo "missing: $OUTPUT " >> ${projectdir}/re-runL1.log
                rm -rf ${OUTPUT}.feat
            fi

            # create template and run analyses
            ITEMPLATE=${projectdir}/templates/L1_task-${TASK}_model-1_type-${TYPE}.fsf
            OTEMPLATE=${MAINOUTPUT}/L1_sub-${sub}_task-${TASK}_model-1_seed-${ppi}_run-${run}.fsf
            if [ "$ppi" == "0" ]; then
            	 REPLACE_NVOLS=$(fslnvols $DATA)
                REPLACE_TR=$(fslval $DATA pixdim4)
                sed -e 's@OUTPUT@'$OUTPUT'@g' \
                -e 's@REPLACE_TR@'$REPLACE_TR'@g' \
                -e 's@REPLACE_NVOLS@'$REPLACE_NVOLS'@g' \
                -e 's@DATA@'$DATA'@g' \
                -e 's@EVDIR@'$EVDIR'@g' \
                -e 's@MISSED_TRIAL@'$MISSED_TRIAL'@g' \
                -e 's@EV_SHAPE@'$EV_SHAPE'@g' \
                -e 's@CONFOUNDEVS@'$CONFOUNDEVS'@g' \
                <$ITEMPLATE> $OTEMPLATE
            else
            	 REPLACE_NVOLS=$(fslnvols $DATA)
                REPLACE_TR=$(fslval $DATA pixdim4)
                sed -e 's@OUTPUT@'$OUTPUT'@g' \
                -e 's@REPLACE_TR@'$REPLACE_TR'@g' \
                -e 's@REPLACE_NVOLS@'$REPLACE_NVOLS'@g' \
                -e 's@DATA@'$DATA'@g' \
                -e 's@EVDIR@'$EVDIR'@g' \
                -e 's@MISSED_TRIAL@'$MISSED_TRIAL'@g' \
                -e 's@EV_SHAPE@'$EV_SHAPE'@g' \
                -e 's@CONFOUNDEVS@'$CONFOUNDEVS'@g' \
                -e 's@SMOOTH@'$sm'@g' \
                -e 's@PPI@'$ppi'@g' \
                <$ITEMPLATE> $OTEMPLATE
            fi
        fi

        feat $OTEMPLATE
        echo "feat $OTEMPLATE" >> $logdir/cmd_feat_${PBS_JOBID}.txt
    done
done
