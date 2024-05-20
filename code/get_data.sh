#!/bin/bash

# ensure paths are correct irrespective from where user runs the script
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
maindir="$(dirname "$scriptdir")"

# go to root and install datasets
cd $maindir
datalad install https://github.com/OpenNeuroDatasets/ds005123.git
datalad install https://github.com/OpenNeuroDatasets/ds003745.git # not working; issue posted

# get anatomical data and fmaps

# get sharedreward data

