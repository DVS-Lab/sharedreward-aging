#!/usr/bin/env bash

# Run one fMRIPrep process per ds003745 participant with bounded concurrency.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
# shellcheck source=project_config.sh
source "$SCRIPT_DIR/project_config.sh"

usage() {
    echo "Usage: run_fmriprep_ds003745_batch.sh --manifest FILE [--jobs N] [--dry-run]" >&2
}

manifest=""
jobs=6
dry=0
while (( $# )); do
    case "$1" in
        --manifest) manifest="$2"; shift 2 ;;
        --jobs) jobs="$2"; shift 2 ;;
        --dry-run) dry=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: unknown argument: $1" >&2; usage; exit 2 ;;
    esac
done

[[ -n "$manifest" && -f "$manifest" ]] || {
    echo "ERROR: manifest not found: $manifest" >&2
    exit 1
}
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || {
    echo "ERROR: --jobs must be a positive integer" >&2
    exit 2
}

subjects=()
declare -A seen=()
while IFS=$'\t' read -r subject _; do
    subject="${subject#sub-}"
    [[ -z "$subject" || "$subject" == subject || "$subject" == \#* ]] && continue
    [[ -z "${seen[$subject]:-}" ]] || {
        echo "ERROR: duplicate subject in manifest: $subject" >&2
        exit 1
    }
    seen[$subject]=1
    subjects+=("$subject")
done < "$manifest"

(( ${#subjects[@]} )) || {
    echo "ERROR: manifest contains no participants" >&2
    exit 1
}

work=()
for subject in "${subjects[@]}"; do
    report="${DS003745_FMRIPREP_ROOT}/sub-${subject}.html"
    output="${DS003745_FMRIPREP_ROOT}/sub-${subject}"
    complete_count=0
    if [[ -d "$output" ]]; then
        complete_count="$(find "$output" -type f -name '*task-sharedreward*space-MNI152NLin6Asym*desc-preproc_bold.nii.gz' | wc -l)"
    fi
    if [[ -s "$report" && "$complete_count" -ge 2 ]]; then
        echo "SKIP COMPLETE: sub-${subject}"
    elif [[ -e "$output" || -e "$report" ]]; then
        echo "ERROR: incomplete existing output requires review: sub-${subject}" >&2
        exit 1
    else
        work+=("$subject")
    fi
done

printf 'ds003745 fMRIPrep batch plan: %d manifest participant(s), %d to run, jobs=%d\n' \
    "${#subjects[@]}" "${#work[@]}" "$jobs"
printf 'Per-subject resources: nprocs=%s, omp-nthreads=%s, mem=%s MB\n' \
    "${FMRIPREP_NPROCS:-16}" "${FMRIPREP_OMP_NTHREADS:-8}" "${FMRIPREP_MEM_MB:-48000}"

(( ${#work[@]} )) || {
    echo "CHECK PASSED: every manifest participant is already complete."
    exit 0
}

if (( dry )); then
    for subject in "${work[@]}"; do
        bash "$SCRIPT_DIR/run_fmriprep_ds003745.sh" "$subject" --dry-run
    done
    exit 0
fi

printf '%s\n' "${work[@]}" |
    xargs -P "$jobs" -n 1 bash "$SCRIPT_DIR/run_fmriprep_ds003745.sh"

echo "CHECK PASSED: all scheduled ds003745 fMRIPrep participants completed."
