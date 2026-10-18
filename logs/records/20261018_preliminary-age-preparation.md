# Preliminary age analysis preparation and behavioral inventory

Date: 2026-10-18. Parent repository commit: `228a0fb`.
User requested basic age effects on activation and connectivity, a behavioral
inventory, and confirmed both whole-brain and ROI summaries.

## State reviewed

- Cooper's exclusion decisions retain 663 runs / 358 people: 315 RF1 and 43
  ds003745; 305 fixed-effects subjects and 53 retained-L1 passthroughs.
- 290 are imaging-and-ratings eligible. The current ratings-only analysis is
  still 318 (285 RF1 and 33 ds003745); it was not silently restricted to 290.
- The latest tracked post-QC readiness audit failed on Linux2 permission
  errors. It cannot establish that new L3 inputs are ready. No FEAT rerun or
  permission change was performed on that basis.
- Current primary behavior is raw ratings with the within-partner Loss > Win
  exclusion; equality allowed. Historical z-score/cluster extractions were
  inventoried as legacy, not promoted to current results.

## Local verification

- Recomputed all 24 cell-age slopes (four scopes), HC3 SEs, p-values and
  six-cell Holm corrections from the source ratings audits and canonical
  participant tables; matched tracked output at rtol 1e-10, atol 1e-12.
- Recomputed all seven paired follow-ups and matched their numeric output.
- Recomputed all 20 joint/decomposed age tests across the four scopes and
  matched the tracked numeric output at the same tolerances.
- New plan-only invocation with current retained manifests yields 358 people,
  663 runs, complete age/sex/motion, a full-rank six-column design, condition
  number 29.684. Age spans 20–89 years. Retained FD is weighted by valid FD
  volumes, excluding removed runs. Subject-level joins stay under ignored
  derivatives. The [plan](preliminary-age/age-plan-20261018/plan.json) records
  exact source/code hashes; its parent commit alone does not include the new
  working-tree script.
- Five new synthetic tests passed: design/HC3, rank failure, ordered candidates
  and excluded-run rejection, merged NIfTI ordering/common ROI coverage, and
  FSL 1−p interpretation with 20-map correction.
- Real local FSL randomise smoke test passed: synthetic 40-person data,
  two dataset exchangeability blocks, both age signs, 5,000 permutations,
  fixed seed, TFCE and both corrected output maps. This was synthetic data,
  not a production imaging result.
- Full repository validation passed: Bash/Python syntax and 99 unit tests.

## Scope and remaining execution

The new isolated launcher audits retained L1/L2 inputs first, then fits ten
whole-brain models and 15 provisional ROI tests. No production imaging age
effects have been computed locally: model images are on Linux2. The launch
command and statistical assumptions are in
[PRELIMINARY_AGE_ANALYSIS.md](../../docs/PRELIMINARY_AGE_ANALYSIS.md).

No existing task templates, L1/L2 workers, exclusions, model outputs, or primary
behavioral result files were changed. No raw participant demographics were
added to Git. Run records and aggregate outputs from the Linux2 execution
must be reviewed before interpreting imaging findings.
