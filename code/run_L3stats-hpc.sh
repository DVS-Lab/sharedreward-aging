#!/bin/bash

maindir=/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging
logdir=$maindir/logs
mkdir -p $logdir

rm -f $logdir/cmd_feat_launcher.txt
touch $logdir/cmd_feat_launcher.txt

# study-specific inputs and general output folder
task=sharedreward
N=245
#model="Fwin-Floss_Swin-Sloss"
model="Fwin-Swin"
#model="Floss-Sloss"
#model="age"

copenum_thresh_randomise=10
REPLACEME="ppi_seed-mPFC"
MAINOUTPUT=${maindir}/derivatives/fsl-compare/L3${REPLACEME}/L3_model-${model}_task-${task}_n${N}_flame1
mkdir -p $MAINOUTPUT

#### --- Submit one job per contrast -----
#for copeinfo in "1 C_pun" "2 C_rew" "3 F_pun" "4 F_rew" "5 S_pun" "6 S_rew" "10 rew-pun" "14 rew-pun_F-S" "17 rew_F-S" "18 pun_F-S" "33 phys"; do
#for copeinfo in "17 rew_F-S" "33 phys"; do
#for copeinfo in "14 rew-pun_F-S" "33 phys"; do
for copeinfo in "17 rew_F-S"; do

  set -- $copeinfo
  copenum=$1
  copename=$2

  # skip non-existent contrast for activation analysis
  if [ "${REPLACEME}" == "act" ] && [ "${copeinfo}" == "33 phys" ]; then
      echo "skipping phys for activation since it does not exist..."
      continue
  fi

  cnum_pad=`zeropad ${copenum} 2`
  OUTPUT=${MAINOUTPUT}/L3_task-${task}_type-${REPLACEME}_cnum-${cnum_pad}_cname-${copename}_onegroup

  echo "re-doing: ${OUTPUT}" >> re-runL3.log
  rm -rf ${OUTPUT}.gfeat

  # create template
  ITEMPLATE=${maindir}/templates/L3_template_task-${task}_model-${model}_n${N}.fsf
  OTEMPLATE=${MAINOUTPUT}/L3_task-${task}_type-${REPLACEME}_copenum-${copenum}.fsf
  sed -e 's@OUTPUT@'$OUTPUT'@g' \
      -e 's@COPENUM@'$copenum'@g' \
      -e 's@REPLACEME@'$REPLACEME'@g' \
      -e 's@BASEDIR@'$maindir'@g' \
      <$ITEMPLATE> $OTEMPLATE

  # submit each contrast as a separate job
  qsub -N "${REPLACEME}_model-${model}_L3_${copename}" -o $logdir -e $logdir <<EOF
#!/bin/bash
#PBS -l walltime=12:00:00
#PBS -N ${REPLACEME}_model-${model}_L3_${copename}
#PBS -q normal
#PBS -m ae
#PBS -M cooper.sharp@temple.edu
#PBS -l nodes=1:ppn=28

cd \$PBS_O_WORKDIR

feat $OTEMPLATE

# clean up unused files
rm -rf ${OUTPUT}.gfeat/cope${copenum}.feat/stats/res4d.nii.gz
rm -rf ${OUTPUT}.gfeat/cope${copenum}.feat/stats/corrections.nii.gz
rm -rf ${OUTPUT}.gfeat/cope${copenum}.feat/stats/threshac1.nii.gz
rm -rf ${OUTPUT}.gfeat/cope${copenum}.feat/var_filtered_func_data.nii.gz

EOF

done

