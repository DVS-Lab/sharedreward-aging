# Production smoothing decision

Decision date: 2026-08-23

The approved production target is **6 mm total measured classic FWHM**. AFNI `3dBlurToFWHM` will iteratively blur each run inside its corresponding fMRIPrep whole-brain mask until the classic combined FWHM reaches the target. FEAT smoothing remains zero. This is not an instruction to add a 6-mm Gaussian kernel.

## Evidence

The final Phase 0 audit contained 865 complete characterization units and no missing units. The 765 analysis-ready runs comprised 665 RF1 runs on the authoritative grid and 100 ds003745 runs resampled to that grid with identity-transform `wsinc5` interpolation.

| Dataset/stage | Runs | Mean classic FWHM | Median | Maximum |
|---|---:|---:|---:|---:|
| RF1 analysis input | 665 | 3.546 mm | 3.451 mm | 4.619 mm |
| ds003745 after RF1-grid `wsinc5` | 100 | 3.727 mm | 3.719 mm | 4.019 mm |

Every run is below the 6-mm target and can therefore be blurred upward. `wsinc5` added 0.259 mm classic FWHM on average to ds003745, substantially less than the 0.717-mm increase from the superseded cubic interpolation.

## Rationale

- Six millimeters is approximately twice the 2.7 × 2.7 × 2.97 mm analysis voxel dimensions.
- A common achieved target reduces study- and subject-level smoothness differences instead of matching only study means.
- The sample spans younger and older adults, with expected intersubject anatomical variability.
- Six millimeters is the approved upper bound; larger targets would unnecessarily reduce specificity in small regions such as ventral striatum.
- ACF parameters remain recorded as diagnostics. When ACF is used for cluster-based inference, it should be estimated from model residuals rather than substituted for the preprocessing target.

## Gate

Production smoothing may proceed. Every target-smoothed output must retain target-encoded naming and achieved classic/ACF QC. L1 may begin only after the smoothing completeness audit passes. Pooled L3 remains out of scope.
