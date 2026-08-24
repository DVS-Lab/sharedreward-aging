#!/usr/bin/env bash

# Reproduce FEAT's SUSAN spatial-smoothing stage on an already preprocessed BOLD.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "${SCRIPT_DIR}/project_config.sh"
usage() { echo "Usage: smooth_with_feat_susan.sh --input FILE --mask FILE --output FILE --kernel-fwhm MM [--metadata-tsv FILE] [--work-dir DIR] [--overwrite]" >&2; }
input=""; mask=""; output=""; kernel=""; metadata=""; requested_work=""; overwrite=0
while (( $# )); do case "$1" in
  --input) input="$2"; shift 2 ;; --mask) mask="$2"; shift 2 ;; --output) output="$2"; shift 2 ;;
  --kernel-fwhm) kernel="$2"; shift 2 ;; --metadata-tsv) metadata="$2"; shift 2 ;;
  --work-dir) requested_work="$2"; shift 2 ;; --overwrite) overwrite=1; shift ;;
  -h|--help) usage; exit 0 ;; *) echo "ERROR: unknown argument: $1" >&2; usage; exit 2 ;;
esac; done
[[ -f "$input" && -f "$mask" && -n "$output" ]] || { usage; exit 2; }
[[ "$kernel" =~ ^[0-9]+([.][0-9]+)?$ ]] && awk -v x="$kernel" 'BEGIN{exit !(x>0)}' || { echo "ERROR: --kernel-fwhm must be positive" >&2; exit 2; }
label="$(printf '%s' "$kernel" | sed 's/\.0*$//; s/\./p/g')"
[[ "$(basename "$output")" == *"susanKernelFWHM${label}"* ]] || { echo "ERROR: output name must encode susanKernelFWHM${label}" >&2; exit 2; }
[[ "$output" != "$input" ]] || { echo "ERROR: input will not be overwritten" >&2; exit 2; }
if [[ -e "$output" && "$overwrite" -ne 1 ]]; then echo "ERROR: output exists; use --overwrite: $output" >&2; exit 1; fi
for cmd in fslmaths fslstats susan; do command -v "$cmd" >/dev/null || { echo "ERROR: $cmd is unavailable" >&2; exit 1; }; done
if [[ -n "$requested_work" ]]; then
  mkdir -p "$requested_work"; work_parent="$(cd "$requested_work" && pwd)"; work="$(mktemp -d "${work_parent}/susan.XXXXXX")"
else
  work="$(mktemp -d "${TMPDIR:-/tmp}/sharedreward-susan.XXXXXX")"
fi
trap 'rm -rf -- "$work"' EXIT
input_abs="$(cd "$(dirname "$input")" && pwd)/$(basename "$input")"
mask_abs="$(cd "$(dirname "$mask")" && pwd)/$(basename "$mask")"
mkdir -p "$(dirname "$output")"; output_abs="$(cd "$(dirname "$output")" && pwd)/$(basename "$output")"
masked="$work/prefiltered_func_data_thresh.nii.gz"; mean_func="$work/mean_func.nii.gz"
susan_raw="$work/prefiltered_func_data_smooth_raw.nii.gz"; final="$work/prefiltered_func_data_smooth.nii.gz"
fslmaths "$input_abs" -mas "$mask_abs" "$masked" -odt float
fslmaths "$masked" -Tmean "$mean_func"
median="$(fslstats "$input_abs" -k "$mask_abs" -p 50)"
awk -v x="$median" 'BEGIN{exit !(x+0>0)}' || { echo "ERROR: non-positive masked median: $median" >&2; exit 1; }
brightness="$(awk -v x="$median" 'BEGIN{printf "%.12g",0.75*x}')"
# FEAT exposes FWHM; SUSAN receives Gaussian sigma in mm (FWHM / 2.354820045).
sigma="$(awk -v x="$kernel" 'BEGIN{printf "%.12g",x/2.3548200450309493}')"
susan "$masked" "$brightness" "$sigma" 3 1 1 "$mean_func" "$brightness" "$susan_raw"
fslmaths "$susan_raw" -mas "$mask_abs" "$final" -odt float
[[ -s "$final" ]] || { echo "ERROR: SUSAN did not create output" >&2; exit 1; }
mv -f -- "$final" "$output_abs"
[[ -n "$metadata" ]] || metadata="${output_abs%.nii.gz}_susan.tsv"
mkdir -p "$(dirname "$metadata")"; tmp_metadata="$work/susan-metadata.tsv"
fsl_version="unknown"; [[ -n "${FSLDIR:-}" && -f "${FSLDIR}/etc/fslversion" ]] && fsl_version="$(tr -d '\n' < "${FSLDIR}/etc/fslversion")"
printf 'input\tmask\toutput\tkernel_fwhm_mm\tspatial_sigma_mm\tmasked_median\tbrightness_threshold\tfsl_version\n' > "$tmp_metadata"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$input_abs" "$mask_abs" "$output_abs" "$kernel" "$sigma" "$median" "$brightness" "$fsl_version" >> "$tmp_metadata"
mv -f -- "$tmp_metadata" "$metadata"
printf 'SUSAN kernel FWHM: %s mm\nSUSAN spatial sigma: %s mm\nMasked median: %s\nBrightness threshold: %s\nOutput: %s\nMetadata: %s\n' "$kernel" "$sigma" "$median" "$brightness" "$output_abs" "$metadata"
