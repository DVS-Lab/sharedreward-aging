# Code

Active Phase 0 utilities:

- `get_ds003745.sh`: clone/pin OpenNeuro ds003745 2.1.1 and selectively retrieve pilot files.
- `run_fmriprep_ds003745.sh`: fMRIPrep 25.2.5 single-subject wrapper, `MNI152NLin6Asym` only.
- `convert_harmonized_events.py`: source-preserving common full-trial event derivative for ds003745 or RF1.
- `summarize_events.py`: per-run timing/count QC.
- `resample_to_rf1_grid.sh` and `check_grid.py`: cubic BOLD/nearest-neighbor mask resampling and exact verification.
- `measure_smoothness.sh`, `smooth_to_target.sh`, and `compute_tsnr.py`: thin wrappers around the explicitly configured authoritative RF1 implementations, preventing metric drift.
- `harmonization_report.py`: compact Phase 0 summary; it does not select a target.
- `run_logged.sh`: local raw log plus a compact Git-trackable record for major Linux2 runs.

Default Temple roots live in `project_config.sh` and can be overridden explicitly. Large data remain outside Git. Use pilot subject lists, conservative fMRIPrep concurrency, and `--dry-run` before expensive processing.

Historical scripts/templates remain provenance only. The model-specific full-trial candidate is documented in `templates/README.md`; no pooled L3 is active.
