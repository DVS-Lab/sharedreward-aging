# Phase 0 status

Reconciled 2026-09-15. The spatial preprocessing decision is complete and fixed:
**6 mm total classic FWHM**, with no additional FEAT smoothing. This is not a
statement that all pooled FEAT models have run. The authoritative execution,
cohort and review snapshot is [CURRENT_STATUS.md](CURRENT_STATUS.md); the
[Cooper handoff](COOPER_HANDOFF.md) separates exclusion/design preparation from
permission to execute final L3 inference.

## Completed work

| Stage | Evidence-backed status |
|---|---|
| ds003745 preprocessing | 50 participants / 100 runs processed on Linux2 with fMRIPrep 25.2.5; no FreeSurfer or multi-echo processing required. |
| Grid harmonization | Signal-free RF1 modal MNI152NLin6Asym reference established; all 100 ds003745 wsinc5 BOLD / nearest-neighbor mask derivatives passed RF1-grid verification. |
| Smoothing decision | Initial 865 characterization units = 665 RF1 runs + 100 older runs at two stages. Target fixed at 6 mm total classic FWHM; ACF retained separately. |
| Original production/control comparison | 765 unique runs; all 2,295 SUSAN/baseline/AFNI measurements complete. Nominal 6-mm SUSAN produced mean total classic FWHM 8.260 mm (ds003745) and 7.919 mm (RF1), versus 5.775 and 5.852 mm for AFNI total-target outputs. No target change is pending. |
| Incremental 12032 runs | Both reported DONE for smoothing on September 2 and passed the 767-run analysis-input QC audit. They are no longer pending catch-up. |
| Analysis-input QC | 767/767 measured; 88 flagged runs / 61 participants. tSNR is from final smoothed FEAT input; motion from named fMRIPrep confounds; coverage uses TemplateFlow minus the historical cerebellum/posterior-brainstem exemption. Flags are not automatic exclusions. |
| Current events | September 15 refreshed 765 event units, with 19 runs strictly >25% missed trials. The two remaining RF1 source gaps are 11450 r2 and 12037 r2. No new neutral-related holds. |
| ds003745 source correction | Raw logs now exist in srndna-datapaper; guarded sub-144 full-trial recovery and downstream regeneration completed. The old statement that no raw logs were found is historical, not current. Phase-resolved older-dataset reconstruction is not required. |
| ds003745 FSL nuisance matrices | September 15 audit: 100 complete, zero incomplete. RF1 consumes Linux2's existing TEDANA-plus-confounds without duplication. |
| Pooled cohort preparation | 744 task-ready runs / 393 subject-sessions; 23 task-excluded runs; zero reward/punish model-review holds. Final scientific and ratings eligibility remain separate. |
| Pooled v3 pilot | Corrected sub-144 runs 1/2 passed activation and provisional VS-PPI L1 plus both fixed-effects outputs on September 15. Retained contract: 28 activation / 29 PPI contrasts, not the superseded 22/23 version. |

## Evidence still to close, without reprocessing

The September 2 smoothing catch-up exited 1 for the already-accepted RF1
10657 r1 convergence exception (approximately 5.280 mm), so its consolidated
check was skipped. Current code consumes the exact bounded exception table.
A read-only consolidated 767-run smoothing audit should record closure; do not
repeat smoothing or relax the global tolerance. This issue is unrelated to the
newly surfaced scientific question about 10657's friend stimulus.

RF1 10803's exact recovered ratings source passes the current rules, but the
tracked ratings table is stale. Refresh ratings discovery/audit and then the
cohort; the recorded 655-run / 346-subject-session ratings-qualified counts
are not final. Keep the task-ready and ratings-qualified cohorts distinct.

## Next steps, not a restart of Phase 0

1. Close the two evidence refreshes above and carry the upstream 10657, 10668
   and 11923 scientific-review questions into the final decision ledger.
2. Review imaging flags and hypothesis-specific exclusions with Cooper/PI;
   record seed-provenance and scientific PPI decisions separately from the
   successful provisional VS-PPI implementation test.
3. Generate/verify the full retained-run EV set, then execute outstanding pooled
   activation and PPI together using bounded paired concurrency. Do not use
   RF1-only phase-resolved COPEs as pooled full-trial inputs.
4. Audit primary L1 outputs, form two-run fixed effects or one-run passthrough
   from the actual retained runs, and repeat the non-neutral group-readiness
   audit. Only sub-144 is currently verified under this definitive contract.
5. Freeze the hypothesis-specific ordered group inputs, covariates, model,
   statistical mask and inference plan before L3 execution. Do not treat a
   partial verified-candidate table as a completed cohort.

Underlying records, exact counts and remaining code-integration limits are
linked in [CURRENT_STATUS.md](CURRENT_STATUS.md). Prior Phase 0 status tables
and numerical snapshots remain recoverable in Git history.
