# Cooper handoff: Shared Reward aging

Updated 2026-10-05. **Ready for Cooper's exclusion review and pooled full-trial L3 design.**
Full pooled activation and provisional VS-PPI processing is complete and
computationally verified. Final QC and hypothesis-specific cohort approval
remain separate. No blanket preprocessing or L1 rerun is needed.

RF1-only phase-resolved activation has also completed L1/L2 and its technical
audit. It is a separate analysis family, not a replacement for pooled full-trial
inputs. Start with the [current contrast-number crosswalk](CONTRAST_CROSSWALK.md)
before selecting phase-resolved inputs; it includes exact manifests and paths.

## Message to Cooper

Please take ownership of imaging-QC exclusions, hypothesis-specific cohorts,
and pooled L3 designs. All current imaging processing was performed on Linux2.
The authoritative pooled analysis is `/ZPOOL/data/projects/sharedreward-aging`;
both datasets use its common full-trial model. Do not substitute the separate
RF1-only phase-resolved COPEs.

For the separate RF1-only phase-resolved activation analysis, **655 runs / 346
subject-sessions** are verified: **309 fixed-effects L2 + 37 L1 passthroughs**.
L2 is already complete. Use the [crosswalk and RF1 input manifest](CONTRAST_CROSSWALK.md#canonical-rf1-phase-resolved-family--activation-only).
In particular, **F-S (pun): full-trial 27 → RF1 phase-resolved 31** and
**F-C (pun): 28 → 32**. RF1 phase-resolved 27/28 are decision effects.
`F-C (rew-pun)` remains 16. Same names/numbers do not make the temporal
estimands interchangeable. SRNDNA phase-resolved validation and the new pooled
phase-resolved family remain outstanding; do not mix it with full-trial inputs.

The completed inventory is **744 runs / 393 subject-sessions**, with **1,488
verified L1 models and 786 verified subject-level outputs** (activation and
VS PPI). The [final audit](../logs/records/full-analysis-20260930-203949-441196/final/summary.json)
passes its computational gate. This is the starting inventory, not a final
approved post-QC group sample.

Settled decisions:

- AFNI target **6-mm total classic FWHM**, no additional FEAT smoothing.
- Keep contrast numbering; current **full-trial** task inference uses non-neutral COPEs
  **1–6, 10–19, 23–28**. Ignore neutral-containing COPEs 7–9 and 20–22 and
  physiology COPE29. Absent neutral trials alone do not exclude a run.
- RF1 phase-resolved **outcome** inputs instead use **1–6, 10–19, 23–26, 31–32**.
  Ignore neutral-containing contrasts there too; decision effects are separate.
- Use **raw ratings**, not within-person z-scores. Exclude the participant if
  **Loss > Win for any partner** (Computer, Stranger, or Friend); equality
  is allowed. Missing/invalid and all-six-identical ratings remain ineligible.
  This behavioral rule is primary until Cooper revises it.
- The behavioral cohort is **318 participants (285 RF1 + 33 ds003745)** before
  imaging QC. Ratings eligibility does not remove otherwise valid imaging
  models from the shared technical inventory.
- Imaging QC decisions are recorded in the [exclusion ledger](EXCLUSION_LEDGER.md).
  On 2026-10-05 the registered FD rule was applied as registered (47 runs;
  [decision file](exclusion_decisions/2026-10-05_high-motion.tsv)). No tSNR
  flags occur. Coverage flags and rf1 11012 run 1 remain pending review. Strictly >25% missed trials and documented
  task-invalid/source-missing runs are already removed from the task manifests.
- VS PPI is computationally verified but provisional pending seed provenance
  and hypothesis approval.

If a contributing run is excluded, rebuild the affected L2 using retained
runs, or use explicit L1 passthrough for a one-run subject. Do not simply
retain an old two-run fixed-effects COPE at L3.

## Working inputs and evidence

Paths are relative to this repository. Audit tables reference large model
files on Linux2; GitHub does not contain those images.

1. [Current status](CURRENT_STATUS.md): inventory and resolved source issues.
2. [Completed run record](../logs/records/20260930-163946_sharedreward-full-20260930-163946.md):
   preparation, paired activation/PPI execution, final audit, command exit 0.
3. [Frozen L1 manifest](../logs/records/full-analysis-20260930-203949-441196/L1-task-ready.tsv)
   and [subject manifest](../logs/records/full-analysis-20260930-203949-441196/L2-task-ready.tsv):
   exact task-valid units used in that run.
4. [Verified pre-QC candidates](../logs/records/full-analysis-20260930-203949-441196/final/verified-pre-QC-candidates.tsv):
   dataset/subject/session, model type, contributing runs, contrast, and
   COPE/VARCOPE/mask paths. **Its ratings flag predates the new behavioral rule.**
   For ratings-qualified analyses, join the current
   [behavioral eligibility table](../qc/ratings-raw/behavioral-eligibility.tsv)
   by dataset + subject, keeping `primary_included=true`. Do not use the
   older `ratings_eligible` flag or join by row order. Ratings are baseline;
   adding another session requires explicit handling.
5. [Run dispositions](../logs/records/analysis-run-dispositions.tsv),
   [subject dispositions](../logs/records/analysis-subject-dispositions.tsv),
   [input QC](../logs/records/analysis-qc-run-level.tsv), and
   [event QC](../logs/records/fulltrial-event-qc-run-level.tsv):
   task decisions, contributing runs, final-input tSNR, motion, coverage, and
   misses. Their historical ratings flags also predate the new rule.
6. [Exclusion policy](EXCLUSION_POLICY.md),
   [behavioral methods/results](RAW_RATINGS_ANALYSIS.md),
   [neutral decision](NEUTRAL_CONDITION_DECISION.md), and
   [contrast coefficients](../templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv).
7. [Current full-trial/phase-resolved crosswalk](CONTRAST_CROSSWALK.md):
   all contrast mappings, number collisions, model-family boundaries,
   exact RF1 L2/passthrough paths, and source/model commits.

Coverage excludes the historical inferior cerebellum/posterior brainstem
exemption from its fixed denominator. Whole-brain tSNR uses the full
TemplateFlow reference and final smoothed FEAT input. Neither is automatically
an approved L3 statistical mask. Source-validated raw rating means/provenance
remain in `logs/records/ratings-qc-subject-level.tsv`; its aggregate-rule flag
is superseded by the behavioral eligibility table, not a request to recover
ratings sources again.

## Resolved source issues

RF1 10657 run 1 is excluded and run 2 retained; 10668's reviewed reconstruction
is repaired and both corrected runs are included; the 11913/11923 source-series
review found no indicated reassignment or exclusion. The
[upstream decision record](https://github.com/DVS-Lab/rf1-sra-linux2/blob/main/docs/sharedreward-source-validity.md)
preserves the evidence and limitations. Do not reopen these as pending lab
questions or infer a Trust disposition. Older-dataset sub-144's corrected events
are already used; see [recovery provenance](SUB144_EVENT_RECOVERY.md).
RF1 10803's ratings recovery is incorporated, not a pending recovery task.

## Cooper's remaining deliverables

- A versioned run/subject decision ledger: reviewer/date, evidence, disposition,
  and exact scope; retain reasons rather than silently dropping rows.
- Hypothesis-specific cohorts and ordered inputs aligned to covariates by
  dataset + subject + session, with explicit missing-data handling. Do not
  automatically impose the behavioral cohort on every imaging hypothesis.
- Rebuilt affected subject outputs after run exclusions, followed by validation
  against final retained-run manifests and selected non-neutral contrasts.
- L3 designs/contrasts, covariates, rank/estimability checks, approved analysis
  mask, inference/multiplicity plan, and final PPI seed decision.

Do not assume residual images remain: existing workers clean residual files.
Check availability before choosing an inference procedure requiring them.
Computational provenance records image size/mtime, not full 4D hashes; the
group audit compares EVs with harmonized events, not raw source behavior.
Keep identifying DICOM/session details private.

The previous September handoff is preserved in
[Git history](https://github.com/DVS-Lab/sharedreward-aging/blob/6e6fe40/docs/COOPER_HANDOFF.md).
Its pilot-only and pending-source-review statements are superseded.
