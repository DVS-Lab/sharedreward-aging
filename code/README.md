# Code

Active Phase 0 utilities:

- `get_ds003745.sh`: clone/pin OpenNeuro ds003745 2.1.1 and selectively retrieve pilot files.
- `run_fmriprep_ds003745.sh`: fMRIPrep 25.2.5 single-subject wrapper, `MNI152NLin6Asym` only.
- `build_ds003745_runlist.py`: build a deterministic cohort runlist from the pinned participants table, with explicit exclusions.
- `run_fmriprep_ds003745_batch.sh`: bounded-concurrency, resumable batch wrapper that skips complete outputs and stops on incomplete existing outputs.
- `audit_fmriprep_ds003745.py`: audit both Shared Reward runs, masks, confounds, and participant reports; optionally emit a retry manifest.
- `convert_harmonized_events.py`: source-preserving common full-trial event derivative for ds003745 or RF1.
- `summarize_events.py`: per-run timing/count QC.
- `resample_to_rf1_grid.sh` and `check_grid.py`: identity-grid `wsinc5` BOLD/nearest-neighbor mask resampling and exact verification.
- `build_resampling_manifest.py`, `run_resampling_batch.py`, and `audit_resampling.py`: deterministic run-level planning, bounded/restartable RF1-grid resampling, and independent cohort completeness QC.
- `build_characterization_manifest.py`, `run_smoothness_batch.py`, and `audit_smoothness.py`: one frozen cross-dataset input contract, bounded/restartable AFNI baseline measurement, and a consolidated run-level audit table.
- `measure_smoothness.sh`, `smooth_to_target.sh`, and `compute_tsnr.py`: thin wrappers around the explicitly configured authoritative RF1 implementations, preventing metric drift.
- `harmonization_report.py`: compact Phase 0 summary including the approved target status.
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

## RF1-grid resampling

Continuous BOLD is already normalized to MNI152NLin6Asym space. It is moved onto the exact RF1 grid by applying an identity transform with `3dAllineate -final wsinc5`; this avoids introducing an additional spatial transform and reduces interpolation blur relative to cubic interpolation. Binary masks use nearest-neighbor `3dresample`.

After the RF1 reference resource exists and the ds003745 fMRIPrep audit is complete, build the frozen run-level contract before launching any resampling:

```bash
python3 code/build_resampling_manifest.py \
  --output logs/runlists/ds003745-resampling-ready.tsv \
  --missing-output logs/runlists/ds003745-resampling-missing.tsv
```

The complete ds003745 cohort should produce 100 ready run units and zero missing units. Preview, run, and audit through `code/run_logged.sh`; use a unique per-unit log directory for each launch. Existing outputs are checked against the reference and skipped, so an interrupted batch is safely restartable. `--overwrite` is intentionally explicit and should be used only after reviewing an invalid existing derivative.

## Baseline smoothness characterization

After the independent 100-run resampling audit passes, build the cross-dataset manifest. It contains one RF1 pre-resampling row per canonical Shared Reward BOLD, plus paired ds003745 pre-resampling and post-resampling/pre-blur rows:

```bash
python3 code/build_characterization_manifest.py \
  --output logs/runlists/phase0-characterization-ready.tsv \
  --missing-output logs/runlists/phase0-characterization-missing.tsv
```

The RF1 rows reference the authoritative Tedana-plus-confounds files under `rf1-sra-linux2/derivatives/fsl/confounds_tedana`; this repository does not copy them. The current cohort should produce 865 units: 665 RF1 pre-resampling, 100 ds003745 pre-resampling, and 100 ds003745 post-resampling/pre-blur.

Long batches should be launched through both `run_logged.sh` and `nohup`, with an explicit outer launcher log, so they survive an SSH disconnect:

```bash
nohup bash code/run_logged.sh \
  --label phase0-baseline-smoothness-full \
  --include-full-log -- \
  python3 code/run_smoothness_batch.py \
    --manifest logs/runlists/phase0-characterization-ready.tsv \
    --jobs 8 \
    --output-dir derivatives/qc/smoothness/run-level \
    --log-dir logs/smoothness-current \
    --work-root work/phase0-smoothness \
  > logs/phase0-baseline-smoothness-full.nohup 2>&1 </dev/null &
```

`run_smoothness_batch.py` delegates every unit to the authoritative RF1 `measure_smoothness.sh`, uses isolated AFNI work directories, writes one atomic result per unit, and verifies existing results before restart skips. Re-running the same command after interruption validates and skips completed units. `audit_smoothness.py` creates the Git-trackable consolidated table used for target evaluation. It records classic Gaussian and ACF estimates. Phase 0 approved a 6-mm total classic-FWHM target on 2026-08-23.
