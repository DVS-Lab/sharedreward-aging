# L3 FEAT/FLAME1 implementation and exclusion verification

Local development validation, 2026-10-18. No production Linux2 L3 fit was
performed in this record, and no L1/L2 data or exclusion decisions were changed.

## User decisions implemented

- Ordinary FEAT/FLAME1 instead of randomise.
- Primary predictors: age, tSNR, mean FD, dataset dummy, plus intercept.
- Optional matched raw friend-win minus stranger-win ratings at COPE17.
- Separate tracked FSF templates under `templates/`; FEAT watcher disabled.
- Preserve Cooper's recorded exclusions and verify them explicitly at launch.

## Checks

- Real local FSL `feat_model` reproduced the intended design and contrast
  matrices for both template families.
- A 24-subject synthetic dataset completed ordinary FEAT/FLAME1, including
  poststats. Fitted design/contrasts, COPE/VARCOPE/zstat maps, cluster masks
  and standard-space cluster tables passed the new output audit.
- Full repository validation: 109 tests passed, with the opt-in real-FEAT
  smoke test skipped in that suite and run successfully separately.
- Current real covariate plan: 358 imaging participants, 290 ratings-qualified
  participants, 12 age and two ratings FEAT models.
- Retained-run manifest: 663 runs. No overlap with any of the 53 high-FD
  flags or 38 low-coverage flags. The registered low-tSNR thresholds flag
  zero runs. These categories overlap; totals are not additive.
- Added a regression test that rejects any retained run crossing a frozen
  FD, tSNR or coverage threshold. Thresholds are not recomputed on survivors.

See `docs/L3_FEAT_AGE_RATINGS.md` for inference scope, output paths, retained
run aggregation and the provisional upstream-mask provenance allowance.
Production execution still requires the Linux2 readiness audit and output audit.
