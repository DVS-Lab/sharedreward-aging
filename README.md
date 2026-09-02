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

## Phase 0 smoothing decision

Phase 0 approved a 6-mm total classic-FWHM target on 2026-08-23 after complete cross-dataset characterization. The original 765-run audit remains the smoothing-decision evidence; subsequent runs use the same fixed procedure and require the same achieved-smoothness QC. Pooled L3 remains out of scope at this stage.

The ds003745 cohort is resampled with a frozen run-level manifest, identity-grid AFNI `wsinc5` interpolation for continuous BOLD, nearest-neighbor interpolation for masks, per-run grid checks, and an independent cohort audit. The sharper `wsinc5` interpolant is used to minimize interpolation-induced smoothness while moving already-normalized MNI data onto the RF1 grid. Generated imaging remains under ignored `derivatives/harmonized`; only compact run records and QC tables belong in Git.

Baseline smoothness is measured from the exact RF1 analysis inputs and from paired ds003745 inputs before and after RF1-grid resampling. RF1 confounds are referenced from the authoritative `rf1-sra-linux2/derivatives/fsl/confounds_tedana` outputs rather than duplicated here. Both classic Gaussian FWHM and ACF parameters are retained. Matched preprocessing uses classic combined FWHM as the explicit `3dBlurToFWHM` stopping criterion; ACF remains a diagnostic here and should be estimated from first-level residuals when it is used for cluster-based inference. The 6-mm target is total achieved smoothness, not an added 6-mm kernel. MRIQC may be added as complementary acquisition QC, but it does not replace analysis-input smoothness, tSNR, motion, or coverage characterization. Coverage preserves the historical inferior cerebellum/posterior-brainstem exemption through a provenance-tracked TemplateFlow-minus-exemption mask; this mask is distinct from the full TemplateFlow tSNR reference.

The complete 765-run preprocessing control confirmed that FEAT-equivalent nominal 6-mm SUSAN would yield materially greater total smoothness (mean 8.260 mm in ds003745 and 7.919 mm in RF1) than the approved AFNI total target (5.775 and 5.852 mm). Production therefore retains the AFNI-smoothed files and keeps FEAT smoothing at zero. The reproducible numerical summary and mean ± SEM figure are under `qc/`.

The current authoritative inventory contains 667 RF1 session-01 Shared Reward runs plus 100 ds003745 runs. Only the two newly added RF1 `sub-12032` runs require incremental smoothing/QC catch-up. Five additional RF1 runs regained event timing through upstream source repair.

Production L1 uses RF1's authoritative headerless `TedanaPlusConfounds.tsv` matrices. Single-echo ds003745 receives a provenance-tracked headerless matrix with the same fMRIPrep base columns, cosine regressors, and non-steady-state regressors; rejected TEDANA ICA components are RF1-only by design. Activation and seed PPI run sequentially inside each bounded run-level worker. Two eligible runs are combined with fixed effects; a one-run subject uses the L1 cope directly rather than a fictitious fixed-effects model.

See [code/HARMONIZATION_AUDIT.md](code/HARMONIZATION_AUDIT.md), [docs/EXCLUSION_POLICY.md](docs/EXCLUSION_POLICY.md), and [code/README.md](code/README.md). Run static/synthetic checks with `make test`.
