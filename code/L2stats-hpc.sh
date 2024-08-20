#!/bin/bash
#PBS -l walltime=12:00:00
#PBS -N L2stats-aging-ppi
#PBS -q normal
#PBS -m ae
#PBS -M cooper.sharp@temple.edu
#PBS -l nodes=1:ppn=28

# load modules and go to workdir
module load fsl/6.0.2
source $FSLDIR/etc/fslconf/fsl.sh
cd $PBS_O_WORKDIR
logdir=/home/tun31934/work/sharedreward-aging/logs
maindir=/home/tun31934/work/sharedreward-aging
mkdir -p $logdir

rm -f $logdir/cmd_feat_${PBS_JOBID}.txt
touch $logdir/cmd_feat_${PBS_JOBID}.txt

# setting inputs and common variables
type="act"
seed="0"
task1=sharedreward
sm=4 # edit if necessary
model=1
NCOPES=32


for sub in ${subjects[@]}; do

# --- start EDIT HERE start: exceptions and conditionals for the task

MAINOUTPUT=${maindir}/derivatives/fsl/sub-${sub}

# ppi has more contrasts than act (phys), so need a different L2 template
if [ "${type}" == "act" ]; then
        ITEMPLATE=${maindir}/templates/L2_task-sharedreward_model-${model}_type-act.fsf
        NCOPES=${NCOPES}
else
        ITEMPLATE=${maindir}/templates/L2_task-sharedreward_model-${model}_type-ppi.fsf
        let NCOPES=${NCOPES}+1 # add 1 since we tend to only have one extra contrast for PPI
fi

# --- end EDIT HERE end: exceptions and conditionals for the task; need to exclude bad/missing runs

if [ ${#sub} -eq 3 ]; then
        INPUT1=${MAINOUTPUT}/L1_task-sharedreward_model-${model}_type-${type}_run-01_sm-${sm}.feat
        INPUT2=${MAINOUTPUT}/L1_task-sharedreward_model-${model}_type-${type}_run-02_sm-${sm}.feat
elif [ ${#sub} -eq 5 ]; then
        INPUT1=${MAINOUTPUT}/L1_task-sharedreward_model-${model}_type-${type}_run-1_sm-${sm}.feat
        INPUT2=${MAINOUTPUT}/L1_task-sharedreward_model-${model}_type-${type}_run-2_sm-${sm}.feat
fi

# check for existing output and re-do if missing/incomplete
OUTPUT=${MAINOUTPUT}/L2_task-sharedreward_model-${model}_type-${type}_sm-${sm}
if [ -e ${OUTPUT}.gfeat/cope${NCOPES}.feat/cluster_mask_zstat1.nii.gz ]; then # check last (act) or penultimate>
        echo "skipping existing output"
else
        echo "re-doing: ${OUTPUT}" >> re-runL2.log
        rm -rf ${OUTPUT}.gfeat

        # set output template and run template-specific analyses
        OTEMPLATE=${MAINOUTPUT}/L2_task-sharedreward_model-${model}_type-${type}.fsf
        sed -e 's@OUTPUT@'$OUTPUT'@g' \
        -e 's@INPUT1@'$INPUT1'@g' \
        -e 's@INPUT2@'$INPUT2'@g' \
        <$ITEMPLATE> $OTEMPLATE

        # delete unused files
        for cope in `seq ${NCOPES}`; do
                rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/res4d.nii.gz
                rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/corrections.nii.gz
                rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/threshac1.nii.gz
                rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/filtered_func_data.nii.gz
                rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/var_filtered_func_data.nii.gz
        done

fi

                echo feat $OTEMPLATE >> $logdir/cmd_feat_${PBS_JOBID}.txt

done

torque-launch -p $logdir/chk_feat_${PBS_JOBID}.txt $logdir/cmd_feat_${PBS_JOBID}.txt

