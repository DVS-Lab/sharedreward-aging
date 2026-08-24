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
- `build_target_smoothing_manifest.py`, `run_target_smoothing_batch.py`, and `audit_target_smoothing.py`: the analysis-ready 6-mm contract, bounded/restartable target smoothing, and independent geometry plus achieved-smoothness audit.
- `smooth_with_feat_susan.sh`, `build_susan_comparison_manifest.py`, `run_susan_comparison.py`, and `audit_susan_comparison.py`: a non-production control reproducing FEAT's 6-mm SUSAN stage and measuring baseline, AFNI total-target, and SUSAN fixed-kernel outputs with the same AFNI estimator.
- `plot_smoothness_comparison.py`: the tracked mean ± run-level SEM comparison of baseline, AFNI-total-target, and FEAT-equivalent SUSAN smoothness.
- `create_common_analysis_mask.py`: nearest-neighbor resampling of the TemplateFlow MNI152NLin6Asym brain mask onto the exact RF1 reference grid.
- `build_analysis_qc_manifest.py`, `run_analysis_qc_batch.py`, `audit_analysis_qc.py`, and `plot_analysis_qc.py`: frozen/restartable post-smoothing tSNR, motion, fixed-mask coverage, review flags, subject summaries, and plots.
- `build_event_qc_manifest.py`, `run_event_qc_batch.py`, and `audit_event_qc.py`: source-preserving full-trial conversion, condition counts, missed-trial exclusions, and run-to-subject usability aggregation.
- `measure_smoothness.sh`, `smooth_to_target.sh`, and `compute_tsnr.py`: thin wrappers around the explicitly configured authoritative RF1 implementations, preventing metric drift. tSNR uses the fixed common-mask/run-mask intersection and reports coverage against the fixed mask.
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

## Production target smoothing

Build the production contract from the frozen characterization manifest. Only RF1 `pre_resample` and ds003745 `post_resample_preblur` rows are selected; each derivative is written in its owning repository.

```bash
python3 code/build_target_smoothing_manifest.py \
  --output logs/runlists/target-smoothing-6mm-ready.tsv \
  --missing-output logs/runlists/target-smoothing-6mm-missing.tsv
```

The current cohort should contain 765 units: 665 RF1 and 100 ds003745. Launch with bounded AFNI concurrency and an SSH-safe outer log:

```bash
nohup bash code/run_logged.sh \
  --label phase0-target-smoothing-6mm-full \
  --include-full-log -- \
  python3 code/run_target_smoothing_batch.py \
    --manifest logs/runlists/target-smoothing-6mm-ready.tsv \
    --jobs 8 \
    --log-dir logs/target-smoothing-6mm-current \
    --work-root work/target-smoothing-6mm \
  --check \
  python3 code/audit_target_smoothing.py \
    --manifest logs/runlists/target-smoothing-6mm-ready.tsv \
    --output logs/records/target-smoothing-6mm-audit.tsv \
    --missing-output logs/records/target-smoothing-6mm-missing.tsv \
    --fail-on-incomplete \
  > logs/phase0-target-smoothing-6mm-full.nohup 2>&1 </dev/null &
```

The runner validates existing output/QC pairs before skipping them, so the same command is restartable. Partial or invalid pairs stop with an explicit request to review and use `--overwrite`; they are never silently replaced. The audit requires output/mask geometry agreement and achieved classic combined FWHM within AFNI's documented ±10% approximation tolerance, while retaining the complete ACF diagnostics. A run outside that tolerance can pass only through an exact row in `docs/smoothing_qc_exceptions.tsv`, with the expected target, a narrow accepted measurement range, rationale, and an existing tracked evidence record; this never waives geometry or other QC failures.

AFNI normally chooses a subset of blurmaster volumes for speed. If a reviewed run repeatedly passes AFNI's internal stopping rule but the independent all-volume `3dFWHMx` audit falls outside tolerance, a one-row retry may add `--all-blurmaster --overwrite`. This passes AFNI `-bmall`, making convergence use every volume. It is an exception mechanism, not the cohort default; the run record must document its use.

## AFNI total-target versus FEAT SUSAN control

FEAT's smoothing field is expressed as FWHM, but its generated `susan` command receives spatial sigma in millimeters: `FWHM / sqrt(8 ln 2)`, so 6 mm becomes 2.54777 mm. FEAT also uses a brightness threshold equal to 75% of the masked median, a temporal mean image as the one USAN image, 3D processing, median fallback, and a final brain-mask application. `smooth_with_feat_susan.sh` reproduces that stage directly on the already motion-corrected analysis BOLD; it deliberately does not repeat MCFLIRT, BET, intensity normalization, or temporal filtering.

This is not an equivalence test between two spellings of the same operation. AFNI `3dBlurToFWHM -FWHM 6` targets approximately 6 mm **total measured** classic smoothness. FEAT applies a nominal 6-mm SUSAN kernel to an already smooth image. For an ideal Gaussian kernel, the latter total is approximately `sqrt(baseline^2 + 6^2)`. The pilot measures the nonlinear SUSAN result empirically with the same `3dFWHMx` command used for the AFNI output.

The comparison manifest defaults to the highest-baseline analysis-ready run from each dataset. `--scope all` generalizes the same contract to the 765 analysis-ready inputs: 665 RF1 runs plus 100 post-`wsinc5` ds003745 runs. The 865-row characterization table additionally contains the same 100 ds003745 runs on their unused native fMRIPrep grid; those rows are intentionally excluded from the production-method comparison. Comparison derivatives are target/method encoded and separate from production inputs.

Build and launch the two-run pilot after the 6-mm target manifest exists. The selected runs are currently RF1 sub-11720/ses-01/run-1 and ds003745 sub-118/run-02.

```bash
python3 code/build_susan_comparison_manifest.py \
  --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv \
  --scope pilot \
  --kernel-fwhm 6 \
  --output logs/runlists/susan-vs-afni-6mm-pilot.tsv \
  --missing-output logs/runlists/susan-vs-afni-6mm-pilot-missing.tsv

nohup bash code/run_logged.sh \
  --label phase0-susan-vs-afni-6mm-pilot \
  --include-full-log -- \
  python3 code/run_susan_comparison.py \
    --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv \
    --jobs 2 \
    --log-dir logs/susan-vs-afni-6mm-pilot \
    --work-root work/susan-vs-afni-6mm-pilot \
  --check \
  python3 code/audit_susan_comparison.py \
    --manifest logs/runlists/susan-vs-afni-6mm-pilot.tsv \
    --output logs/records/susan-vs-afni-6mm-pilot.tsv \
    --missing-output logs/records/susan-vs-afni-6mm-pilot-missing.tsv \
    --fail-on-incomplete \
  > logs/phase0-susan-vs-afni-6mm-pilot.nohup 2>&1 </dev/null &
```

After the production AFNI target-smoothing launcher has stopped and its outputs have been reviewed, rebuild with `--scope all`. The expected contract is 765 ready and zero incomplete units. Use a separate log directory and request a compact dataset-level summary in addition to the 2,295 method-level rows:

```bash
python3 code/build_susan_comparison_manifest.py \
  --target-manifest logs/runlists/target-smoothing-6mm-ready.tsv \
  --scope all \
  --kernel-fwhm 6 \
  --output logs/runlists/susan-vs-afni-6mm-full.tsv \
  --missing-output logs/runlists/susan-vs-afni-6mm-full-missing.tsv

nohup bash code/run_logged.sh \
  --label phase0-susan-vs-afni-6mm-full \
  --include-full-log -- \
  python3 code/run_susan_comparison.py \
    --manifest logs/runlists/susan-vs-afni-6mm-full.tsv \
    --jobs 8 \
    --log-dir logs/susan-vs-afni-6mm-full \
    --work-root work/susan-vs-afni-6mm-full \
  --check \
  python3 code/audit_susan_comparison.py \
    --manifest logs/runlists/susan-vs-afni-6mm-full.tsv \
    --output logs/records/susan-vs-afni-6mm-full.tsv \
    --summary-output logs/records/susan-vs-afni-6mm-full-summary.tsv \
    --missing-output logs/records/susan-vs-afni-6mm-full-missing.tsv \
    --fail-on-incomplete \
  > logs/phase0-susan-vs-afni-6mm-full.nohup 2>&1 </dev/null &
```

## Post-smoothing tSNR, motion, and coverage QC

The production tSNR definition is voxelwise temporal mean divided by sample temporal standard deviation (`ddof=1`). It is measured from the approved `desc-smoothToFWHM6_bold` file that will enter FEAT. Summary statistics use the intersection of each run's fMRIPrep brain mask and one fixed TemplateFlow MNI152NLin6Asym brain mask resampled by nearest neighbor to the exact RF1 grid. `coverage_pct` is the intersection voxel count divided by the fixed common-mask voxel count; it is not calculated against each run's own denominator. Motion is read from the named fMRIPrep `desc-confounds_timeseries.tsv`, not from RF1's intentionally headerless Tedana-plus-confounds FEAT matrix. The latter remains the nuisance input to L1 and is not duplicated here.

Create the non-participant common mask once. Review the `find` result before running the command; it must identify the TemplateFlow `MNI152NLin6Asym` brain mask rather than a different template:

```bash
template_mask=$(find "$TEMPLATEFLOW_HOME/tpl-MNI152NLin6Asym" -type f \
  -name 'tpl-MNI152NLin6Asym_res-02_desc-brain_mask.nii.gz' \
  | sort | head -n 1)

printf 'Template mask: %s\n' "$template_mask"
test -n "$template_mask" && test -f "$template_mask"

python3 code/create_common_analysis_mask.py \
  --source-mask "$template_mask" \
  --reference-grid "$REFERENCE_GRID" \
  --output "$COMMON_ANALYSIS_MASK" \
  --json-output resources/tpl-MNI152NLin6Asym_space-RF1Grid_desc-brain_mask.json
```

Build the 765-run QC contract, then launch it through `nohup`. The batch reads each smoothed 4D input once, delegates tSNR to the authoritative RF1 implementation, requires one confound row per BOLD volume, and calculates FD>0.5-mm volume fractions. It writes small restartable per-run JSON files under ignored `derivatives/qc/`.

```bash
python3 code/build_analysis_qc_manifest.py \
  --output logs/runlists/analysis-qc-ready.tsv \
  --missing-output logs/runlists/analysis-qc-missing.tsv

nohup bash code/run_logged.sh \
  --label phase0-analysis-input-qc-full \
  --include-full-log -- \
  python3 code/run_analysis_qc_batch.py \
    --manifest logs/runlists/analysis-qc-ready.tsv \
    --jobs 8 \
    --log-dir logs/analysis-qc-current \
  --check \
  python3 code/audit_analysis_qc.py \
    --manifest logs/runlists/analysis-qc-ready.tsv \
    --output logs/records/analysis-qc-run-level.tsv \
    --summary-output logs/records/analysis-qc-dataset-summary.tsv \
    --subject-output logs/records/analysis-qc-subject-level.tsv \
    --missing-output logs/records/analysis-qc-missing.tsv \
    --fail-on-incomplete \
  > logs/phase0-analysis-input-qc-full.nohup 2>&1 </dev/null &
```

The default audit reports the preregistration-consistent, dataset-specific 1.5×IQR review flags: low tSNR, high mean FD, and low fixed-mask coverage. FD>0.5-mm counts and fractions remain descriptive columns. Optional fixed coverage/high-motion warning cutoffs may be requested on the command line, but they are not enabled by default and must not be confused with the registered exclusion rules. Thresholds and all raw metrics are retained so exclusions can be reviewed scientifically. Missed-trial exclusions are handled separately from imaging quality: a run is excluded only when more than 25% of its trials are missed. After a complete audit, create the simple QC plots:

```bash
python3 code/plot_analysis_qc.py \
  --input logs/records/analysis-qc-run-level.tsv \
  --output-dir qc
```

The tracked `qc/` outputs and compact `logs/records/` tables should be committed after review. Large per-run JSON derivatives stay ignored.

## Full-trial event and missed-trial QC

Event QC is a separate gate from imaging QC. It reads source BIDS events from each owning dataset, writes model-specific full-trial derivatives only under this repository's ignored `derivatives/harmonized/events`, and never edits source BIDS. RF1 full trials span the validated decision onset through matching outcome offset; ds003745 retains the published trial-level onset and duration. A miss is represented as one full-trial nuisance event.

The registered task-compliance rule is strict: exclude a run only when **more than** 25% of its trials are missed. Exactly 25% remains usable. A participant is excluded on this basis only if every available run is excluded. Zero-count substantive conditions are reported explicitly for design review; they are not silently converted into a different scientific exclusion rule.

```bash
python3 code/build_event_qc_manifest.py \
  --output logs/runlists/fulltrial-event-qc-ready.tsv \
  --missing-output logs/runlists/fulltrial-event-qc-missing.tsv

nohup bash code/run_logged.sh \
  --label phase0-fulltrial-event-qc \
  --include-full-log -- \
  python3 code/run_event_qc_batch.py \
    --manifest logs/runlists/fulltrial-event-qc-ready.tsv \
    --jobs 16 \
    --log-dir logs/fulltrial-event-qc-current \
  --check \
  python3 code/audit_event_qc.py \
    --manifest logs/runlists/fulltrial-event-qc-ready.tsv \
    --output logs/records/fulltrial-event-qc-run-level.tsv \
    --subject-output logs/records/fulltrial-event-qc-subject-level.tsv \
    --missing-output logs/records/fulltrial-event-qc-missing.tsv \
    --fail-on-incomplete \
  > logs/phase0-fulltrial-event-qc.nohup 2>&1 </dev/null &
```

The resulting run-level imaging and event tables remain separate evidence. A later explicit cohort-selection step must combine them before building L1 manifests; neither audit silently deletes data.
