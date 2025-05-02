#!/bin/bash

# ensure paths are correct
maindir=/gpfs/scratch/tug87422/smithlab-shared/sharedreward-aging #this should be the only line that has to change if the rest of the script is set up correctly
scriptdir=$maindir/code


mapfile -t myArray < sublist-rf1.txt


# grab the first 10 elements
ntasks=20
counter=0
for task in sharedreward; do
	for type in "act"; do #"VS_thr5" "dmn"; do # 0 "VS_thr5" "dmn"; do
		
		while [ $counter -lt ${#myArray[@]} ]; do
			subjects=${myArray[@]:$counter:$ntasks}
			echo $subjects
			let counter=$counter+$ntasks
			qsub -v subjects="${subjects[@]}" L2stats-hpc.sh
		done

			bash $SCRIPTNAME $sub $task $type &
	  		sleep 1s
			done	  	
	  	done
	#done
