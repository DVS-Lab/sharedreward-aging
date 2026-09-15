# Corrected sub-144 events and neutral-nuisance model contract

Date: 2026-09-14. Implementation/validation on the local Mac, not a Linux2 analysis run.
Starting sharedreward-aging commit: `6acafcf` (main), with the previously pending
neutral-decision edits completed in this change.

## Upstream evidence

Reviewed local `srndna-datapaper` at
`be25871ba5ac1983116183bf91aaff937f9f8f16`. The Shared Reward correction is
`db67173efd0d6d4ef31800d9ac24ca8d665a20bf`; its recovery check passed against the
second raw session. Both corrected sub-144 files matched the pinned SHA256
values documented in `docs/SUB144_EVENT_RECOVERY.md`.

Conversion with this repository's full-trial converter:

- Run 01: 72 trials, one missed (1/72), all reward/punishment cells present.
- Run 02: 72 trials, zero missed, all reward/punishment cells present;
  friend-neutral absent.

No source BIDS files, upstream code, fMRIPrep products, resampled images or
smoothed images were modified. OpenNeuro publication is not asserted by this
record. Until the release carries the exact verified correction, the event
manifest can read the authoritative upstream clone directly.

## Changes

- Finalize neutral-as-nuisance policy for both datasets and both analysis types:
  22 activation contrasts, the same 22 interaction contrasts plus physiology
  for PPI. Observed neutral remains modeled; absent neutral is an empty EV.
- Correct an extra underscore in rendered EV paths. This was caught by the
  real `feat_model` test, not the earlier mock render tests.
- Detect changed event sources and stale EV contents. New event QC carries
  source SHA256 provenance; old cached QC requires regeneration.
- Add model-input fingerprints and exact contrast-count checks. Reject old
  28/29-cope models and changed inputs rather than accepting cope22/23 alone.
- Add a scoped sub-144 recovery command with cohort refresh, recoverable model
  archiving, paired activation/PPI, fixed effects and four completeness audits.
- Keep L2 fixed effects and enforce `FSLSUB_PARALLEL=1`; make manifest-reader
  and activation failures propagate through paired launchers.

## Verification

- Bash/Python syntax and 52 repository tests passed (see the separately logged
  local-validation run record).
- Eight actual installed FSL `feat_model` cases passed: act/PPI crossed with
  neutral empty/present and missed empty/present. Matrices are finite, and all
  active contrasts are estimable. Numerical results:
  `logs/records/20260914-neutral-feat-design.json`.
- The empty neutral columns are genuinely zero, not synthetic events. A rank
  deficient full design due to unused zero nuisance columns does not imply
  non-estimability of the retained contrasts.
- `git diff --check` passed.

## Pending Linux2 work

Run the documented preparation and scoped recovery command. No Linux2 model
has been launched or declared complete from this local validation. Confirm
fresh cohort counts and sub-144's actual selected runs from generated records.
After this pilot passes, audit/migrate any cohort-wide old-contract outputs
before pooled group analyses; this recovery command does not rerun everyone.
