# Phase 0 hard-stop status

Status date: 2026-08-23. No production smoothing target has been selected and no new full-cohort L1/L2/L3 analysis has been launched.

| Required report item | Current status |
|---|---|
| Modern fMRIPrep | Wrapper pins Linux2's `fmriprep-25.2.5.simg`; ds003745 output is `MNI152NLin6Asym` only, without FreeSurfer. The 50-subject/100-run cohort completed on Linux2 and passed the completeness audit. |
| Successful ds003745 pilot subjects | The pilot passed and the complete 50-subject cohort was processed. |
| Historical raw behavioral logs | Not found in the checked local aging or public data-paper repositories. |
| Phase-resolved ds003745 reconstruction | Not performed and no longer required. Exact phase timing is not supported by the published representation. |
| Unrecoverable event information | Exact historical decision/outcome phase boundaries. Published full-trial and block timing remains available. |
| ds003745 public event audit | 50 subjects, 100 runs, 7,200 trials, 900 blocks; all runs have 72 trials and 9 blocks. All 100 model-specific conversions passed. |
| RF1 reference grid | The signal-free RF1 reference resource was created from the verified modal `MNI152NLin6Asym` grid. |
| RF1 grid consistency | The upstream fMRIPrep BOLD/mask geometry audit and repair completed; Shared Reward analysis inputs now match the authoritative grid. |
| ds003745 grid resampling | Identity-grid `wsinc5` BOLD and nearest-neighbor mask utilities plus exact grid checks are implemented. Existing cubic BOLD derivatives must be regenerated before target selection. |
| Baseline smoothness | The 865-unit classic/ACF audit completed without missing units under the prior cubic derivative; the 100 ds003745 post-resampling rows must be refreshed after `wsinc5` regeneration. |
| Resampling effect on smoothness | Cubic interpolation increased classic FWHM by about 0.72 mm on average and is now superseded. The paired effect must be recomputed after `wsinc5`. |
| Candidate targets | The cubic-derived table is superseded. One classic-FWHM target no greater than 6 mm will be selected after the `wsinc5` refresh. |
| Pilot achieved smoothing | Pending. No target was guessed. |
| tSNR | Shared definition and implementation established (temporal mean/sample temporal SD); real cross-dataset results pending. |
| Motion/coverage/outliers | Table/report scaffolding implemented; real values pending. |
| Target recommendation | None final yet. Classic FWHM is the matched-preprocessing stopping metric; ACF is retained for diagnostics and later residual-based inference. |
| Template decisions | Authoritative RF1 activation is 14 EVs/34 contrasts/0-mm FEAT smoothing. The inherited `C_neu` temporal-filter flag remains pending explicit review. Historical aging vectors are not authoritative. |
| Pooled temporal model | Recommend reviewing the common full-trial model as primary. A block model is a ds003745 sensitivity candidate, not silently a pooled primary model. |

## Next real-data step

On Linux2, after pulling this repository:

1. regenerate all 100 ds003745 harmonized BOLD files from the untouched fMRIPrep outputs using identity-grid `wsinc5`; masks remain nearest-neighbor;
2. require the independent 100-run grid audit to pass;
3. overwrite only the 100 ds003745 post-resampling smoothness results;
4. regenerate the consolidated 865-unit audit and compare paired native/`wsinc5` estimates;
5. select one attainable classic-FWHM target at or below 6 mm, then stop again for approval before production smoothing.
