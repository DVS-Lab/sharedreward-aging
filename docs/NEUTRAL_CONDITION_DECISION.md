# Neutral-condition inferential decision

Decision date: 2026-09-04.

## Decision

Neutral trials remain part of the common nine-condition first-level design when
they are observed, but neutral is not part of the primary inferential contrast
set. The same rule applies to RF1 and ds003745 and to activation and seed-PPI
models.

A run with zero trials in one or more neutral cells remains eligible. Its empty
neutral psychological EV, and the corresponding PPI interaction EV, are
rendered with FEAT shape 10 (empty). The workflow never invents a neutral event
or substitutes a different trial. A zero-count reward or punish cell remains a
model-review hold because it is required by the primary contrasts.

## Rationale

Neutral cells have too few trials for stable planned inference, and occasional
zero cells are an expected consequence of the task realization rather than a
failure of otherwise valid reward/punish data. The planned questions concern
reward, punish, partner, and their interactions. Retaining observed neutral
trials in the design accounts for their task-related variance without claiming
adequate support for neutral inference. Allowing an explicitly empty neutral EV
also preserves valid reward/punish information from affected runs without
fabricating data.

The actual contrast coefficients were audited rather than inferred from their
labels. Six former contrasts had nonzero neutral weights and were removed from
the active pooled contract:

- `C_neu`, `F_neu`, and `S_neu`;
- `F-S (rew-neu)`, `S-C (rew-neu)`, and `F-C (rew-neu)`.

The retained `F-(S+C) all` label is historical: its actual vector weights only
reward and punish; all three neutral coefficients are zero. The active contract
therefore contains 22 activation copes. PPI applies those same 22 vectors to the
interaction EVs and adds one physiological cope, for 23 total.

## Enforcement

- `templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv` is the shared contrast source
  for both datasets and both L1 analysis types. Every active vector must have
  zero weights for neutral and missed-trial EVs.
- `code/render_pooled_fsf.py` rejects a contrast table that violates that rule.
- `code/generate_l1_evs.py` permits empty neutral files but rejects empty
  reward or punish EVs.
- `code/L1stats.sh` maps empty neutral psychological and PPI interaction EVs to
  FEAT shape 10 and requires all reward/punish EVs to be nonempty.
- `code/build_analysis_cohort.py` admits neutral-only zero-count runs and keeps
  non-neutral zero-count runs on model-review hold.

If neutral inference is later demanded during review, it will be treated as a
separate sensitivity analysis with an explicitly supported cohort and contrast
contract. It will not silently alter the primary model or its cope numbering.

Based on the frozen manifests available when this decision was recorded,
rebuilding on Linux2 is expected to move all 17 neutral-only holds into the
task-ready set: 737 L1 runs and 391 subject-sessions (346 two-run fixed-effects
units and 45 one-run passthroughs). These are expectations to be verified by
the logged rebuild, not replacements for its generated audit records.

## Validation and migration (2026-09-14)

Real installed FSL `feat_model` was exercised for activation and PPI, with all
neutral nuisance EVs empty or present and the missed-trial nuisance EV empty or
present (eight cases). Every matrix was finite and every retained contrast was
estimable by row-space projection. Empty nuisance columns can make the full
design rank deficient without making the active contrasts non-estimable.
The reproducible check is `code/verify_neutral_feat_design.py`; its tracked
numerical report is `logs/records/20260914-neutral-feat-design.json`.
This tests design construction, not a completed Linux2 FEAT model or its image QC.

The upstream sub-144 correction and the old-to-new cope migration are described
in [SUB144_EVENT_RECOVERY.md](SUB144_EVENT_RECOVERY.md). Do not reuse unstamped
old-contract models or treat the earlier projected cohort counts as current.
