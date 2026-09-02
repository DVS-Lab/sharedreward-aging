#!/usr/bin/env bash

# Run activation followed by seed PPI within each bounded run-level worker.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
usage() { echo "Usage: run_L1stats.sh --manifest FILE [--ppi-seed vs|--activation-only] [--jobs N] [--dry-run|--render-only] [--overwrite] [--log-dir DIR]" >&2; }
manifest=""; ppi_seed=vs; jobs=20; mode=run; overwrite=0; log_dir=""
while (( $# )); do
    case "$1" in
        --manifest) manifest="$2"; shift 2 ;; --ppi-seed) ppi_seed="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"; shift 2 ;;
        --activation-only) ppi_seed=""; shift ;; --jobs) jobs="$2"; shift 2 ;;
        --dry-run) mode=dry-run; shift ;; --render-only) mode=render-only; shift ;;
        --overwrite) overwrite=1; shift ;; --log-dir) log_dir="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;; *) echo "ERROR: unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done
[[ -f "$manifest" ]] || { echo "ERROR: manifest not found: $manifest" >&2; exit 1; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: --jobs must be positive" >&2; exit 2; }
units=()
while IFS= read -r unit || [[ -n "$unit" ]]; do units+=("$unit"); done < <(
    python3 "${SCRIPT_DIR}/read_l1_manifest.py" "$manifest"
)
(( ${#units[@]} )) || { echo "ERROR: no L1 work units" >&2; exit 1; }
printf 'Paired L1 plan: %d unit(s), jobs=%d, activation%s\n' "${#units[@]}" "$jobs" "$([[ -n "$ppi_seed" ]] && printf ' + PPI seed-%s' "$ppi_seed")"
if [[ -n "$log_dir" && "$mode" != dry-run ]]; then mkdir -p "$log_dir"; echo "Per-unit logs: $log_dir"; fi
pids=(); labels=(); logfiles=(); failures=0
wait_oldest() {
    local pid="${pids[0]}" label="${labels[0]}" logfile="${logfiles[0]}"
    if ! wait "$pid"; then echo "ERROR: failed paired L1 unit: $label${logfile:+ (log: $logfile)}" >&2; failures=$((failures+1)); else echo "DONE: $label"; fi
    pids=("${pids[@]:1}"); labels=("${labels[@]:1}"); logfiles=("${logfiles[@]:1}")
}
run_unit() {
    local dataset="$1" sub="$2" session="$3" run="$4" bold="$5" mask="$6" confounds="$7"
    local common=("$dataset" "$sub" "$session" "$run") options=(--bold "$bold" --mask "$mask" --confounds "$confounds")
    [[ "$mode" == dry-run ]] && options+=(--dry-run)
    [[ "$mode" == render-only ]] && options+=(--render-only)
    (( overwrite )) && options+=(--overwrite)
    bash "${SCRIPT_DIR}/L1stats.sh" "${common[@]}" 0 "${options[@]}"
    [[ -z "$ppi_seed" ]] || bash "${SCRIPT_DIR}/L1stats.sh" "${common[@]}" "$ppi_seed" "${options[@]}"
}
for unit in "${units[@]}"; do
    IFS='|' read -r dataset sub session run bold mask confounds <<< "$unit"
    label="${dataset} sub-${sub} ses-${session} run-${run}"
    if [[ "$mode" == dry-run ]]; then run_unit "$dataset" "$sub" "$session" "$run" "$bold" "$mask" "$confounds" || failures=$((failures+1)); continue; fi
    logfile=""
    if [[ -n "$log_dir" ]]; then
        logfile="${log_dir}/${dataset}_sub-${sub}_ses-${session}_task-sharedreward_run-${run}.log"
        echo "START: $label (log: $logfile)"; run_unit "$dataset" "$sub" "$session" "$run" "$bold" "$mask" "$confounds" >"$logfile" 2>&1 &
    else
        echo "START: $label"; run_unit "$dataset" "$sub" "$session" "$run" "$bold" "$mask" "$confounds" &
    fi
    pids+=("$!"); labels+=("$label"); logfiles+=("$logfile")
    (( ${#pids[@]} >= jobs )) && wait_oldest
done
while (( ${#pids[@]} )); do wait_oldest; done
(( failures == 0 )) || exit 1
