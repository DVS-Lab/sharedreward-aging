#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
DS003745_ROOT="${DS003745_ROOT:-${PROJECT_ROOT}/sourcedata/ds003745}"
DS003745_FMRIPREP_ROOT="${DS003745_FMRIPREP_ROOT:-${PROJECT_ROOT}/derivatives/fmriprep}"
HARMONIZED_ROOT="${HARMONIZED_ROOT:-${PROJECT_ROOT}/derivatives/harmonized}"
QC_ROOT="${QC_ROOT:-${PROJECT_ROOT}/derivatives/qc}"
RF1_SHAREDREWARD_ROOT="${RF1_SHAREDREWARD_ROOT:-/ZPOOL/data/projects/rf1-sra-sharedreward}"
RF1_SRA_LINUX2_ROOT="${RF1_SRA_LINUX2_ROOT:-/ZPOOL/data/projects/rf1-sra-linux2}"
REFERENCE_GRID="${REFERENCE_GRID:-${RF1_SHAREDREWARD_ROOT}/resources/rf1_MNI152NLin6Asym_reference_grid.nii.gz}"
# Approved 2026-08-23 after complete RF1/ds003745 characterization.
# This is total measured classic FWHM, not an added 6-mm kernel.
TARGET_FWHM_MM="${TARGET_FWHM_MM:-6}"
FMRIPREP_IMAGE="${FMRIPREP_IMAGE:-/ZPOOL/data/tools/fmriprep-25.2.5.simg}"
TEMPLATEFLOW_HOME="${TEMPLATEFLOW_HOME:-/ZPOOL/data/tools/templateflow}"
FS_LICENSE_FILE="${FS_LICENSE_FILE:-/ZPOOL/data/tools/licenses/fs_license.txt}"
