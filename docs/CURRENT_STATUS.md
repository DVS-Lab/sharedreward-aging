# Shared Reward: current state and handoff gate

Updated 2026-10-02. **Pooled activation and provisional VS-PPI processing is
complete and computationally verified. Ready for Cooper's QC and L3 design,
not automatic final cohort approval.** The [Cooper handoff](COOPER_HANDOFF.md)
is the working checklist.

## Completed Linux2 execution

The [full-run record](../logs/records/20260930-163946_sharedreward-full-20260930-163946.md)
exited 0. Frozen manifests and audits are in
`logs/records/full-analysis-20260930-203949-441196/`. The
[final summary](../logs/records/full-analysis-20260930-203949-441196/final/summary.json)
has `computational_gate_passed=true`, with no unverified expected models:

| Layer | ds003745 | RF1 | Total |
|---|---:|---:|---:|
| Task-valid runs | 89 | 655 | 744 |
| Task-valid subject-sessions | 47 | 346 | 393 |
| Two-run subject-sessions | 42 | 309 | 351 |
| One-run subject-sessions | 5 | 37 | 42 |
| Verified L1 models (activation + VS PPI) | 178 | 1,310 | 1,488 |
| Verified subject outputs (activation + VS PPI) | 94 | 692 | 786 |

Two-run subjects use fixed effects; one-run subjects use L1 passthrough.
786 therefore counts subject/model-type outputs, not independent people or
two-run L2 models. The
[verified pre-QC candidates](../logs/records/full-analysis-20260930-203949-441196/final/verified-pre-QC-candidates.tsv)
supply actual model paths but are not a final approved L3 sample.

Preparation in that run verified 768 smoothed/input-QC units, 766 event-QC
units, and all 100 ds003745 FSL nuisance matrices. It generated 744 retained
EV sets, refreshed ratings provenance, and applied reviewed source decisions.
The updated arithmetic is **768 - 2 source gaps - 19 excessive-miss runs - 3
curated invalid runs = 744**. Source gaps are RF1 11450 r2 and 12037 r2;
curated invalid runs are 11539 r1/r2 and 10657 r1. There are zero reward/punish
model-review holds. Motion/tSNR/coverage flags still require Cooper's review.

Do not repeat the full launcher merely to begin QC/L3: it can regenerate
inputs and retire superseded models. Use scoped, logged reruns only when a
new decision changes contributing runs or model inputs.

## Current behavioral policy and cohort

The user's 2026-10-01 primary rule, pending Cooper, excludes the participant
if **Loss > Win for any partner**; equality is allowed. Missing/invalid ratings
and all-six-identical responses remain ineligible. Use raw ratings, not
within-person z-scores.

The behavioral cohort has **318 participants (285 RF1 + 33 ds003745)**, all
with canonical age and recorded sex, before imaging-QC exclusions. This removes
29 additional participants from the former aggregate-rule cohort of 347.
See [methods, results, and archives](RAW_RATINGS_ANALYSIS.md).

Use [behavioral-eligibility.tsv](../qc/ratings-raw/behavioral-eligibility.tsv),
joining dataset + subject and keeping `primary_included=true`. September
frozen manifests, final candidates, the source audit, and dispositions still
retain historical aggregate-rule ratings flags. They must not override the
new behavioral membership table. Future cohort construction re-evaluates the
within-partner rule from validated means; existing frozen execution evidence
was deliberately not rewritten. This update does not invalidate imaging models
or automatically restrict every L3 hypothesis.

## Source resolutions already propagated

- **10657:** exclude Shared Reward r1, retain r2. The PI accepted Ryan's session
  form: deviation for r1, no task deviations for r2. This is not a direct saved
  record of the corrected name and does not imply a Trust exclusion.
- **10668:** the PI-approved reconstruction and first-255-volume trim were
  repaired upstream and validated through confounds on September 30. The full
  downstream run re-smoothed/rebuilt both corrected runs and their models.
  This is a reviewed reconstruction, not timestamp-proven stimulus identity.
- **11913/11923:** source-series review found no cross-folder Shared Reward
  assignment or conflicting metadata. No reassignment/exclusion is indicated.
  The exact referent of the historical registration note remains unproven;
  this is not an outstanding broad lab-review request.
- **ds003745 sub-144:** corrected events and the restored full contrast model
  are included. [Recovery provenance](SUB144_EVENT_RECOVERY.md) distinguishes
  this correction from an unpatched OpenNeuro 2.1.1 download.
- **RF1 10803:** recovered ratings are incorporated in the refreshed source
  audit. The older 346-person aggregate-rule cohort was superseded by 347,
  then by the current 318-person within-partner-rule cohort.

Evidence: [upstream source-validity record](https://github.com/DVS-Lab/rf1-sra-linux2/blob/main/docs/sharedreward-source-validity.md),
[upstream 10668 validation](https://github.com/DVS-Lab/rf1-sra-linux2/blob/main/logs/records/20260930-153531_10668-final-validation-20260930-153531.md),
[curated exclusions](curated_run_exclusions.tsv), and completed-run frozen
manifests. The upstream note's downstream-refresh request is fulfilled by
that run. These cases do not need repeated source-review requests.

## Settled model and preprocessing contract

`fulltrial-retained-contrasts-v3`: nine partner-by-feedback psychological EVs,
optional convolved missed-trial nuisance EV, 28 activation contrasts; PPI has
21 EVs, the same 28 interaction contrasts, and physiology COPE29. Preserve
all slots. Current inference uses **1–6, 10–19, 23–28** only. Ignore neutral-
containing COPEs **7–9, 20–22** and physiology COPE29 for the task gate.
Selection is based on coefficients, not labels. Missing neutral cells alone
do not exclude a run. See [neutral policy](NEUTRAL_CONDITION_DECISION.md) and
[contrast coefficients](../templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv).

ds003745 BOLD uses `wsinc5` resampling to the RF1 grid; masks use nearest
neighbor. AFNI targets **6-mm total classic FWHM**, not a 6-mm additive kernel.
FEAT smoothing is 0 and all per-EV temporal filters are 0. ACF is a different
diagnostic, not a replacement label for the classic target. Two-run models use
fixed effects (`mixed_yn=3`, `FSLSUB_PARALLEL=1`). No smoothing or timing
redesign is required for this handoff.

| Repository | Responsibility |
|---|---|
| `rf1-sra-linux2` | Canonical RF1 BIDS/events, fMRIPrep, TEDANA/confounds and upstream QC |
| `rf1-sra-sharedreward` | RF1-only phase-resolved models; shared RF1 smoothing/grid resources |
| `sharedreward-aging` | ds003745 preprocessing/harmonization and pooled full-trial models for both datasets |
| `srndna-datapaper` | Older-dataset source repair and release provenance |

Pooled models live under Linux2
`/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/{dataset}/sub-{subject}`.
Do not substitute RF1-only 14-EV/34-contrast outputs. RF1's canonical phase
timing stays intact upstream; pooled RF1 epochs span decision onset through
outcome offset. ds003745 uses its recoverable published full trial.

## Remaining work: final analysis specification

Cooper reviews imaging-QC flags and records exclusions, defines hypothesis-
specific cohorts/covariates, and builds L3 designs with approved contrasts,
mask, inference, and multiplicity control. Final VS seed provenance/hypothesis
approval remains open. If a contributing run is removed, rebuild the affected
subject output or use one-run passthrough, then validate ordered COPE/VARCOPE
inputs against the new retained-run cohort.

Coverage uses the fixed TemplateFlow mask minus the historical inferior
cerebellum/posterior-brainstem exemption. Whole-brain tSNR uses the full reference
mask and final smoothed input. Neither is automatically the L3 mask. See
[exclusion policy](EXCLUSION_POLICY.md). Existing workers clean residuals:
check availability before choosing an inference method requiring them.

The final audit documents its limits: computational validity is not scientific
cohort approval; image provenance uses size/mtime rather than full 4D hashes,
and EV comparison is against harmonized events rather than raw sources.
This documentation update inspects tracked Linux2 evidence, not a new live
audit of the remote filesystem.

Historical pilot-only results, inventories, and launch instructions remain in
[Git history](https://github.com/DVS-Lab/sharedreward-aging/blob/6e6fe40/docs/CURRENT_STATUS.md)
and dated run records. They are superseded as current status, not erased from
the provenance trail.
