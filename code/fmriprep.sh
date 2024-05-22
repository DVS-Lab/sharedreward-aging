#!/bin/bash


sub=$1

# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
maindir="$(dirname "$scriptdir")"

# make derivatives folder if it doesn't exist.
# let's keep this out of bids for now
if [ ! -d $maindir/derivatives ]; then
	mkdir -p $maindir/derivatives
fi

scratchdir=/ZPOOL/data/scratch/`whoami`
if [ ! -d $scratchdir ]; then
	mkdir -p $scratchdir
fi


TEMPLATEFLOW_DIR=/ZPOOL/data/tools/templateflow
export SINGULARITYENV_TEMPLATEFLOW_HOME=/opt/templateflow

if [ $sub -ge 300 ] ; then
	singularity run --cleanenv \
	-B ${TEMPLATEFLOW_DIR}:/opt/templateflow \
	-B $maindir:/base \
	-B /ZPOOL/data/projects/rf1-sra-data/bids:/input \
	-B /ZPOOL/data/tools/licenses:/opts \
	-B $scratchdir:/scratch \
	/ZPOOL/data/tools/fmriprep-23.2.1.simg \
	/input /base/derivatives/fmriprep \
	participant --participant_label $sub \
	-t sharedreward \
	--stop-on-first-crash \
	--me-output-echos \
	--use-syn-sdc \
	--output-spaces MNI152NLin6Asym:res-2 \
	--bids-filter-file /base/code/fmriprep_config.json \
	--fs-no-reconall --fs-license-file /opts/fs_license.txt -w /scratch
else
	singularity run --cleanenv \
	-B ${TEMPLATEFLOW_DIR}:/opt/templateflow \
	-B $maindir:/base \
	-B /ZPOOL/data/tools/licenses:/opts \
	-B $scratchdir:/scratch \
	/ZPOOL/data/tools/fmriprep-23.2.1.simg \
	/base/ds003745 /base/derivatives/fmriprep \
	participant --participant_label $sub \
	-t sharedreward \
	--stop-on-first-crash \
	--use-syn-sdc \
	--output-spaces MNI152NLin6Asym:res-2 \
	--fs-no-reconall --fs-license-file /opts/fs_license.txt -w /scratch
fi

#	--bids-filter-file /base/code/fmriprep_config.json \
