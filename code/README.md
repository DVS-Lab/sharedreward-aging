# Code

Active Phase 0 utilities:

- `get_ds003745.sh`: clone/pin OpenNeuro ds003745 2.1.1 and selectively retrieve pilot files.
- `run_fmriprep_ds003745.sh`: fMRIPrep 25.2.5 single-subject wrapper, `MNI152NLin6Asym` only.
- `build_ds003745_runlist.py`: build a deterministic cohort runlist from the pinned participants table, with explicit exclusions.
- `run_fmriprep_ds003745_batch.sh`: bounded-concurrency, resumable batch wrapper that skips complete outputs and stops on incomplete existing outputs.
- `convert_harmonized_events.py`: source-preserving common full-trial event derivative for ds003745 or RF1.
- `summarize_events.py`: per-run timing/count QC.
- `resample_to_rf1_grid.sh` and `check_grid.py`: cubic BOLD/nearest-neighbor mask resampling and exact verification.
- `measure_smoothness.sh`, `smooth_to_target.sh`, and `compute_tsnr.py`: thin wrappers around the explicitly configured authoritative RF1 implementations, preventing metric drift.
- `harmonization_report.py`: compact Phase 0 summary; it does not select a target.
- `run_logged.sh`: local raw log plus a compact Git-trackable record for major Linux2 runs.

Default Temple roots live in `project_config.sh` and can be overridden explicitly. Large data remain outside Git. Use pilot subject lists, conservative fMRIPrep concurrency, and `--dry-run` before expensive processing.

The pinned OpenNeuro clone under `sourcedata/ds003745` is an independent
DataLad dataset inside a parent-Git-ignored directory. It is intentionally not
registered as a Git submodule or DataLad subdataset of this analysis repository.
This keeps source acquisition reproducible without annexing analysis outputs or
requiring a large-file content sibling for the GitHub repository. A broader
`datalad run`/superdataset migration should be a separate, deliberate change.

On Linux2, create the dedicated Phase 0 Python/DataLad environment from
`environment-phase0-linux2.yml`, then run `install_phase0_afni.sh` to install
the complete official AFNI `linux_ubuntu_24_64` command distribution into that
environment without editing shell dotfiles. This isolates DataLad, git-annex,
and AFNI from the base and FSL installations. The installer records the AFNI
archive URL and checksum. The fMRIPrep version remains independently pinned by
the Apptainer wrapper.

The Ubuntu 24 host must provide Motif's `libXm.so.4` runtime. Install the
Ubuntu `libxm4` package (from the Universe repository) before validating AFNI.
This is a host library required by AFNI's official Ubuntu 24 binaries, not a
Conda dependency.

For an active Phase 0 shell, prepend `afni-bin` and the environment `bin`
directory to `PATH`. Do not prepend the Conda environment's `lib` directory to
`LD_LIBRARY_PATH`: that can override the matching `libmri.so` shipped beside
the official AFNI binaries. The Ubuntu 24 build finds its bundled libraries via
its own runtime path.

Historical scripts/templates remain provenance only. The model-specific full-trial candidate is documented in `templates/README.md`; no pooled L3 is active.
