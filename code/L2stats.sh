#!/bin/bash

# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
maindir="$(dirname "$scriptdir")"

# setting inputs and common variables
sub=$1
type=$2
task1=sharedreward # edit if necessary
sm=4 # edit if necessary
MAINOUTPUT=${maindir}/derivatives/fsl/sub-${sub}
model=1
NCOPES=18


# --- start EDIT HERE start: exceptions and conditionals for the task

# ppi has more contrasts than act (phys), so need a different L2 template
if [ "${type}" == "act" ]; then
	ITEMPLATE=${maindir}/templates/L2_task-trust_model-${model}_type-act_nruns-2.fsf
	NCOPES=${NCOPES}
else
	ITEMPLATE=${maindir}/templates/L2_task-trust_model-${model}_type-ppi_nruns-2.fsf
	let NCOPES=${NCOPES}+1 # add 1 since we tend to only have one extra contrast for PPI
fi

# --- end EDIT HERE end: exceptions and conditionals for the task; need to exclude bad/missing runs

if [ ${#sub} -eq 3 ]; then
	INPUT1=${MAINOUTPUT}/L1_task-trust_model-${model}_type-${type}_run-01_sm-${sm}.feat
	INPUT2=${MAINOUTPUT}/L1_task-trust_model-${model}_type-${type}_run-02_sm-${sm}.feat
elif [ ${#sub} -eq 5 ]; then
	INPUT1=${MAINOUTPUT}/L1_task-trust_model-${model}_type-${type}_run-1_sm-${sm}.feat
	INPUT2=${MAINOUTPUT}/L1_task-trust_model-${model}_type-${type}_run-2_sm-${sm}.feat
fi

# check for existing output and re-do if missing/incomplete
OUTPUT=${MAINOUTPUT}/L2_task-trust_model-${model}_type-${type}_sm-${sm}
if [ -e ${OUTPUT}.gfeat/cope${NCOPES}.feat/cluster_mask_zstat1.nii.gz ]; then # check last (act) or penultimate (ppi) cope
	echo "skipping existing output"
else
	echo "re-doing: ${OUTPUT}" >> re-runL2.log
	rm -rf ${OUTPUT}.gfeat

	# set output template and run template-specific analyses
	OTEMPLATE=${MAINOUTPUT}/L2_task-trust_model-${model}_type-${type}.fsf
	sed -e 's@OUTPUT@'$OUTPUT'@g' \
	-e 's@INPUT1@'$INPUT1'@g' \
	-e 's@INPUT2@'$INPUT2'@g' \
	<$ITEMPLATE> $OTEMPLATE
	feat $OTEMPLATE

	# delete unused files
	for cope in `seq ${NCOPES}`; do
		rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/res4d.nii.gz
		rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/corrections.nii.gz
		rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/stats/threshac1.nii.gz
		rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/filtered_func_data.nii.gz
		rm -rf ${OUTPUT}.gfeat/cope${cope}.feat/var_filtered_func_data.nii.gz
	done

fi