#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
DS003745_ROOT="${DS003745_ROOT:-${PROJECT_ROOT}/sourcedata/ds003745}"
DS003745_FMRIPREP_ROOT="${DS003745_FMRIPREP_ROOT:-${PROJECT_ROOT}/derivatives/fmriprep}"
HARMONIZED_ROOT="${HARMONIZED_ROOT:-${PROJECT_ROOT}/derivatives/harmonized}"
QC_ROOT="${QC_ROOT:-${PROJECT_ROOT}/derivatives/qc}"
FSL_DERIVATIVES_ROOT="${FSL_DERIVATIVES_ROOT:-${PROJECT_ROOT}/derivatives/fsl}"
EVFILES_ROOT="${EVFILES_ROOT:-${FSL_DERIVATIVES_ROOT}/EVfiles}"
RF1_SHAREDREWARD_ROOT="${RF1_SHAREDREWARD_ROOT:-/ZPOOL/data/projects/rf1-sra-sharedreward}"
RF1_SRA_LINUX2_ROOT="${RF1_SRA_LINUX2_ROOT:-/ZPOOL/data/projects/rf1-sra-linux2}"
RF1_SRA_SOURCE_ROOT="${RF1_SRA_SOURCE_ROOT:-/ZPOOL/data/projects/rf1-sra}"
RF1_RATINGS_ROOT="${RF1_RATINGS_ROOT:-${RF1_SRA_SOURCE_ROOT}/stimuli/Scan-Card_Guessing_Game/logs}"
REFERENCE_GRID="${REFERENCE_GRID:-${RF1_SHAREDREWARD_ROOT}/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz}"
TSNR_REFERENCE_MASK="${TSNR_REFERENCE_MASK:-${PROJECT_ROOT}/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.nii.gz}"
COVERAGE_EXEMPTION_MASK="${COVERAGE_EXEMPTION_MASK:-${PROJECT_ROOT}/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageExemption_mask.nii.gz}"
COVERAGE_ELIGIBLE_MASK="${COVERAGE_ELIGIBLE_MASK:-${PROJECT_ROOT}/resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-coverageEligible_mask.nii.gz}"
# Backward-compatible name for commands that predate the distinct coverage denominator.
COMMON_ANALYSIS_MASK="${COMMON_ANALYSIS_MASK:-${TSNR_REFERENCE_MASK}}"
# Approved 2026-08-23 after complete RF1/ds003745 characterization.
# This is total measured classic FWHM, not an added 6-mm kernel.
TARGET_FWHM_MM="${TARGET_FWHM_MM:-6}"
FMRIPREP_IMAGE="${FMRIPREP_IMAGE:-/ZPOOL/data/tools/fmriprep-25.2.5.simg}"
TEMPLATEFLOW_HOME="${TEMPLATEFLOW_HOME:-/ZPOOL/data/tools/templateflow}"
FS_LICENSE_FILE="${FS_LICENSE_FILE:-/ZPOOL/data/tools/licenses/fs_license.txt}"

normalize_subject() { local value="${1#sub-}"; printf '%s\n' "$value"; }
normalize_session() {
    local value="${1#ses-}"
    [[ -n "$value" && "$value" != none ]] && printf '%s\n' "$value" || printf 'none\n'
}

analysis_type_from_ppi() {
    local ppi="$1"
    if [[ "$ppi" == 0 || "$ppi" == act ]]; then
        printf 'act\n'
    else
        printf 'ppi_seed-%s\n' "$(printf '%s' "$ppi" | tr '[:upper:]' '[:lower:]')"
    fi
}

cope_count_for_type() {
    case "$1" in
        act) printf '28\n' ;;
        ppi_seed-*) printf '29\n' ;;
        *) return 1 ;;
    esac
}

unit_directory() {
    local dataset="$1" subject="$2" session="$3"
    local directory="${FSL_DERIVATIVES_ROOT}/${dataset}/sub-${subject}"
    [[ "$session" != none ]] && directory="${directory}/ses-${session}"
    printf '%s\n' "$directory"
}

l1_output_base() {
    local dataset="$1" subject="$2" session="$3" run="$4" type="$5"
    printf '%s/L1_task-sharedreward_model-fulltrial_type-%s_run-%s_sm-6\n' \
        "$(unit_directory "$dataset" "$subject" "$session")" "$type" "$run"
}

l2_output_base() {
    local dataset="$1" subject="$2" session="$3" type="$4"
    printf '%s/L2_task-sharedreward_model-fulltrial_type-%s_sm-6\n' \
        "$(unit_directory "$dataset" "$subject" "$session")" "$type"
}

ev_directory() {
    local dataset="$1" subject="$2" session="$3" run="$4"
    local directory="${EVFILES_ROOT}/${dataset}/sub-${subject}"
    [[ "$session" != none ]] && directory="${directory}/ses-${session}"
    printf '%s/sharedreward/run-%s\n' "$directory" "$run"
}
