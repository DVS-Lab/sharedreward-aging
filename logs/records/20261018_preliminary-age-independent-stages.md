# Preliminary age analysis independent launch preparation

- Date: 2026-10-18
- Repository base: `775c4e3`
- Execution: local Mac development and synthetic tests, not Linux2 production analyses.
- Authorization: user requested separate VS ROI and whole-brain activation/PPI launches
  while the upstream mask investigation continues, with the reviewed narrow allowance.

## Changes

- Added independent `roi` and `wholebrain` stages; `all` remains supported.
- ROI-only avoids merged 4D image stacks and randomise, retaining the same pooled
  HC3 tests, covariates, common ROI coverage and 15-test Holm family.
- Whole-brain-only retains the ten activation/PPI models, 20 signed maps and
  existing permutation/correction settings. No subject exclusions changed.
- Added opt-in exact old/current mask fingerprint transitions for ten upstream
  masks from `20261018-202606_age-mask-fingerprint-diagnostic.md`.
- Default audit remains strict. Exceptions are reported as provisional; no BOLD,
  model input, parent, contrast, actual map or geometry validation is bypassed.
- Original FEAT outputs and provenance stamps are untouched.
- Added pandas and scipy to the environment specification.

## Evidence and limits

The source inventory `20261018-203436_age-mask-source-investigation.md` found
current copies and listed fMRIPrep logs for all five subjects during the same
night. It did not compare mask voxel contents. Successful earlier PPI fits do
not resolve later upstream file changes. These preliminary analyses concern
the existing FEAT outputs, not certification of new upstream preprocessing.

## Validation

- Bash and Python syntax: passed.
- Full workflow suite: 103 tests passed.
- Independent-stage orchestration test uses real synthetic extraction, statistics
  and plotting with external audit/permutations stubbed; production images are
  available only on Linux2.
- Tests verify exact nanosecond preservation, explicit opt-in, rejection of
  subsequent drift and changed model inputs, unchanged stamps, identical ROI
  results without image-stack creation, and stage-specific completion counts.
- Production age effects have not been run or claimed complete by this record.
