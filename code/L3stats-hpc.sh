#!/bin/bash
#PBS -l walltime=03:00:00
#PBS -N L3stats-aging
#PBS -q large
#PBS -m ae
#PBS -M cooper.sharp@temple.edu
#PBS -l nodes=2:ppn=16

# load modules and go to workdir
source $FSLDIR/etc/fslconf/fsl.sh
cd $PBS_O_WORKDIR

maindir=/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging
logdir=/$maindir/logs
mkdir -p $logdir

rm -f $logdir/cmd_feat_${PBS_JOBID}.txt
touch $logdir/cmd_feat_${PBS_JOBID}.txt

# study-specific inputs and general output folder
task=sharedreward
N=96
model="sogs-updated"
seed="0"
copenum_thresh_randomise=10 # actual contrasts start with cope10 (rec > def). no need to do randomise main effects (e.g., rec > nothing/fixation/baseline)
REPLACEME="act" # this defines the parts of the path that differ across analyses
MAINOUTPUT=${maindir}/derivatives/fsl/L3${REPLACEME}-large/L3_model-${model}_task-${task}_n${N}_flame1
mkdir -p $MAINOUTPUT

#### --- Two groups ------------------------------
# set outputs and check for existing

for copeinfo in "1 C_pun" "2 C_rew" "3 F_pun" "4 F_rew" "5 S_pun" "6 S_rew" "7 C_neu" "10 rew-pun" "11 F-S" "12 F-C" "13 FS-C" "14 rew-pun_F-S" "15 rew-pun_S-C" "16 rew-pun_F-C" "17 rew_F-S" "18 rew_S-C" "19 rew_F-C" "24 rew_F-SC" "26 rew_pun_F-SC" "33 phys"; do


	set -- $copeinfo
	copenum=$1
	copename=$2
	REPLACEME="act"

	# skip non-existent contrast for activation analysis
	if [ "${REPLACEME}" == "act" ] && [ "${copeinfo}" == "33 phys" ]; then
			echo "skipping phys for activation since it does not exist..."
			continue
	fi

	cnum_pad=`zeropad ${copenum} 2`
	OUTPUT=${MAINOUTPUT}/L3_task-${task}_type-${REPLACEME}_cnum-${cnum_pad}_cname-${copename}_onegroup


	echo "re-doing: ${OUTPUT}" >> re-runL3.log
	rm -rf ${OUTPUT}.gfeat

	# create template and run FEAT analyses, removed the N because of sogs typo
	ITEMPLATE=${maindir}/templates/L3_template_task-${task}_model-${model}_${N}.fsf
	OTEMPLATE=${MAINOUTPUT}/L3_task-${task}_type-${REPLACEME}_copenum-${copenum}.fsf
	sed -e 's@OUTPUT@'$OUTPUT'@g' \
	-e 's@COPENUM@'$copenum'@g' \
	-e 's@REPLACEME@'$REPLACEME'@g' \
	-e 's@BASEDIR@'$maindir'@g' \
	<$ITEMPLATE> $OTEMPLATE
	echo feat $OTEMPLATE >> $logdir/cmd_feat_${PBS_JOBID}.txt

	# delete unused files
	rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/res4d.nii.gz
	rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/corrections.nii.gz
	rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/threshac1.nii.gz
	#rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/filtered_func_data.nii.gz
	rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/var_filtered_func_data.nii.gz

done

torque-launch -p $logdir/chk_feat_${PBS_JOBID}.txt $logdir/cmd_feat_${PBS_JOBID}.txt

