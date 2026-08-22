# Phase 0 hard-stop status

Status date: 2026-08-22. No production smoothing target has been selected and no new full-cohort L1/L2/L3 analysis has been launched.

| Required report item | Current status |
|---|---|
| Modern fMRIPrep | Wrapper pins Linux2's `fmriprep-25.2.5.simg`; ds003745 output is `MNI152NLin6Asym` only, with 16 processes/8 OMP threads/48 GB defaults. Command rendering passed; no real pilot was run on this Mac clone. |
| Successful ds003745 pilot subjects | None yet. Selective DataLad retrieval and Linux2/Apptainer execution are required. |
| Historical raw behavioral logs | Not found in the checked local aging or public data-paper repositories. |
| Phase-resolved ds003745 reconstruction | Not performed and no longer required. Exact phase timing is not supported by the published representation. |
| Unrecoverable event information | Exact historical decision/outcome phase boundaries. Published full-trial and block timing remains available. |
| ds003745 public event audit | 50 subjects, 100 runs, 7,200 trials, 900 blocks; all runs have 72 trials and 9 blocks. All 100 model-specific conversions passed. |
| RF1 reference grid | Audit and zero-grid creation utilities are implemented. Exact dimensions/affine and the signal-free NIfTI remain pending execution against Linux2 derivatives. |
| RF1 grid consistency | Pending Linux2 whole-inventory audit. A nonzero unique-grid count will stop the workflow. |
| ds003745 grid resampling | Cubic BOLD and nearest-neighbor mask utilities plus exact grid checks are implemented; real-data validation awaits the fMRIPrep pilot and RF1 resource. |
| Baseline smoothness | Measurement utility implemented; real RF1/ds003745 distributions pending Linux2/AFNI execution. |
| Resampling effect on smoothness | Pending paired pre/post ds003745 pilot measurements. |
| Candidate targets | Proposal utility implemented; no candidate table can be scientifically populated before baseline measurements. |
| Pilot achieved smoothing | Pending. No target was guessed. |
| tSNR | Shared definition and implementation established (temporal mean/sample temporal SD); real cross-dataset results pending. |
| Motion/coverage/outliers | Table/report scaffolding implemented; real values pending. |
| Target recommendation | None yet. Historical 5/6-mm settings are explicitly not recommendations. |
| Template decisions | Authoritative RF1 activation is 14 EVs/34 contrasts/0-mm FEAT smoothing. The inherited `C_neu` temporal-filter flag remains pending explicit review. Historical aging vectors are not authoritative. |
| Pooled temporal model | Recommend reviewing the common full-trial model as primary. A block model is a ds003745 sensitivity candidate, not silently a pooled primary model. |

## Next real-data pilot

On Linux2, after pulling both repositories:

1. run the RF1 whole-inventory grid audit and review its JSON;
2. create/commit the zero-valued reference resource only if the RF1 inventory has one grid;
3. selectively retrieve several ds003745 participants with both runs, anatomy, and fieldmaps;
4. run fMRIPrep 25.2.5 for those participants and review HTML reports;
5. produce model-specific full-trial event derivatives and parity summaries;
6. resample pilot BOLD/masks to the RF1 grid and require exact equality;
7. measure pre/post-resampling smoothness and tSNR, then pilot multiple candidate targets;
8. generate the consolidated report and stop again for target/model approval.
