# Cooper's contrast crosswalk: current full-trial vs RF1 phase-resolved

Verified 2026-10-05 against the active pooled renderer, all original/real
contrast weights, the RF1 template, and completed RF1 run provenance.
This is a crosswalk between existing model families, **not a renumbering or
change to any model**. C = computer, F = friend, S = stranger; `pun` is loss,
`rew` is win, and `dec` is decision.

## The two number changes that matter for outcome analyses

| Contrast | Pooled full-trial COPE | RF1 phase-resolved activation COPE |
|---|---:|---:|
| F-S (pun) | 27 | 31 |
| F-C (pun) | 28 | 32 |

**Do not copy the full-trial COPE list into the RF1 phase-resolved tree.**
RF1 phase-resolved COPE27 and COPE28 are friend/stranger decision effects,
not punishment contrasts. The key `F-C (rew-pun)` contrast remains COPE16
in both families.

## Complete current outcome crosswalk

The full-trial number applies to both its activation and PPI models, but
PPI rows weight interaction EVs, not activation EVs. There is no validated
RF1 phase-resolved PPI mapping in this handoff.

| Contrast name | Full-trial activation/PPI COPE | RF1 phase-resolved activation COPE | Scope |
|---|---:|---:|---|
| C_pun | 1 | 1 | Outcome |
| C_rew | 2 | 2 | Outcome |
| F_pun | 3 | 3 | Outcome |
| F_rew | 4 | 4 | Outcome |
| S_pun | 5 | 5 | Outcome |
| S_rew | 6 | 6 | Outcome |
| C_neu | 7 | 7 | Ignore: neutral |
| F_neu | 8 | 8 | Ignore: neutral |
| S_neu | 9 | 9 | Ignore: neutral |
| rew-pun | 10 | 10 | Outcome |
| F-S | 11 | 11 | Outcome |
| F-C | 12 | 12 | Outcome |
| (F+S)-C | 13 | 13 | Outcome |
| F-S (rew-pun) | 14 | 14 | Outcome |
| S-C (rew-pun) | 15 | 15 | Outcome |
| F-C (rew-pun) | 16 | 16 | Outcome |
| F-S (rew) | 17 | 17 | Outcome |
| S-C (rew) | 18 | 18 | Outcome |
| F-C (rew) | 19 | 19 | Outcome |
| F-S (rew-neu) | 20 | 20 | Ignore: neutral |
| S-C (rew-neu) | 21 | 21 | Ignore: neutral |
| F-C (rew-neu) | 22 | 22 | Ignore: neutral |
| F-(S+C) all | 23 | 23 | Outcome |
| F-(S+C) rew | 24 | 24 | Outcome |
| F-(S+C) pun | 25 | 25 | Outcome |
| F-(S+C) rew-pun | 26 | 26 | Outcome |
| F-S (pun) | 27 | 31 | Outcome |
| F-C (pun) | 28 | 32 | Outcome |

The nine outcome coefficient patterns match by name across these two activation
contracts, with zero weights on their other EVs. **Their temporal estimands
still differ:** full-trial spans the broader trial; RF1 phase-resolved models
outcomes separately from decisions. Equal names or weights do not permit
mixing their images in one L3 model. The PPI contract applies the same
coefficient patterns to its interaction block, a third distinct measure.

The non-neutral outcome sets are:

- Full-trial: **1–6, 10–19, 23–28**.
- RF1 phase-resolved activation: **1–6, 10–19, 23–26, 31–32**.

These are eligible contrast families, not approval to test every contrast
without a hypothesis/multiplicity plan. `all` in COPE23 does not imply a
neutral weight: the actual neutral coefficients are zero.

## Other slots: do not confuse these across models

| RF1 phase-resolved COPE | Name | Full-trial counterpart |
|---:|---|---|
| 27 | F_dec | None; full-trial COPE27 is F-S (pun) |
| 28 | S_dec | None; full-trial COPE28 is F-C (pun) |
| 29 | C_dec | None; full-trial PPI COPE29 is physiology |
| 30 | Face v Non-Face | None |
| 33 | F-S (dec) | None |
| 34 | F-C (dec) | None |

RF1 decision effects were technically checked but are not primary outcome
inputs. Full-trial activation has 28 contrasts; full-trial PPI has 29,
including physiology `phys` at 29, excluded from task inference.
Neutral-containing contrasts 7–9 and 20–22 remain ignored in both families.
An absent neutral EV alone does not exclude a run; FSL may zero its pure-neutral
actual contrast row without changing the canonical FSF definition or numbering.

## Where Cooper gets the images

### Existing pooled full-trial family — both datasets, activation and VS PPI

Model family: `fulltrial-retained-contrasts-v3`.
Root: `/ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/`.
Use the frozen [verified pre-QC candidates](../logs/records/full-analysis-20260930-203949-441196/final/verified-pre-QC-candidates.tsv)
for exact contrast, model type, contributing runs, COPE and VARCOPE paths.
This remains the completed pooled family; no existing output was replaced.

### Canonical RF1 phase-resolved family — activation only

Root: `/ZPOOL/data/projects/rf1-sra-sharedreward/derivatives/fsl/`.
The completed audit verifies **655 runs / 346 subject-sessions**, comprising
309 two-run fixed-effects outputs and 37 single-run passthroughs.
Use the frozen [verified RF1 subject-output manifest](https://github.com/DVS-Lab/rf1-sra-sharedreward/blob/d5331d38c298023eeaf094e6e83ee0df65434ac2/logs/records/phase-resolved-20261005-144746/verified-subject-outputs.tsv)
and [completed audit](https://github.com/DVS-Lab/rf1-sra-sharedreward/blob/d5331d38c298023eeaf094e6e83ee0df65434ac2/logs/records/phase-resolved-20261005-144746/audit.md).

Given that manifest's `output` and the RF1 contrast number N above:

| Strategy | COPE path | VARCOPE path |
|---|---|---|
| `fixed_effects` | `<output>/copeN.feat/stats/cope1.nii.gz` | `<output>/copeN.feat/stats/varcope1.nii.gz` |
| `l1_passthrough` | `<output>/stats/copeN.nii.gz` | `<output>/stats/varcopeN.nii.gz` |

The mask is `<output>/copeN.feat/mask.nii.gz` for fixed effects and
`<output>/mask.nii.gz` for passthrough. **Inside an L2 copeN directory,
the result is cope1, not copeN.** For example, RF1 F-C (pun) uses
`cope32.feat/stats/cope1.nii.gz`, while the pooled full-trial fixed-effects
result uses `cope28.feat/stats/cope1.nii.gz`.

Before freezing L3 inputs, validate names/vectors in each source L1
`design.fsf`/`design.con` and the L2 contributing-run linkage, not merely
filenames or an L2 child contrast called `mean`. Existing execution audits
perform these checks for the recorded pre-QC inputs. If Cooper drops a
contributing run, rebuild only the appropriate model-family L2 or select the
retained L1 passthrough; do not retain an old two-run output.

RF1 canonical L1 need not be refit for an aging-specific retained-run change.
Any newly needed aging-specific phase-resolved L2 belongs in a separate
`sharedreward-aging/derivatives/fsl-phase-resolved/rf1/` namespace with explicit
source L1 provenance. This is a prospective destination, not a claim that
those project-specific outputs already exist.

## Handoff boundary and provenance

Cooper can proceed with QC/L3 for the completed pooled full-trial family and
separately with RF1-only phase-resolved activation. The proposed pooled
`phase-resolved-outcome-v1` family is **not yet complete**: this RF1 result
does not establish SRNDNA phase reconstruction/model validation, cross-dataset
phase-resolved inputs, or phase-resolved PPI. Do not fill the SRNDNA half with
full-trial COPEs. Neither estimand is automatically promoted to manuscript primary.

Current numbering sources:

- [Active full-trial coefficient contract](../templates/FULLTRIAL_CONTRAST_CANDIDATE.tsv)
  and [renderer](../code/render_pooled_fsf.py). Despite the historical
  `CANDIDATE` filename, these define the completed v3 fits.
- [RF1 canonical template at model commit 562f0d1](https://github.com/DVS-Lab/rf1-sra-sharedreward/blob/562f0d15e0ac370a69ea36d40fdcb23f5e20f597/templates/L1_task-sharedreward_model-1_type-act.fsf)
  and [completed RF1 contrast provenance](https://github.com/DVS-Lab/rf1-sra-sharedreward/blob/d5331d38c298023eeaf094e6e83ee0df65434ac2/logs/records/phase-resolved-20261005-144746/provenance.json).
- [Machine-readable verification/crosswalk](../logs/records/20261005-contrast-crosswalk-verification.json):
  all 28 common contrast names, both current COPE numbers, nine outcome
  coefficients, neutral flags, RF1-only decision vectors, source hashes and SHAs.

Do not use the historical `sharedreward_aging_cope` column in RF1's older
`CONTRAST_CROSSWALK.tsv` as the current pooled-v3 numbering. That column
describes a legacy 32-contrast template, not the completed 28/29-contrast fits.
This documentation update reads tracked execution evidence; it is not a new
live audit of Linux2 images and changes no model files or exclusion decisions.
