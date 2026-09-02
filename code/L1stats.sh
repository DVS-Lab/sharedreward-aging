#!/usr/bin/env bash

# Render and run one pooled Shared Reward activation or seed-PPI FEAT model.

set -euo pipefail
export FSLSUB_PARALLEL="${FSLSUB_PARALLEL:-1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=project_config.sh
source "${SCRIPT_DIR}/project_config.sh"

usage() {
    cat >&2 <<'EOF'
Usage: L1stats.sh DATASET SUBJECT SESSION RUN PPI --bold FILE --mask FILE \
                  --confounds FILE [--dry-run|--render-only] [--overwrite]

PPI is 0/act or a seed name matching masks/seed-<name>.nii.gz.
SESSION is 01 for RF1 and none for ds003745.
EOF
}

(( $# >= 5 )) || { usage; exit 2; }
dataset="$1"; sub="$(normalize_subject "$2")"; session="$(normalize_session "$3")"
run="$((10#$4))"; ppi="$5"; shift 5
bold=""; run_mask=""; confounds=""; mode=run; overwrite=0
while (( $# )); do
    case "$1" in
        --bold) bold="$2"; shift 2 ;;
        --mask) run_mask="$2"; shift 2 ;;
        --confounds) confounds="$2"; shift 2 ;;
        --dry-run) mode=dry-run; shift ;;
        --render-only) mode=render-only; shift ;;
        --overwrite) overwrite=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done
case "$dataset" in rf1|ds003745) ;; *) echo "ERROR: unsupported dataset: $dataset" >&2; exit 2 ;; esac
[[ -n "$bold" && -n "$run_mask" && -n "$confounds" ]] || { echo "ERROR: --bold, --mask, and --confounds are required" >&2; exit 2; }
type="$(analysis_type_from_ppi "$ppi")"
ncopes="$(cope_count_for_type "$type")" || { echo "ERROR: unsupported analysis type: $type" >&2; exit 2; }
directory="$(unit_directory "$dataset" "$sub" "$session")"
output="$(l1_output_base "$dataset" "$sub" "$session" "$run" "$type")"
ev_dir="$(ev_directory "$dataset" "$sub" "$session" "$run")"
missed_ev="${ev_dir}/missed_trial.txt"; missed_shape=10
[[ -s "$missed_ev" ]] && missed_shape=3
conditions=(
    event_computer_punish event_computer_reward
    event_friend_punish event_friend_reward
    event_stranger_punish event_stranger_reward
    event_computer_neutral event_friend_neutral event_stranger_neutral
)
[[ -f "$bold" ]] || { echo "ERROR: BOLD input not found: $bold" >&2; exit 1; }
[[ -f "$run_mask" ]] || { echo "ERROR: run mask not found: $run_mask" >&2; exit 1; }
[[ -s "$confounds" ]] || { echo "ERROR: FSL confounds missing or empty: $confounds" >&2; exit 1; }
for condition in "${conditions[@]}"; do
    [[ -s "${ev_dir}/${condition}.txt" ]] || { echo "ERROR: substantive EV missing or empty: ${ev_dir}/${condition}.txt" >&2; exit 1; }
done
source_template="${PROJECT_ROOT}/templates/L1_task-sharedreward_model-1_type-act_seed-0_HPC.fsf"
template_type=act
if [[ "$type" == ppi_seed-* ]]; then
    source_template="${PROJECT_ROOT}/templates/L1_task-sharedreward_model-1_type-ppi_seed-VS_HPC.fsf"
    template_type=ppi
fi
printf 'L1 plan\n  dataset: %s\n  BOLD: %s\n  confounds: %s\n  EV directory: %s\n  source template: %s\n  output: %s.feat\n' \
    "$dataset" "$bold" "$confounds" "$ev_dir" "$source_template" "$output"
[[ "$type" == ppi_seed-* ]] && printf '  seed: %s\n' "${PROJECT_ROOT}/masks/seed-${type#ppi_seed-}.nii.gz"
[[ "$mode" == dry-run ]] && exit 0

for command in fslnvols fslval; do
    command -v "$command" >/dev/null || { echo "ERROR: $command is unavailable; load FSL." >&2; exit 1; }
done
nvolumes="$(fslnvols "$bold")"
[[ "$nvolumes" =~ ^[0-9]+$ ]] || { echo "ERROR: invalid BOLD volume count: $nvolumes" >&2; exit 1; }
tr_seconds="$(fslval "$bold" pixdim4)"
[[ "$tr_seconds" =~ ^[0-9]+([.][0-9]+)?$ ]] || { echo "ERROR: invalid BOLD TR: $tr_seconds" >&2; exit 1; }
confound_rows="$(awk 'NF {n++} END {print n+0}' "$confounds")"
[[ "$confound_rows" -eq "$nvolumes" ]] || { echo "ERROR: confound rows ($confound_rows) != BOLD volumes ($nvolumes)" >&2; exit 1; }
feat_dir="${output}.feat"
if [[ -e "$feat_dir" ]]; then
    if (( ! overwrite )); then
        if [[ -f "$feat_dir/cluster_mask_zstat1.nii.gz" && -f "$feat_dir/stats/cope${ncopes}.nii.gz" ]]; then
            echo "Complete output already exists; skipping: $feat_dir"; exit 0
        fi
        echo "ERROR: incomplete output exists: $feat_dir (use --overwrite)." >&2; exit 1
    fi
    case "$feat_dir" in "${FSL_DERIVATIVES_ROOT}"/*) rm -rf -- "$feat_dir" ;; *) echo "ERROR: refusing removal outside FSL_DERIVATIVES_ROOT" >&2; exit 1 ;; esac
fi
mkdir -p "$directory"

geometry_signature() {
    local image="$1" key
    for key in dim1 dim2 dim3 pixdim1 pixdim2 pixdim3; do printf '%s ' "$(fslval "$image" "$key")"; done
}

prepare_seed() {
    local source="$1" seed="$2" cached reference
    [[ -f "$source" ]] || { echo "ERROR: seed mask not found: $source" >&2; return 1; }
    if [[ "$(geometry_signature "$source")" == "$(geometry_signature "$bold")" ]]; then
        printf '%s\n' "$source"; return 0
    fi
    for command in fslroi flirt; do command -v "$command" >/dev/null || { echo "ERROR: $command is needed to resample the seed." >&2; return 1; }; done
    cached="${FSL_DERIVATIVES_ROOT}/resampled_masks/${dataset}/sub-${sub}/seed-${seed}_space-RF1Grid.nii.gz"
    mkdir -p "$(dirname "$cached")"
    if [[ -f "$cached" && ! "$source" -nt "$cached" && "$(geometry_signature "$cached")" == "$(geometry_signature "$bold")" ]]; then
        printf '%s\n' "$cached"; return 0
    fi
    reference="${cached%.nii.gz}_reference.nii.gz"
    fslroi "$bold" "$reference" 0 1
    flirt -in "$source" -ref "$reference" -applyxfm -usesqform -interp nearestneighbour -out "$cached"
    rm -f -- "$reference"
    [[ "$(geometry_signature "$cached")" == "$(geometry_signature "$bold")" ]] || { echo "ERROR: resampled seed geometry mismatch" >&2; return 1; }
    printf '%s\n' "$cached"
}

phys=""
if [[ "$type" == ppi_seed-* ]]; then
    seed="${type#ppi_seed-}"
    phys="${directory}/ts_task-sharedreward_mask-${seed}_run-${run}.txt"
    if [[ "$mode" != render-only ]]; then
        command -v fslmeants >/dev/null || { echo "ERROR: fslmeants is unavailable; load FSL." >&2; exit 1; }
        seed_mask="$(prepare_seed "${PROJECT_ROOT}/masks/seed-${seed}.nii.gz" "$seed")"
        fslmeants -i "$bold" -o "$phys" -m "$seed_mask"
        [[ "$(awk 'NF {n++} END {print n+0}' "$phys")" -eq "$nvolumes" ]] || { echo "ERROR: seed time-series length mismatch: $phys" >&2; exit 1; }
    fi
fi

rendered="${directory}/L1_${dataset}_sub-${sub}_task-sharedreward_model-fulltrial_type-${type}_run-${run}.fsf"
pooled="$(mktemp "${TMPDIR:-/tmp}/sharedreward-pooled.XXXXXX.fsf")"
trap 'rm -f -- "$pooled"' EXIT
python3 "${SCRIPT_DIR}/render_pooled_fsf.py" --type "$template_type" --source "$source_template" --output "$pooled"
sed_escape() { printf '%s' "$1" | sed 's/[&@\\]/\\&/g'; }
sed_args=(
    -e "s@OUTPUT@$(sed_escape "$output")@g"
    -e "s@DATA@$(sed_escape "$bold")@g"
    -e "s@EVDIR@$(sed_escape "${ev_dir}/")@g"
    -e "s@MISSED_TRIAL@$(sed_escape "$missed_ev")@g"
    -e "s@SHAPE_EV@${missed_shape}@g"
    -e "s@CONFOUNDEVS@$(sed_escape "$confounds")@g"
    -e "s@NVOLUMES@${nvolumes}@g"
    -e "s@TR_INFO@${tr_seconds}@g"
)
[[ -n "$phys" ]] && sed_args+=( -e "s@PHYS@$(sed_escape "$phys")@g" )
sed "${sed_args[@]}" "$pooled" > "$rendered"
if grep -En 'OUTPUT|DATA|EVDIR|MISSED_TRIAL|SHAPE_EV|CONFOUNDEVS|NVOLUMES|TR_INFO|PHYS' "$rendered" >/dev/null; then
    echo "ERROR: unresolved placeholder in rendered template: $rendered" >&2; exit 1
fi
echo "Rendered: $rendered"
[[ "$mode" == render-only ]] && exit 0
command -v feat >/dev/null || { echo "ERROR: feat is unavailable; load FSL." >&2; exit 1; }
feat "$rendered"
[[ -n "${FSLDIR:-}" && -f "${FSLDIR}/etc/flirtsch/ident.mat" ]] || { echo "ERROR: FSLDIR/ident.mat unavailable." >&2; exit 1; }
mkdir -p "$feat_dir/reg"
ln -sfn "${FSLDIR}/etc/flirtsch/ident.mat" "$feat_dir/reg/example_func2standard.mat"
ln -sfn "${FSLDIR}/etc/flirtsch/ident.mat" "$feat_dir/reg/standard2example_func.mat"
ln -sfn "$feat_dir/mean_func.nii.gz" "$feat_dir/reg/standard.nii.gz"
rm -f -- "$feat_dir/stats/res4d.nii.gz" "$feat_dir/stats/corrections.nii.gz" \
    "$feat_dir/stats/threshac1.nii.gz" "$feat_dir/filtered_func_data.nii.gz"
[[ -f "$feat_dir/cluster_mask_zstat1.nii.gz" && -f "$feat_dir/stats/cope${ncopes}.nii.gz" ]] || { echo "ERROR: FEAT output is incomplete: $feat_dir" >&2; exit 1; }
