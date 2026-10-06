# Archived: February 2026 exclusion and L3 model pipeline

**Archived 2026-10-05. Do not run it.** This is Cooper's original HPC pipeline (`exclusion-pipeline.sh`, steps 01–10) and its outputs for the N = 288 sm-5 / model-1 analysis. It is kept as a historical record. Step 0 of `exclusion-pipeline.sh` deletes every `.tsv`/`.csv` and the `models/` directory next to it, and its paths point at the old `/gpfs/scratch` tree.

## What replaced each step

| Step | Legacy behavior | Current replacement |
|---|---|---|
| 01 ratings | Aggregate rule (loss sum > win sum) on `logs-cleaned` files | `code/audit_ratings_qc.py` → `qc/ratings-raw/behavioral-eligibility.tsv`, using the within-partner Loss > Win rule on validated raw six-cell sources (`docs/RAW_RATINGS_ANALYSIS.md`) |
| 02 missing BOLD | BIDS file-existence check | Frozen task-ready manifests and `logs/records/analysis-run-dispositions.tsv` |
| 03 >25% misses | Line counts in legacy EV files | `code/audit_event_qc.py` on harmonized full-trial events |
| 04 tSNR / FD | MRIQC IQMs; IQR thresholds pooled across studies; auto-exclusion | `code/audit_analysis_qc.py` on the final smoothed FEAT input; IQR per dataset; flags reviewed in the ledger |
| 05 coverage | Run-mask coverage plus vmPFC coverage, IQR per study | Coverage-eligible TemplateFlow mask with a fixed denominator. **vmPFC/ROI coverage has no current equivalent**; handle it per hypothesis if needed |
| 06–07 combine / summarize | Wide run01/run02 flags → `usable_subjects.csv` | `docs/exclusion_ledger.tsv` with `code/build_exclusion_ledger.py` and `code/resolve_exclusion_ledger.py` (`docs/EXCLUSION_LEDGER.md`) |
| 08 z-scored ratings | Within-person z-scores | Superseded: raw ratings are primary |
| 09–10 L3 design files | `fsl_model.tsv` and `models/*.csv` | **Not yet replaced.** A new L3 design builder should read `logs/records/exclusion-ledger/candidates.tsv` |

## Issues not to carry into the new L3 builder

- `gender_M` and `gender_F` were both entered with an intercept (r = −0.96, VIF ≈ 15). Use a single sex code.
- `flip` coded 20°, 76° and "not in `code/flip-angles.csv`" all as 0. That last group includes every ds003745 and every later RF1 subject.
- tSNR and FD covariates were MRIQC values averaged across runs, not values for the runs that actually entered each subject's COPE.
- `code/L3paths.sh` picks inputs by whether a file exists rather than by recorded decisions. It also falls back from L2 `cope4.feat` to L1 `cope1`, which is a different contrast.

## Recorded decision

Commit `71e1491` changed rf1 sub-11012 from its L2 input to an L1 run-2 passthrough, so run 1 was dropped. No reason was recorded. It is carried as a `pending_review` row in `docs/exclusion_ledger.tsv`.
