#!/bin/bash

# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for sub in `cat $scriptdir/sublist-srndna.txt`; do

	script=${scriptdir}/fmriprep.sh
	NCORES=10
	while [ $(ps -ef | grep -v grep | grep $script | wc -l) -ge $NCORES ]; do
		sleep 5s
	done
	bash $script $sub &
	sleep 5s
	
done

