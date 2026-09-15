# Neutral-condition decision and retained contrast numbering

Clarified 2026-09-15; supersedes the September 14 contrast-removal implementation.

Neutral is not a primary inferential target because there are too few trials.
This does **not** mean deleting its contrasts. Retain all 28 original pooled
activation contrasts, the same 28 PPI interaction contrasts and physiology at
COPE 29, identically for RF1 and ds003745. The tracked TSV is restored exactly
to its pre-removal version. COPE 10 is rew-pun; COPEs 27/28 are F-S/F-C (pun).

## Design and empty conditions

Observed neutral trials remain modeled. Absent neutral psychological EVs and
their PPI interaction EVs use FEAT shape 10, without fabricated events.
An otherwise valid run is not excluded for missing neutral. Empty reward or
punish conditions still require model review.

Retain the six neutral-weighted contrasts at their original positions:
7 C_neu, 8 F_neu, 9 S_neu, 20 F-S (rew-neu), 21 S-C (rew-neu),
22 F-C (rew-neu). These are not approved for inference in the current analysis.
All other task contrast vectors have zero neutral and missed-trial weights.

FSL may automatically zero a single-EV contrast on an empty EV in design.con.
Its slot and name remain. Mixed comparisons involving that absent EV may retain
their coefficients while being non-estimable. This is recorded explicitly, not
mistaken for valid neutral inference or fixed by renumbering the contrast set.

## Enforcement and validation

- The renderer retains all 28/29 contrast slots and FEAT's global
  `conmask1_1=0` switch. That switch was accidentally removed by the pooled
  renderer, although present in both source templates.
- `audit_l1_contrasts.py` verifies intended FSF names/weights, actual design.con
  weights (allowing FSL's documented-in-our-tests empty-EV zeroing), and
  estimability of primary contrasts. It reports unsupported neutral hypotheses.
- L1 saves `design-contrast-audit.json` before cleanup; the completeness audit
  repeats the checks. The report does not authorize neutral group inference.
- `verify_neutral_feat_design.py` tests activation/PPI with neutral present,
  friend-neutral absent and all neutral absent, crossed with missed EV
  present/absent (12 real feat_model cases).
- Real FEAT poststats and L2 passed for both sub-144 runs and both model types
  on Linux2 in the [September 15 restored-contract pilot](../logs/records/20260915-091946_sub144-restored-contrasts-L1-L2.md).
  This goes beyond feat_model validation but does not certify whole-cohort output;
  see [current status](CURRENT_STATUS.md).

## Scope and migration

The September 15 inventory found only four L1 FSFs in the two scanned FSL
derivative trees: sub-144 runs 1/2, activation/PPI, using the reduced 22/23
contract. It found no additional L1 FSFs in those trees, including the scanned
replacement paths. This is not a claim about historical outputs elsewhere.

The completed scoped recovery archived those incompatible sub-144 outputs
recoverably and reran with the corrected events and restored contrast set. No upstream
BIDS, fMRIPrep, resampling or target smoothing is changed. Model provenance is
versioned `fulltrial-retained-contrasts-v3`; do not retrofit new stamps onto
old output.

If neutral inference is requested later, choose a support-qualified cohort and
validate those effects at each level explicitly. The primary contrast numbering
does not change.
