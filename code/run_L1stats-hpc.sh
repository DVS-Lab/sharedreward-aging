#!/bin/bash

# ensure paths are correct
maindir=~/work/sharedreward-aging #this should be the only line that has to change if the rest of the script is set up correctly
scriptdir=$trustdir/code


mapfile -t myArray < sublist-sr.txt


# grab the first 10 elements
ntasks=4
counter=0
for task in sharedreward; do
	for ppi in "VS"; do #"VS_thr5" "dmn"; do # 0 "VS_thr5" "dmn"; do # putting 0 first will indicate "activation"
		#for run in 1 2; do
		
		while [ $counter -lt ${#myArray[@]} ]; do
			subjects=${myArray[@]:$counter:$ntasks}
			echo $subjects
			let counter=$counter+$ntasks
			qsub -v subjects="${subjects[@]}" L1stats-hpc.sh
		done

			bash $SCRIPTNAME $sub $run $ppi $task &
	  		sleep 1s
			done	  	
	  	done
	#done
