#!/bin/bash

# This script is used to transfer BIDS info from the local to cluster

# Ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
basedir="$(dirname "$scriptdir")"

source_directory="/ZPOOL/data/projects/rf1-sra-data/bids/"
destination_server="@owlsnest.hpc.temple.edu"
destination_path=":work/rf1-sra-data/bids/"

read -p "Enter AccessNet ID: " destination_user

for sub in `cat ${basedir}/code/sublist_all.txt`; do
#for sub in 10929; do
	source_file="$source_directory/sub-$sub"
    rsync -avh --no-compress --progress --include='*/' --include='*.nii.gz' --include='*.json' --exclude='*' "${source_file}" "${destination_user}${destination_server}${destination_path}"
done

exit   
