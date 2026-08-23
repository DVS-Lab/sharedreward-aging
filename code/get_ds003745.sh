#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)";source "$SCRIPT_DIR/project_config.sh"
usage(){ echo "Usage: get_ds003745.sh [--subject ID ...] [--dry-run]" >&2; }
subjects=();dry=0;while(( $# ));do case "$1" in --subject)subjects+=("${2#sub-}");shift 2;;--dry-run)dry=1;shift;;-h|--help)usage;exit 0;;*)echo "ERROR: unknown argument: $1" >&2;exit 2;;esac;done
command -v datalad>/dev/null||{ echo 'ERROR: datalad is required' >&2;exit 1;}
if [[ ! -d "$DS003745_ROOT/.git" ]]; then cmd=(datalad clone https://github.com/OpenNeuroDatasets/ds003745.git "$DS003745_ROOT"); printf '%q ' "${cmd[@]}"; echo; (( dry )) || "${cmd[@]}"; fi
cmd=(git -C "$DS003745_ROOT" checkout 2.1.1);printf '%q ' "${cmd[@]}";echo;((dry))||"${cmd[@]}"
if (( ${#subjects[@]} )); then
  for sub in "${subjects[@]}"; do
    # DataLad resolves relative input paths from the process working directory,
    # not from --dataset. Run from the nested dataset so these paths cannot be
    # misinterpreted as children of the analysis repository.
    cmd=(datalad -C "$DS003745_ROOT" get -d . "sub-${sub}/anat" "sub-${sub}/func/*task-sharedreward*" "sub-${sub}/fmap")
    printf '%q ' "${cmd[@]}"; echo
    (( dry )) || "${cmd[@]}"
  done
else
  echo 'Dataset metadata pinned. Use one or more --subject values for selective pilot retrieval.'
fi
