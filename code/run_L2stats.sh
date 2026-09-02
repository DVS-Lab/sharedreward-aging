#!/usr/bin/env bash

# Run paired activation and PPI fixed effects for every two-run subject.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
usage() { echo "Usage: run_L2stats.sh --manifest FILE [--ppi-seed vs|--activation-only] [--jobs N] [--dry-run|--render-only] [--overwrite] [--log-dir DIR]" >&2; }
manifest=""; ppi_seed=vs; jobs=20; mode=run; overwrite=0; log_dir=""
while (( $# )); do
    case "$1" in --manifest) manifest="$2"; shift 2 ;; --ppi-seed) ppi_seed="$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]')"; shift 2 ;; --activation-only) ppi_seed=""; shift ;; --jobs) jobs="$2"; shift 2 ;; --dry-run) mode=dry-run; shift ;; --render-only) mode=render-only; shift ;; --overwrite) overwrite=1; shift ;; --log-dir) log_dir="$2"; shift 2 ;; -h|--help) usage; exit 0 ;; *) echo "ERROR: unknown argument: $1" >&2; usage; exit 2 ;; esac
done
[[ -f "$manifest" ]] || { echo "ERROR: manifest not found: $manifest" >&2; exit 1; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: --jobs must be positive" >&2; exit 2; }
units=(); passthrough_log="$(mktemp "${TMPDIR:-/tmp}/sharedreward-l2-passthrough.XXXXXX")"; trap 'rm -f -- "$passthrough_log"' EXIT
while IFS= read -r unit || [[ -n "$unit" ]]; do units+=("$unit"); done < <(python3 "${SCRIPT_DIR}/read_l2_manifest.py" "$manifest" 2>"$passthrough_log")
passthrough_count="$(awk 'END {print NR+0}' "$passthrough_log")"
printf 'Paired L2 plan: %d fixed-effects unit(s), %d one-run passthrough(s), jobs=%d, activation%s\n' "${#units[@]}" "$passthrough_count" "$jobs" "$([[ -n "$ppi_seed" ]] && printf ' + PPI seed-%s' "$ppi_seed")"
if [[ -n "$log_dir" && "$mode" != dry-run ]]; then mkdir -p "$log_dir"; echo "Per-unit logs: $log_dir"; fi
pids=(); labels=(); logfiles=(); failures=0
wait_oldest() { local pid="${pids[0]}" label="${labels[0]}" logfile="${logfiles[0]}"; if ! wait "$pid"; then echo "ERROR: failed paired L2 unit: $label${logfile:+ (log: $logfile)}" >&2; failures=$((failures+1)); else echo "DONE: $label"; fi; pids=("${pids[@]:1}"); labels=("${labels[@]:1}"); logfiles=("${logfiles[@]:1}"); }
run_unit() {
    local dataset="$1" sub="$2" session="$3" run1="$4" run2="$5" options=()
    [[ "$mode" == dry-run ]] && options+=(--dry-run); [[ "$mode" == render-only ]] && options+=(--render-only); (( overwrite )) && options+=(--overwrite)
    bash "${SCRIPT_DIR}/L2stats.sh" "$dataset" "$sub" "$session" act "$run1" "$run2" "${options[@]}"
    [[ -z "$ppi_seed" ]] || bash "${SCRIPT_DIR}/L2stats.sh" "$dataset" "$sub" "$session" "ppi_seed-${ppi_seed}" "$run1" "$run2" "${options[@]}"
}
for unit in "${units[@]}"; do
    IFS='|' read -r dataset sub session run1 run2 <<< "$unit"; label="${dataset} sub-${sub} ses-${session}"
    if [[ "$mode" == dry-run ]]; then run_unit "$dataset" "$sub" "$session" "$run1" "$run2" || failures=$((failures+1)); continue; fi
    logfile=""; if [[ -n "$log_dir" ]]; then logfile="${log_dir}/${dataset}_sub-${sub}_ses-${session}_task-sharedreward.log"; echo "START: $label (log: $logfile)"; run_unit "$dataset" "$sub" "$session" "$run1" "$run2" >"$logfile" 2>&1 & else echo "START: $label"; run_unit "$dataset" "$sub" "$session" "$run1" "$run2" & fi
    pids+=("$!"); labels+=("$label"); logfiles+=("$logfile"); (( ${#pids[@]} >= jobs )) && wait_oldest
done
while (( ${#pids[@]} )); do wait_oldest; done
(( failures == 0 )) || exit 1
