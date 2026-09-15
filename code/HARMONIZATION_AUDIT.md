# Harmonization audit

Historical audit date: 2026-08-22. Reconciled 2026-09-15; see
[current status](../docs/CURRENT_STATUS.md) for execution and outstanding review.

## Event implementations

The data descriptor identifies Shared Reward as a block design: two runs, nine blocks per run, and eight trials per block. The public ds003745 events contain both `block_<partner>_<predominant-feedback>` rows and trial-level `event_<partner>_<feedback>` rows. Across the 100 tracked public run files inspected, event durations ranged from about 3.503 to 4.537 seconds (mean about 3.536 seconds). Run-level responded event counts vary because missed trials are represented separately.

The old `convertSharedReward_BIDS.m` explicitly used `decision_onset` plus `trialDuration`. That is evidence of the intended historical full-trial representation, not proof that exact outcome-phase timing can be reconstructed. Its questioned outcome-onset alternative and `computer_non-faceclea` typo are historical warnings, not instructions for a new source-data rewrite.

The approved pooled model is an estimand-level full-trial model:

- ds003745 uses its published full-trial representation, with the separately
  documented source correction for sub-144;
- RF1 derives partner × feedback full-trial rows from validated canonical decision/outcome phase pairs;
- misses become one full-trial nuisance epoch only when both boundaries are present;
- harmonization itself does not rewrite source BIDS; approved upstream source
  corrections remain separately documented.

Exact phase-resolved ds003745 events are neither required nor generated. The
August search did not locate raw logs, but this is no longer a current absence
claim: `srndna-datapaper` now tracks raw acquisition logs and guarded sub-144
full-trial recovery. That recovery does not change the agreed pooled temporal
model or justify manufacturing phase-resolved events for the older cohort.

## Historical template drift

The old aging activation template has 13 EVs, 32 contrasts, 5-mm FEAT smoothing, and one unconvolved generic miss EV. Several named neutral/decision contrast vectors are malformed. The RF1 and `r01-soi` templates have 34 contrasts and nominal 6-mm smoothing. The pooled scientific definition must come from the authoritative crosswalk/model specification, not from the old aging FSF.

FLOBS variants are historical/sensitivity material. Old qsub, WarpKit, TEDANA, and fMRIPrep scripts document earlier processing but are not production inputs.

## Acquisition differences retained in metadata

RF1 is multi-echo and uses TEDANA-enhanced confounds. ds003745 is single-echo and uses the corresponding fMRIPrep nuisance information. The current ds003745 wrapper pins the same fMRIPrep container version as Linux2 (25.2.5) and requires only `MNI152NLin6Asym`, but it does not pretend to reproduce RF1's multi-echo steps.

## Spatial/smoothness plan

RF1 defines the common verified grid. ds003745 continuous BOLD is resampled by applying an identity transform with AFNI `wsinc5` interpolation, and masks use nearest-neighbor interpolation, into a separate derivative. Grid equality is tested from dimensions, voxel sizes, orientation, and affine. Matched preprocessing uses classic combined FWHM as the `3dBlurToFWHM` stopping criterion; ACF is retained as a diagnostic and for later residual-based inferential characterization. Phase 0 approved a 6-mm total classic-FWHM target on 2026-08-23 after all 865 characterization units passed. The target is supported by the measured distributions, voxel dimensions, and expected cross-age anatomical heterogeneity rather than inherited from historical FEAT settings.

## Decisions deferred

- whether a block-level analysis should be a ds003745 sensitivity analysis only;
- final pooled covariates, including tSNR;
- pooled L3 design and subject exclusions;
- final seed provenance and PPI hypotheses; the common PPI implementation has
  passed the sub-144 Linux2 pilot but is not yet a completed whole-cohort analysis.
