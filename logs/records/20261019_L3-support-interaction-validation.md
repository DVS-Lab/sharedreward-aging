# L3 variance support and interaction validation

Date: 2026-10-19 (America/New_York). Development validation on the local Mac;
this is not a Linux2 production completion record. Starting revision: 8e87080.

## Requested changes

- Keep FLAME1 with `robust_yn=0` and the existing retained-run exclusions.
- Validate DOF on directory-mask intersection AND positive VARCOPE in every
  subject, matching the variance gate in FSL `fsl-flameo/design.cc`.
- Use that same explicit support for shared group ROIs and FEAT adapter masks,
  including poststats. Record full/directory/effective ROI coverage and the
  number of voxels removed for nonpositive input variance. Do not modify any
  original masks or statistical images, fill fixed-effects DOF, or drop people.
- Keep additive age and ratings models; add age × raw friend-win minus
  stranger-win rating models for activation and VS-PPI COPE17. Both main effects,
  tSNR, FD and dataset remain included. The interaction multiplies centered age
  in decades by centered raw rating difference, without orthogonalization.
- `--with-interactions` enables 16 whole-brain models and 24 ROI tests.
  Interaction zstat1/2 are positive/negative interaction, zstat3/4 ratings at
  mean age, and zstat5/6 age at mean ratings. Templates are tracked in `templates/`.

## Executed validation

Environment: local FSL 6.0.7.19, `/Users/tug87422/fsl/bin/python3`.

```bash
export FSLDIR=/Users/tug87422/fsl
source "$FSLDIR/etc/fslconf/fsl.sh"
export PATH="$FSLDIR/share/fsl/bin:$FSLDIR/bin:$PATH"
export MPLCONFIGDIR=/private/tmp/sharedreward-mpl-test
export RUN_FSL_SMOKE=1
bash code/validate_workflow.sh
```

Result: bash/Python syntax passed; **113 tests passed, no skips**, 49.360 s
for the unittest suite. Full local output:
`/tmp/sharedreward-L3-support-interaction-final-validation.log`.
`git diff --check` also passed.

The tests include:

- Actual `feat_model` matrix/contrast generation for all three families;
  exact main-effect/interaction columns and signed contrasts; robust=0.
- Independent OLS and full HC3 sandwich calculation agreeing with the ROI
  interaction coefficient and standard error.
- A 24-subject native FEAT/FLAME1 interaction fit, including poststats for all
  six contrasts. Every directory mask contains an intentionally unsupported
  slab with zero input variance/DOF. The effective mask excludes only that
  slab; fitted mask, matrices, positive output variance, zstats and cluster
  outputs pass. SHA-256 checks confirm all original images remain unchanged.
- ROI CLI orchestration with synthetic data and mocked upstream cohort/readiness:
  16 model-support reports, 24 results (18 age, 3 additive ratings, 3 interaction),
  three figures and successful completion records. Each synthetic ROI retains
  48/64 supported voxels, excluding the zero-filled slab from its mean.
- Nonfinite variance, absent fixed-effects DOF and nonpositive DOF on valid
  positive-variance support still fail. Frozen QC outliers cannot enter retained
  manifests. Within-partner ratings reversal exclusion and equality policy remain.

## Production status

Not launched from this Mac. Run the documented `--stage all --with-interactions`
command on Linux2 with a new label. ROI results are saved after input validation
and before FEAT staging; four whole-brain workers run concurrently thereafter.
No L1/L2 rerun or deletion is required. The scoped upstream-mask provenance
allowance remains provisional and is separate from this variance-support fix.
