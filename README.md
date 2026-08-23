# Shared Reward aging harmonization

This repository owns the project-specific harmonization of RF1 Shared Reward with OpenNeuro `ds003745` version 2.1.1. It does not replace either source dataset and does not copy RF1 FEAT trees.

```text
ds003745 v2.1.1 raw BIDS        RF1 canonical Linux2 BIDS/derivatives
          |                                  |
          v                                  v
 fMRIPrep 25.2.5                  rf1-sra-sharedreward
          |                                  |
          v                                  |
 RF1-grid resampling                         |
          |                                  |
          +--------> model-specific common full-trial EVs
                             |
                             v
                   matched AFNI smoothing
                             |
                             v
                   dataset-specific L1/L2
                             |
                             v
                    harmonization QC
```

## Timing boundary

The experiments are not temporally identical. ds003745 was organized as 2 runs × 9 partner/valence blocks × 8 trials. Its published `event_<partner>_<feedback>` rows describe recoverable full-trial epochs (usually about 3.5 seconds), accompanied by block rows. Although decision and outcome displays were conceptually distinct, their exact phase boundaries are not assumed recoverable from the published files.

RF1 retains its richer canonical decision/outcome events. Cross-dataset harmonization happens only in this repository as a model-specific derivative:

- ds003745: retain published `event_<partner>_<feedback>` onset/duration;
- RF1: derive a full-trial epoch from validated decision onset through the matching outcome offset;
- never rewrite either source BIDS dataset;
- never manufacture phase-resolved ds003745 timing.

A block-level ds003745 model is scientifically legitimate as a sensitivity analysis, but is not automatically a pooled model because RF1 did not use the same historical block design.

## Phase 0 hard stop

Current work is limited to audit, reproducible acquisition, a small modern fMRIPrep pilot, event/grid/smoothness/tSNR characterization, and candidate target evaluation. No target FWHM is selected and no full-cohort smoothing, L1/L2, or pooled L3 should run before review.

The ds003745 cohort is resampled with a frozen run-level manifest, cubic interpolation for continuous BOLD, nearest-neighbor interpolation for masks, per-run grid checks, and an independent cohort audit. Generated imaging remains under ignored `derivatives/harmonized`; only compact run records and QC tables belong in Git.

Baseline smoothness is measured from the exact RF1 analysis inputs and from paired ds003745 inputs before and after RF1-grid resampling. RF1 confounds are referenced from the authoritative `rf1-sra-linux2/derivatives/fsl/confounds_tedana` outputs rather than duplicated here. Both classic Gaussian FWHM and ACF parameters are retained. MRIQC may be added as complementary acquisition QC, but it does not replace analysis-input smoothness, tSNR, motion, or coverage characterization.

See [code/HARMONIZATION_AUDIT.md](code/HARMONIZATION_AUDIT.md) and [code/README.md](code/README.md). Run static/synthetic checks with `make test`.
