# Retained contrast restoration and FEAT control fix

Implementation on the local Mac, 2026-09-15. Starting main: `4210fd1`.
No Linux2 models or upstream imaging products were modified by this change.

## Evidence and scope

The user's inventory record `20260915-085622_sharedreward-L1-fsf-inventory.md`
found four L1 FSFs in the scanned derivative trees: ds003745 sub-144 runs 1/2,
activation/PPI. All four used the reduced 22/23 contrast contract and lacked
`conmask1_1`; no L1 FSFs were found under rf1-sra-sharedreward/derivatives/fsl.
The scan does not establish what historical models exist outside those roots.

The internal stage log `sub144-FEAT-stage-details.txt` reports the missing Tcl
setting after FILM saved results. Both historical source templates contain it;
the pooled renderer introduced at `1cac9f9` stripped it and generated only
off-diagonal masking settings. This is separate from the scientific decision
about neutral inference, and does not imply a problem with upstream fMRIPrep.

## Change

- Restored FULLTRIAL_CONTRAST_CANDIDATE.tsv byte-for-byte to `6acafcf`:
  28 activation contrasts and the same 28 PPI interactions plus physiology
  at COPE 29. Original neutral contrasts and numbering are retained for all
  subjects and both datasets; neutral remains non-primary/non-inferential.
- Restored the global FEAT contrast-masking setting `conmask1_1=0` in generated
  activation/PPI FSFs. Historical source FSFs were not edited.
- Updated L2 input counts, completion checks, scoped recovery and provenance
  consistently. New contract ID: `fulltrial-retained-contrasts-v3`.
- Added a per-model contrast audit checking intended names/weights, actual
  design.con weights and primary estimability. FSL's automatic single-EV
  zeroing for an empty neutral condition is allowed and explicitly reported;
  non-estimable neutral hypotheses remain tagged, not silently interpreted.
- Added missing L2 varcope existence checking to the completeness audit.
- Updated the decision and recovery documentation; older records are preserved
  as history rather than rewritten.

## Validation

`20260915-090716_retained-contrasts-local-validation.md` records testing on the
working tree based on starting commit 4210fd1, before the implementation commit.

- All 61 unit/regression tests passed, including missing conmask1_1 rejection,
  changed matrix rejection, primary non-estimability rejection, empty-neutral
  reporting, bounded activation/PPI concurrency, and fixed-effects L2 counts.
- All 12 real installed FSL feat_model cases passed, crossing act/PPI with
  neutral present/friend-neutral absent/all-neutral absent and missed EV
  present/absent. These cases also exercised the new production contrast audit.
- Numerical report: `20260915-retained-contrast-feat-design.json`.
- `git diff 6acafcf -- templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv` is empty.
- `git diff --check` passed.

This is not a completed full FEAT/poststats/L2 pilot. The next Linux2 action is
the existing scoped recovery command with --run-models, activation/PPI paired.
It recoverably archives the four incompatible sub-144 FEAT directories under
derivatives/fsl/replaced-models before rerunning, then performs L1 and subject-
level audits. No BIDS/fMRIPrep/resampling/smoothing recomputation is requested.

Full-cohort launch remains gated on that pilot, ratings/cohort refresh and
final imaging-QC dispositions. In particular, the sub-10803 ratings audit is
still stale; no new ratings audit is claimed by this implementation.
