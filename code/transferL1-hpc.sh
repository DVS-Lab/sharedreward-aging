#!/bin/bash

# This script is used to transfer BIDS info from the local to cluster

# Ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
basedir="$(dirname "$scriptdir")"

fmriprep_dir=/ZPOOL/data/projects/rf1-sra-data/derivatives/fmriprep
bids_dir=/ZPOOL/data/projects/rf1-datapaper-dev/bids
destination_server="@owlsnest.hpc.temple.edu"

read -p "Enter AccessNet ID: " destination_user
	
for sub in $(cat "${scriptdir}/sublist_all.txt"); do

	source_fmriprep="$fmriprep_dir/sub-$sub"
	source_bids="$bids_dir/sub-$sub/func"

	# Transfer Preproc BOLD files, Confound files, and events.tsv files
	rsync -avh --no-compress --progress \
		--ignore-existing \
		--recursive \
		--include='*/' \
		--include='*MNI152NLin6Asym_desc-preproc_bold.nii.gz' \
		--include='*-confounds_timeseries.tsv' \
		--include='*_events.tsv' \
		--exclude='*' \
		"${source_fmriprep}" "${destination_user}${destination_server}:work/rf1-sra-data/derivatives/fmriprep/sub-${sub}/"
		
	sleep 10

	# Transfer events.tsv files
	rsync -avh --no-compress --progress \
		--ignore-existing \
		--recursive \
		--include='*/' \
		--include='*_events.tsv' \
		--exclude='*' \
		"${source_bids}" "${destination_user}${destination_server}:work/rf1-sra-data/bids/sub-${sub}/"
		
	sleep 30
	
done

exit
