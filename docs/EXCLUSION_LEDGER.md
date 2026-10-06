# Exclusion ledger

[`exclusion_ledger.tsv`](exclusion_ledger.tsv) is the versioned record of run and subject exclusion decisions. Each row is one unit × one criterion, and it keeps its evidence and reason. Git history is the version record: commit the ledger whenever you record decisions.

## Workflow

1. `python3 code/build_exclusion_ledger.py` seeds or refreshes the ledger from the frozen QC evidence. Rebuilding keeps reviewer decisions on pending rows and keeps manual rows untouched.
2. To decide `pending_review` rows, write a decision file in [`exclusion_decisions/`](exclusion_decisions/) with `ledger_id`, `disposition`, `reviewer`, `review_date` (YYYY-MM-DD) and `rationale`. Apply it with `python3 code/apply_ledger_decisions.py docs/exclusion_decisions/<file>.tsv`. Only pending rows can be decided this way, and a file can't be applied twice. When a run is excluded for one criterion, mark its other pending rows `not_applicable` in the same file. The builder rejects incomplete decisions.
3. To record a finding the seeder does not generate (for example visual QC), add a row with `origin=manual`. Use `run=*` for a whole subject.
4. `python3 code/resolve_exclusion_ledger.py` writes the following to `logs/records/exclusion-ledger/`:
   - `retained-L1.tsv` and `retained-L2.tsv`, which use the frozen manifests' schemas.
   - `candidates.tsv`, the frozen COPE candidates with current `ratings_eligible`. Removed subjects are dropped, and subjects that lost a run are marked `input_status=requires_rebuild` with blank COPE paths. Use this file for L3 joins instead of the frozen `verified-pre-QC-candidates.tsv`.
   - `subject-status.tsv`.
   - `rebuild-list.tsv`.
   - `pending-review-units.tsv`, the analysis-QC rows for runs that still have pending imaging rows. It is the input for the Linux2 review commands below.
   - `summary.tsv`, which always shows two bounds: every pending row retained and every pending row excluded.
   - `provenance.json`.

   Use `--pending fail` when you build the final L3 inputs.

## Columns that matter

- `applies_to`:
  - `imaging_all` rows remove runs from every imaging analysis.
  - `ratings_qualified` rows (the primary behavioral rule) only set `ratings_eligible` and never remove imaging runs.
- `decision_basis`:
  - `automatic_rule` rows are refreshed from the evidence on every rebuild.
  - `curated_record` rows mirror [`curated_run_exclusions.tsv`](curated_run_exclusions.tsv). Make task-validity changes there, then rebuild the cohort and the ledger.
  - `reviewer` rows are where you record decisions.
- `disposition=not_applicable` marks an imaging flag on a run that is already task-excluded.
- `evidence_status=stale` marks a decided row whose seeded evidence no longer appears. It is kept so the decision is not silently lost.

## Current state (2026-10-05)

- **Thresholds:** IQR thresholds are recomputed per dataset over all 768 runs (stored in `logs/records/exclusion-ledger/iqr-thresholds.tsv`). They reproduce every recorded flag. [`qc/exclusion-review_distributions.png`](../qc/exclusion-review_distributions.png) (`code/plot_exclusion_review.py`) records the cohort distributions that were inspected.
- **High motion, decided:** Cooper applied the registered FD rule as registered to all 47 flagged task-ready runs ([decision file](exclusion_decisions/2026-10-05_high-motion.tsv)). Two coverage rows on those runs became `not_applicable`. Result: 697 runs / 371 subjects. 11 subjects drop to one run and 22 lose every run. Of the remaining imaging subjects, 302 also meet the ratings rule. The ratings-only cohort of 318 is unchanged. Flagged runs skew toward older participants, which is typical for motion; plan an FD covariate at L3 and report the ages of excluded subjects.
- **Low coverage, decided:** after the mosaic and ROI-coverage review, Cooper applied the registered coverage rule as registered to all 34 flagged runs, as one sample-level rule with no per-run or analysis-level exceptions ([decision file](exclusion_decisions/2026-10-05_low-coverage.tsv)). The review found six runs with field-of-view or registration failures (rf1 11960 runs 1–2, 11719 run 1, 11472 run 1; ds003745 120 run 01, 111 run 02). The other 26 rf1 runs lose about 1% of the mask in ventromedial orbitofrontal cortex, the upper tail of a gradual drift in ventral coverage across the later rf1 subject sequence. Retained later-enrolled runs still show lower vmPFC coverage than early ones (`roi-coverage.tsv`), which will shrink the group mask in ventral frontal cortex.
- **rf1 11012 run 1, retained:** the February 2026 pipeline (archived in `code/archive/exclusions-2026-02/`) dropped it, which Cooper attributes to a preprocessing issue in an earlier pipeline version. The reprocessed run passes all QC and its mosaic is clean ([decision file](exclusion_decisions/2026-10-05_sub-11012.tsv)).
- **Final imaging sample:** 663 runs / 358 subjects (35 subjects lose every run; 23 drop to one run). Of these, 290 also meet the ratings rule; the ratings-only cohort of 318 is unchanged. `resolve_exclusion_ledger.py --pending fail` succeeds.
- **Affected subjects:** all 23 subjects that lost a run now have one run, so they become L1 passthroughs and no new models are estimated. `candidates.tsv` already points their full-trial activation and VS-PPI inputs at the retained run's verified L1 COPE (`input_status=l1_passthrough_verified`, taken from the frozen `final/l1-audit.tsv`). `rebuild-list.tsv` lists them per family. The 22 rf1 subjects still need the same re-pointing in the RF1 phase-resolved manifest, which lives in the rf1-sra-sharedreward repository.
- **Old two-run outputs stay on disk:** each affected subject's two-run `L2_…_sm-6.gfeat` is still at its usual Linux2 path. `candidates.tsv` never uses them, but any tool that picks inputs because a file exists would. Quarantine or rename those directories on Linux2 before L3, and use only `candidates.tsv` for L3 inputs.

## Coverage review on Linux2

These commands produced the 2026-10-05 review evidence (`qc/coverage-mosaics/review-2026-10/`, `coverage-review-mosaics-*.tsv`, `roi-coverage.tsv`). Rerun them from the repository root on Linux2 if new pending runs appear:

```bash
python3 code/plot_coverage_mosaics.py --input logs/records/exclusion-ledger/pending-review-units.tsv --dataset rf1 --coverage-below 100 --output-dir qc/coverage-mosaics/review-2026-10 --summary-output logs/records/exclusion-ledger/coverage-review-mosaics-rf1.tsv
```

```bash
python3 code/plot_coverage_mosaics.py --input logs/records/exclusion-ledger/pending-review-units.tsv --dataset ds003745 --coverage-below 100 --output-dir qc/coverage-mosaics/review-2026-10 --summary-output logs/records/exclusion-ledger/coverage-review-mosaics-ds003745.tsv
```

```bash
python3 code/audit_roi_coverage.py --input logs/records/analysis-qc-run-level.tsv --roi vs=masks/seed-vs.nii.gz --roi vmpfc=masks/VMPFC-mask-neurovault-resliced-bin.nii.gz --output logs/records/exclusion-ledger/roi-coverage.tsv
```

The first two commands make mosaics for every pending run, including 11012 run 1. The third measures every run, so the flagged runs can be compared with the cohort. It reports the share of the VS PPI seed and of the vmPFC mask that each run covers, and the world-z range of the eligible voxels it misses. Missing voxels near the vertex are likely harmless. Missing voxels in inferior OFC or temporal cortex matter for vmPFC hypotheses. ROI coverage reflects field-of-view truncation and the severe signal dropout that the fMRIPrep BOLD brain mask leaves out. Milder dropout stays inside the mask, so 100% vmPFC coverage does not guarantee usable OFC signal (ROI tSNR would show that). It is review evidence, not a registered rule, and it does not settle the PPI seed choice.
