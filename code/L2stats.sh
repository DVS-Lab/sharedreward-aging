#!/usr/bin/env bash

# Combine two eligible Shared Reward runs with FSL fixed effects.

set -euo pipefail
export FSLSUB_PARALLEL="${FSLSUB_PARALLEL:-1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=project_config.sh
source "${SCRIPT_DIR}/project_config.sh"
usage() { echo "Usage: L2stats.sh DATASET SUBJECT SESSION TYPE RUN1 RUN2 [--dry-run|--render-only] [--overwrite]" >&2; }
(( $# >= 6 )) || { usage; exit 2; }
dataset="$1"; sub="$(normalize_subject "$2")"; session="$(normalize_session "$3")"; type="$4"; run1="$((10#$5))"; run2="$((10#$6))"; shift 6
mode=run; overwrite=0
while (( $# )); do
    case "$1" in --dry-run) mode=dry-run; shift ;; --render-only) mode=render-only; shift ;; --overwrite) overwrite=1; shift ;; -h|--help) usage; exit 0 ;; *) echo "ERROR: unknown argument: $1" >&2; exit 2 ;; esac
done
ncopes="$(cope_count_for_type "$type")" || { echo "ERROR: unsupported type: $type" >&2; exit 2; }
case "$type" in act) template_type=act ;; ppi_seed-*) template_type=ppi ;; esac
input1="$(l1_output_base "$dataset" "$sub" "$session" "$run1" "$type").feat"
input2="$(l1_output_base "$dataset" "$sub" "$session" "$run2" "$type").feat"
for input in "$input1" "$input2"; do
    [[ -f "$input/cluster_mask_zstat1.nii.gz" && -f "$input/stats/cope${ncopes}.nii.gz" ]] || { echo "ERROR: complete L1 input required: $input" >&2; exit 1; }
done
output="$(l2_output_base "$dataset" "$sub" "$session" "$type")"
directory="$(unit_directory "$dataset" "$sub" "$session")"
rendered="${directory}/L2_${dataset}_sub-${sub}_task-sharedreward_model-fulltrial_type-${type}.fsf"
printf 'L2 plan (fixed effects)\n  dataset: %s\n  run %s: %s\n  run %s: %s\n  output: %s.gfeat\n  FSLSUB_PARALLEL: %s\n' "$dataset" "$run1" "$input1" "$run2" "$input2" "$output" "$FSLSUB_PARALLEL"
[[ "$mode" == dry-run ]] && exit 0
gfeat="${output}.gfeat"
if [[ -e "$gfeat" ]]; then
    if (( ! overwrite )); then
        if [[ -f "$gfeat/cope${ncopes}.feat/cluster_mask_zstat1.nii.gz" ]]; then echo "Complete output already exists; skipping: $gfeat"; exit 0; fi
        echo "ERROR: incomplete output exists: $gfeat (use --overwrite)." >&2; exit 1
    fi
    case "$gfeat" in "${FSL_DERIVATIVES_ROOT}"/*) rm -rf -- "$gfeat" ;; *) echo "ERROR: refusing removal outside FSL_DERIVATIVES_ROOT" >&2; exit 1 ;; esac
fi
mkdir -p "$directory"
pooled="$(mktemp "${TMPDIR:-/tmp}/sharedreward-l2.XXXXXX.fsf")"
trap 'rm -f -- "$pooled"' EXIT
python3 "${SCRIPT_DIR}/render_pooled_l2_fsf.py" --type "$template_type" --output "$pooled"
sed_escape() { printf '%s' "$1" | sed 's/[&@\\]/\\&/g'; }
sed -e "s@OUTPUT@$(sed_escape "$output")@g" -e "s@INPUT1@$(sed_escape "$input1")@g" -e "s@INPUT2@$(sed_escape "$input2")@g" "$pooled" > "$rendered"
if grep -En 'OUTPUT|INPUT1|INPUT2' "$rendered" >/dev/null; then echo "ERROR: unresolved placeholder: $rendered" >&2; exit 1; fi
echo "Rendered: $rendered"
[[ "$mode" == render-only ]] && exit 0
command -v feat >/dev/null || { echo "ERROR: feat is unavailable; load FSL." >&2; exit 1; }
feat "$rendered"
for cope in $(seq "$ncopes"); do
    cope_dir="$gfeat/cope${cope}.feat"
    rm -f -- "$cope_dir/stats/res4d.nii.gz" "$cope_dir/stats/corrections.nii.gz" "$cope_dir/stats/threshac1.nii.gz" "$cope_dir/filtered_func_data.nii.gz" "$cope_dir/var_filtered_func_data.nii.gz"
done
[[ -f "$gfeat/cope${ncopes}.feat/cluster_mask_zstat1.nii.gz" ]] || { echo "ERROR: fixed-effects output is incomplete: $gfeat" >&2; exit 1; }
