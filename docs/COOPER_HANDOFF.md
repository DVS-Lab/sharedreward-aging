# Cooper handoff: Shared Reward aging

Prepared 2026-09-15. **Ready for exclusion review and L3 preparation; not yet
cleared for full-cohort L3 execution.** The [current status](CURRENT_STATUS.md)
is the evidence index and numerical snapshot. Do not interpret this document
as a final cohort approval or an instruction to rerun preprocessing.

## Message to Cooper

Please take ownership of the Shared Reward aging exclusion review and pooled
L3 design specification. All current processing was done on Linux2. The
authoritative pooled analysis is `/ZPOOL/data/projects/sharedreward-aging`:
RF1 and ds003745 must both use its common full-trial L1/L2 contract. The separate
RF1-only repository's 14-EV/34-contrast phase-resolved COPEs are not interchangeable
group inputs.

The model and smoothing decisions are settled: 6-mm total classic-FWHM AFNI
inputs, no additional FEAT smoothing, 28 activation contrasts and 28 PPI
interaction contrasts plus physiology COPE29. Preserve numbering and use only
non-neutral task COPEs **1–6, 10–19, 23–28**. Do not exclude a run simply because
neutral trials are absent. VS PPI is provisional pending seed-provenance and
hypothesis approval.

The current technical/task inventory has **744 runs / 393 subject-sessions**,
before final imaging or hypothesis-specific exclusions. Strictly >25% misses
exclude a run; two known missing-event runs and RF1 11539's wrong-friend-photo
runs are already excluded. Valid opposite runs remain eligible. Imaging IQR
flags are review information, not automatic exclusions. Ratings are a separate
hypothesis-level gate: the tracked 655/346 ratings-qualified count needs a refresh
for recovered RF1 10803 and must not be treated as final.

The current v3 real-data pilot is complete for ds003745 sub-144 (both runs,
activation and VS PPI, plus both fixed-effects outputs). The full-cohort audit
verified those four L1s and two subject outputs; the other 1,484 expected L1s
are absent. Full pooled execution and verification remain outstanding. Do not
build a final L3 sample from the partial verified-candidate table.

Please resolve or escalate these questions with the PI/source-data team:

1. **10657 r1/r2:** what was the friend-identifier error, and what exact run or
   contrast scope is invalid? Its 5.280-mm smoothing exception is unrelated.
2. **10668 r1:** which evidence confirms Shared Reward is valid despite the
   historical broad exclusion and later narrower Trust-r2 disposition?
3. **11923 r1/r2 versus 11913:** do source DICOM identifiers and visit timelines
   establish correct participant identity for the Shared Reward images?

Record reviewer/date, evidence, include/exclude/review decision and exact
run/contrast scope; absence of a technical error is not source-validity proof.
Do not publish identifying DICOM/session details. Review the existing tSNR,
motion and coverage flags, and define the hypothesis-specific ratings and
covariate requirements without silently changing the preprocessing cohort.

## Working inputs

Paths below are relative to `sharedreward-aging` on Linux2; compact records are
tracked in Git, imaging and runlists are not.

- `logs/records/analysis-run-dispositions.tsv` and
  `analysis-subject-dispositions.tsv`: current task-valid versus excluded runs,
  one/two-run status, ratings eligibility, and imaging review flags. These do
  not yet encode the three upstream historical-review questions.
- `logs/records/analysis-qc-run-level.tsv`: final-input tSNR, FD, coverage and
  flags; `qc/` contains figures/mosaics. Use the correct coverage denominator,
  not an assumed whole-brain or future statistical mask.
- `logs/records/fulltrial-event-qc-run-level.tsv`: condition support and misses;
  `ratings-qc-subject-level.tsv`: source-provenanced ratings (refresh required).
- `templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv` and
  `docs/NEUTRAL_CONDITION_DECISION.md`: pooled contrast identities and coefficients.
- `logs/records/group-readiness-20260915-103331/`: current incomplete computational
  audit, including exact missing paths; not the eventual group input list.
- Upstream `rf1-sra-linux2/docs/historical-tracker-reconciliation.md`: scientific
  review evidence. `srndna-datapaper/code/README.md` and the sub-144 recovery
  record establish the older-dataset event repair.

## Owners and completion criteria

Cooper owns proposed exclusions and L3 specifications; the PI/source-data team
signs off scientific/identity decisions. Workflow execution remains a separate
logged step, not an assumption that Cooper must regenerate preprocessing.

Before L3 execution, require:

- an approved, versioned run/subject decision ledger and hypothesis-specific
  cohort, with unresolved decisions explicitly visible;
- refreshed ratings provenance; complete primary L1 and subject-level audit
  against that cohort, with no missing/unverified inputs silently omitted;
- two-run fixed effects using only the retained runs, or explicit L1 passthrough
  for one-run subjects; rebuild affected L2 if a formerly included run is removed;
- exact ordered COPE/VARCOPE paths, dataset + subject + session keys, contributing
  runs, model/seed/contrast identity and audit/code revisions;
- aligned participant/covariate rows, explicit missing-data handling, design
  rank/contrast estimability checks, approved statistical mask and inference/
  multiplicity plan. Residual smoothness should be addressed if needed by the
  chosen inference method; existing workers clean residual files, so their
  availability must not be assumed.

The earlier source gaps, wrong-friend-photo exclusion for 11539, sub-144 event
recovery, neutral policy, and spatial preprocessing do not need reopening.
