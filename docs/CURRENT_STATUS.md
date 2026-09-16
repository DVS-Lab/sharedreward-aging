# Shared Reward: current state and handoff gate

Reconciled 2026-09-15 against `sharedreward-aging` main `a9b1919`,
`rf1-sra-sharedreward` main `a398cb7`, `rf1-sra-linux2` main `67ba6dcd`,
and `srndna-datapaper` main `be25871`. This is the current status index;
dated run records remain the evidence. The current processing discussed here
was performed on **Linux2**, not the historical HPC installation.

**Source-validity update, later 2026-09-15:** the PI agrees with excluding
10657 Shared Reward r1 and retaining r2 conditional on confirmation that the
friend name was corrected. Trust is unchanged. For 10668, establish raw BOLD
acquisition count/order and map the two recorded attempts; the current BIDS
inventory contains one Shared Reward run. Audit 11913/11923 using raw dates and
series identities (BIDS scans.tsv dates are shifted). See the upstream
[source-validity follow-up](https://github.com/DVS-Lab/rf1-sra-linux2/blob/main/docs/sharedreward-source-validity.md).
No generated dispositions/counts below have been changed by this update.
Imaging-QC exclusions remain Cooper's responsibility, not a prerequisite for
collecting these source-validity facts.

## Architecture: two intentional scientific models

| Owner | Responsibility | Model outputs |
|---|---|---|
| `rf1-sra-linux2` | Canonical RF1 BIDS/events, fMRIPrep, TEDANA/confounds and canonical QC | Acquisition/preprocessing truth, not pooled FEAT models |
| `rf1-sra-sharedreward` | RF1-only phase-resolved analysis; reusable RF1 grid, smoothing and QC resources | Activation: 14 EVs, 34 contrasts. RF1-only connectivity still requires revalidation |
| `sharedreward-aging` | RF1 + ds003745 full-trial harmonization, ds003745 preprocessing and pooled analysis/QC | Both datasets fitted here under the same full-trial model |
| `srndna-datapaper` | Older-dataset source recovery and release provenance | Approved sub-144 event correction, not pooled FEAT estimates |

RF1's canonical decision/outcome phases remain intact upstream. For pooling,
RF1 trial epochs span decision onset through matching outcome offset; ds003745
uses the recoverable published full-trial representation, not invented phase
boundaries. The downloaded 2.1.1 dataset requires the documented sub-144 source
correction; do not describe an unpatched 2.1.1 download as the corrected input.
The [guarded recovery record](SUB144_EVENT_RECOVERY.md) links that exception to
the source repository. This reconciliation does not assert that the next
OpenNeuro release is already published.

RF1 smoothed BOLD/resources may physically live in `rf1-sra-sharedreward`, but
its **14-EV FEAT COPEs must not be substituted for the RF1 half of the pooled
full-trial analysis**. Pooled models belong under
`/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/{dataset}/sub-{subject}`.

## Settled pooled contract

`fulltrial-retained-contrasts-v3`: nine partner × feedback psychological EVs
plus the optional convolved full-trial missed nuisance EV; 28 activation
contrasts; PPI has 21 EVs and the same 28 interaction contrasts plus physiology
at COPE29. Retain all slots. The temporary reduced 22/23 implementation is
superseded, not a second valid pooled model.

Current task inference uses **1–6, 10–19, 23–28**: 22 contrasts with zero neutral
weights. COPEs **7, 8, 9, 20, 21, 22** remain numbered but are ignored for current
inference; physiology COPE29 is also outside that task gate. This selection is
verified from actual coefficients, not labels. Observed neutral trials remain
modeled; absent neutral uses explicit empty EVs. Empty reward/punish conditions
remain model-validity concerns. See [the decision](NEUTRAL_CONDITION_DECISION.md).

No new smoothing decision is needed: AFNI target **6 mm total classic FWHM**,
ds003745 BOLD resampling with `wsinc5`, masks with nearest neighbor, FEAT
smoothing 0, all per-EV temporal filters 0. ACF remains a different diagnostic
measure, not a reason to relabel the classic target. Two retained runs use
fixed effects (`mixed_yn=3`, `FSLSUB_PARALLEL=1`); one retained run uses L1
passthrough. Activation and provisional VS PPI can run together with
`--parallel-types`: maximum FEAT concurrency is twice the paired-worker count.

## Inventory is not execution or final eligibility

The September 15 [cohort rebuild and sub-144 execution record](../logs/records/20260915-091946_sub144-restored-contrasts-L1-L2.md)
and [run dispositions](../logs/records/analysis-run-dispositions.tsv) establish:

| Layer | ds003745 | RF1 | Total |
|---|---:|---:|---:|
| Imaging-ready runs | 100 | 667 | 767 |
| Event-available runs | 100 | 665 | 765 |
| Task-ready runs, before final imaging/ratings adjudication | 89 | 655 | 744 |
| Task-ready subject-sessions | 47 | 346 | 393 |
| Two-run subject-sessions | 42 | 309 | 351 |
| One-run subject-sessions | 5 | 37 | 42 |

The run arithmetic is **767 − 2 source gaps − 19 excessive-miss runs − 2
wrong-stimulus runs = 744**. The source gaps are RF1 11450 r2 and 12037 r2;
the wrong-friend-photo runs are RF1 11539 r1/r2. Misses exclude only when
**strictly >25%**; exactly 25% does not. Valid opposite runs remain usable.
The event-only audit leaves four participants with no usable run; the separate
11539 stimulus exclusion makes five participants absent from the task-ready
subject inventory. There are zero reward/punish model-review holds. This does
not mean there are zero outstanding scientific-validity questions.

Current ratings-qualified counts are **655 runs / 346 subject-sessions**, and
are stale with respect to recovered RF1 10803. Its exact recovered six-cell
file passes the unchanged audit (`win_sum=7`, `loss_sum=-5`, nonidentical;
SHA-256 `461da4b6290c2a590023808d196c1354eeca89fb534a438b031b740651d1a112`).
The current disposition still says `missing_ratings_file`. Refresh discovery,
ratings QC and the cohort on Linux2; do not hand-edit the generated tables.
That recovery alone would add one retained run and one subject-session, but
**656/347 is a conditional expectation, not an executed final audit count**.
Missing ratings do not block fitting otherwise task-valid activation/PPI.

## What actually completed on Linux2

- The original 765-run smoothing/SUSAN comparison established the procedure;
  865 characterization units counted the older dataset both before and after
  resampling, **not 865 distinct analysis runs**.
- Both new 12032 runs report `DONE` in the
  [September 2 smoothing catch-up](../logs/records/20260902-001921_phase0-target-smoothing-6mm-catchup-20260902.md).
  That wrapper exited 1 only for the stable 10657 r1 tolerance exception and
  skipped its consolidated check. Do not relabel this record as exit 0 or
  schedule the two new runs again. Current code supports the
  [bounded exception](smoothing_qc_exceptions.tsv); a read-only 767-run smoothing
  audit should close the missing consolidated evidence, without reblurring.
- [Input QC passed 767/767](../logs/records/20260902-002601_phase0-analysis-input-qc-refresh-20260902.md):
  tSNR on final smoothed BOLD, named-confound FD and fixed eligible-mask coverage.
  There are 88 review-flagged runs across 61 participants (80 flagged runs are
  task-ready). They are not automatic exclusions. Coverage excludes the
  historical inferior cerebellum/posterior-brainstem exemption from its
  denominator; tSNR uses the full TemplateFlow reference. Neither is an
  automatically approved group statistical mask.
- September 15 preparation refreshed all 765 event units, audited all 100
  ds003745 FSL nuisance matrices and rebuilt the 744/393 task manifests.
- Corrected **sub-144 only** passed two activation L1s, two VS-PPI L1s and both
  fixed-effects subject outputs with the restored v3 contract. The later
  [primary group-readiness audit](../logs/records/group-readiness-20260915-103331/summary.json)
  independently verified all six. It expected 1,488 L1 models and found four
  verified / 1,484 absent; subject-level candidates were two verified / 784
  unverified. This is **outstanding current pooled-model execution**, not 1,484
  preprocessing failures or evidence of lost HPC output. No full-cohort current
  pooled-model completion record establishes otherwise.

The partial `verified-pre-QC-candidates.tsv` is not an approved L3 sample.
Final group modeling cannot start from a table containing only sub-144.

## Scientific review that technical completeness cannot settle

The upstream [September 11 tracker reconciliation](https://github.com/DVS-Lab/rf1-sra-linux2/blob/67ba6dcd/docs/historical-tracker-reconciliation.md)
identifies three Shared Reward issues. These **five runs remain present** in
the task-ready table; no new exclusions or manifest changes are made here.

| RF1 subject / retained runs | Specific question for PI/team | Record needed before final cohort freeze |
|---|---|---|
| 10657, ses-01 r1/r2 | Ryan identifies the incorrect Shared Reward collection as r1 only; historical code confirms the name is displayed. PI agrees with r1 exclusion/r2 retention conditional on the r2 name correction. | Confirm that r2 was corrected before final sign-off. Do not change Trust or infer a wrong photo. Generated policy is not changed yet. |
| 10668, ses-01 r1 | Two recorded attempts both use the run-1 design, but the current BIDS inventory contains one Shared Reward run. | Compare raw acquisition episodes, including adjacent Trust series, to establish count/order and attempt mapping. Do not equate echoes/phase/SBRefs with separate runs. |
| 11923, ses-01 r1/r2; cross-check 11913 | Do DICOM study/series IDs and acquisition timestamps map these Shared Reward series to the correct participant despite the reported 11913 scanner registration? | Verify both visit timelines; document any mapping or confirm no correction is needed. Keep identifying source details private. |

11539 is already excluded and is not a new decision. Imaging IQR review,
hypothesis-specific ratings/covariates, and final VS seed provenance also need
explicit decisions. Current VS PPI is computationally demonstrated but remains
provisional scientifically. Do not resurrect neutral inference, timing redesign,
or terminal-miss salvage as prerequisites for this agreed primary analysis.

## Code reconciliation and remaining work

The inspected current renderers/workers implement the settled pooled contract;
RF1-only 14/34 is intentional, not drift. No scientific code is changed here.
Two integration limits matter:

1. `build_analysis_cohort.py` reads curated exclusions but **does not ingest the
   new upstream historical-review queue**. Its `task_ready` and zero model holds
   cannot be used as scientific sign-off for the three cases above. Preserve a
   separate review ledger until scoped decisions can be recorded upstream and
   consumed downstream; do not invent exclusions.
2. Cohort construction reads the existing ratings audit; it does not automatically
   rediscover recovered sources. Thus regenerating a cohort alone leaves 10803
   stale. Ratings discovery and audit must precede the rebuild.

Before a final L3 handoff: close the consolidated smoothing audit record;
refresh ratings/cohort provenance; record the three source/stimulus decisions
and imaging review; generate/verify the full task-ready EV set; execute remaining
pooled L1 activation and provisional/approved PPI together with bounded
concurrency; audit and form L2 only from retained runs; repeat the non-neutral
readiness audit against the actual intended manifest. A changed run decision
must propagate to L2 (or one-run passthrough), not merely filter an old two-run
COPE at L3. Cooper can prepare exclusions/designs now, but final L3 execution
requires the complete verified, adjudicated, ordered input list.

Use [the Cooper handoff](COOPER_HANDOFF.md) for roles and acceptance criteria.

## Documentation corrections in this reconciliation

- Top-level flow: removed the implication that pooled RF1 modeling consumes
  the RF1-only FEAT model; clarified shared BOLD/resources versus different COPEs.
- Phase 0 status: replaced pending grid/target/12032 catch-up claims with dated
  completed evidence; retained the genuine skipped smoothing-audit closure.
- Inventory: replaced stale 765-run input-QC / 89-flag descriptions with the
  767-run / 88-flag record, without rewriting historical 765-run smoothing data.
- Event/confound preparation: marked the September 15 765-event and 100-matrix
  audits complete instead of asking to regenerate them as an unperformed stage.
- Raw-source availability: corrected the old absence claim after sub-144 raw
  logs and guarded recovery became available in `srndna-datapaper`.
- Pilot status: marked sub-144 real FEAT/L2 checks complete; distinguished that
  evidence from the still-incomplete full-cohort primary-output audit.
- Concurrency: documented the supported concurrent activation/PPI mode in both
  L1/L2 examples and halved paired-worker counts to preserve their former FEAT
  concurrency ceilings. No launcher defaults or workers were changed.
- RF1 historical comparison: dated the old RF1/r01-soi template identity claim;
  it is not a current assertion about the modernized RF1 14-EV model.
- Eligibility: exposed stale 10803 ratings and the three upstream scientific
  review questions instead of equating task readiness with cohort approval.

The [local reconciliation check](../logs/records/20260915-115207_sharedreward-state-reconciliation.md)
verified these counts, current renderer contracts, recovered ratings behavior
and documentation links. It is not a new Linux2 imaging/model audit. Only
documentation was changed in this pass; previous processing logs were retained.
