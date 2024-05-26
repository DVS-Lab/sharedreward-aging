#!/bin/bash

# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

touch $scriptdir/missing-tedanaInput.log

for sub in `cat ${scriptdir}/sublist-rf1.txt`; do
	for run in 1 2; do
		script=${scriptdir}/tedana.sh
		NCORES=12
		while [ $(ps -ef | grep -v grep | grep $script | wc -l) -ge $NCORES ]; do
			sleep 5s
		done
		bash $script $sub $run &
		sleep 5s
	done
done
