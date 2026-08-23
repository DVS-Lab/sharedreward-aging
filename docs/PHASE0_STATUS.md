# Phase 0 status

Status date: 2026-08-23. Production target smoothing is approved at 6 mm total classic FWHM. No new full-cohort L1/L2/L3 analysis has been launched.

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
| ds003745 grid resampling | All 100 identity-grid `wsinc5` BOLD and nearest-neighbor mask derivatives passed exact RF1-grid verification. |
| Baseline smoothness | All 865 classic/ACF characterization units passed: 665 RF1 native, 100 ds003745 native, and 100 ds003745 post-`wsinc5`. |
| Resampling effect on smoothness | `wsinc5` increased ds003745 classic FWHM by 0.259 mm on average, versus 0.717 mm under superseded cubic interpolation. |
| Candidate targets | Complete. Every analysis-ready run is below 5 mm classic FWHM; 6 mm is attainable for all runs. |
| Pilot achieved smoothing | Passed. RF1 achieved 5.728 mm classic/9.153 mm ACF-effective; ds003745 achieved 5.993 mm classic/9.084 mm ACF-effective. The larger ACF scale is retained for sensitivity review and does not replace the classic target. |
| tSNR | Shared definition and implementation established (temporal mean/sample temporal SD); real cross-dataset results pending. |
| Motion/coverage/outliers | Table/report scaffolding implemented; real values pending. |
| Target recommendation | Approved: 6 mm total classic FWHM. Rationale: approximately twice the 2.7–2.97 mm voxel dimensions, accommodates cross-age anatomical heterogeneity, and remains the upper acceptable bound for spatial specificity in small regions. |
| Template decisions | Authoritative RF1 activation is 14 EVs/34 contrasts/0-mm FEAT smoothing. The inherited `C_neu` temporal-filter flag remains pending explicit review. Historical aging vectors are not authoritative. |
| Pooled temporal model | Recommend reviewing the common full-trial model as primary. A block model is a ds003745 sensitivity candidate, not silently a pooled primary model. |

## Next real-data step

On Linux2, after pulling this repository:

1. build the frozen 765-run production smoothing manifest;
2. launch restartable full-cohort target smoothing through `nohup` and `run_logged.sh`;
3. require complete geometry, classic, and ACF QC before any L1 launch;
4. retain the target-encoded derivatives and keep FEAT smoothing at zero;
5. cross-check final-model residual smoothness with FSL before pooled inference and, only if warranted, create a separate non-overwriting 5-mm sensitivity derivative;
6. keep pooled L3 out of scope until dataset-specific L1/L2 outputs and QC are complete.
