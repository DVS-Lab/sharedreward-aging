#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash_scripts=(
    project_config.sh get_ds003745.sh run_fmriprep_ds003745.sh
    run_fmriprep_ds003745_batch.sh resample_to_rf1_grid.sh
    measure_smoothness.sh smooth_to_target.sh smooth_with_feat_susan.sh
    run_logged.sh install_phase0_afni.sh validate_workflow.sh
    L1stats.sh run_L1stats.sh L2stats.sh run_L2stats.sh
)
for script in "${bash_scripts[@]}"; do bash -n "$ROOT/code/$script"; done
echo 'PASS: bash syntax'

python_scripts=(
    audit_analysis_qc.py audit_event_qc.py audit_fmriprep_ds003745.py
    audit_fsl_confounds.py audit_outputs.py audit_ratings_qc.py
    audit_resampling.py audit_smoothness.py audit_target_smoothing.py
    audit_susan_comparison.py build_analysis_cohort.py
    build_analysis_qc_manifest.py build_characterization_manifest.py
    build_ds003745_runlist.py build_event_qc_manifest.py
    build_fsl_confounds_manifest.py build_ratings_qc_manifest.py
    build_resampling_manifest.py build_susan_comparison_manifest.py
    build_target_smoothing_manifest.py check_grid.py compute_tsnr.py
    convert_harmonized_events.py create_common_analysis_mask.py
    create_coverage_eligible_mask.py generate_fsl_confounds.py
    generate_l1_evs.py harmonization_report.py plot_analysis_qc.py
    plot_coverage_mosaics.py plot_smoothness_comparison.py
    read_l1_manifest.py read_l2_manifest.py render_pooled_fsf.py
    render_pooled_l2_fsf.py run_analysis_qc_batch.py
    run_event_qc_batch.py run_fsl_confounds_batch.py
    run_resampling_batch.py run_smoothness_batch.py
    run_susan_comparison.py run_target_smoothing_batch.py summarize_events.py
)
python_paths=()
for script in "${python_scripts[@]}"; do python_paths+=("$ROOT/code/$script"); done
PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/sharedreward-aging-pycache" \
    python3 -m py_compile "${python_paths[@]}"
echo 'PASS: Python syntax'

if grep -En 'computer_non-faceclea|featwatcher_yn\) 1' \
    "$ROOT/code/project_config.sh" "$ROOT/code/convert_harmonized_events.py"; then
    echo 'ERROR: active typo/watcher found' >&2
    exit 1
fi
python3 -m unittest discover -s "$ROOT/tests" -v
