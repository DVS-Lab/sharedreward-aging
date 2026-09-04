# Phase 0 status

Status date: 2026-09-02. Production target smoothing is fixed at the approved 6 mm total classic FWHM. No new full-cohort L1/L2/L3 analysis has been launched.

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
| Baseline smoothness | The decision audit passed all 865 units: 665 RF1 native, 100 ds003745 native, and 100 ds003745 post-`wsinc5`. The current inventory adds two RF1 runs that use the fixed procedure without reopening the target decision. |
| Resampling effect on smoothness | `wsinc5` increased ds003745 classic FWHM by 0.259 mm on average, versus 0.717 mm under superseded cubic interpolation. |
| Candidate targets | Complete. Every analysis-ready run began below 5 mm classic FWHM. The 6-mm target passed the cohort tolerance for 764 runs; one stable run-specific convergence limit is handled by a tightly bounded, documented exception. |
| Pilot achieved smoothing | Passed. RF1 achieved 5.728 mm classic/9.153 mm ACF-effective; ds003745 achieved 5.993 mm classic/9.084 mm ACF-effective. The larger ACF scale is retained for sensitivity review and does not replace the classic target. |
| Production target smoothing | Complete and audited: 764 runs pass the common 5.4-6.6 mm tolerance. RF1 sub-10657/ses-01/run-1 reproducibly achieved 5.280 mm under both default and all-volume retries and is the sole bounded exception. Zero unresolved failures. |
| FEAT-equivalent SUSAN control | Complete: 765/765 runs and 2,295/2,295 method measurements. Nominal 6-mm SUSAN yielded mean total classic FWHM of 8.260 mm (ds003745) and 7.919 mm (RF1), versus 5.775 and 5.852 mm for the approved AFNI total target. Production remains AFNI target smoothing with FEAT smoothing zero. |
| tSNR | Complete for 765/765 final smoothed FEAT inputs. Mean run-level median tSNR is 133.358 for ds003745 and 108.670 for RF1; the full TemplateFlow mask is the fixed reference. |
| Motion/coverage/outliers | Complete for 765/765 runs with zero unresolved measurement failures. Motion uses named fMRIPrep confounds rather than the headerless FEAT nuisance matrix. Coverage preserves the historical cerebellum/posterior-brainstem exemption through a fixed TemplateFlow-minus-exemption denominator. Dataset-specific 1.5×IQR rules produced 89 review-flagged runs across 61 subjects: 12 ds003745 runs/8 subjects and 77 RF1 runs/53 subjects. These remain review flags, not automatic exclusions. The 33 RF1 low-coverage flags include 29 runs clustered between 98.43% and 99.15% coverage plus four materially lower runs, so the modern-mask result must be inspected before cohort freezing rather than assumed equivalent to the historical zero-RF1 exclusion count. |
| Missed trials | The August audit covered 758 runs. Upstream subsequently recovered five event sources and added two valid `sub-12032` runs. Only `sub-11450` run 2 and `sub-12037` run 2 remain source-missing. Rebuild the event audit before freezing final counts; the strict rule remains exclusion only when missed trials are greater than 25%. |
| Ratings | The 2026-09-02 audit covered 398 subjects and found 49 exclusions. RF1 `sub-10803` has since been restored exactly from Git history, so the ratings audit and qualified-cohort count must be refreshed. The 11 missing ds003745 files are absent from the pinned OpenNeuro inventory and repository history. Session-note review partitions the other RF1 gaps into confirmed non-collection/incompleteness, high-priority reported-complete recovery searches, and unresolved secondary searches; see `docs/SOURCE_GAPS.md` and `docs/rf1_ratings_source_notes.tsv`. |
| Cohort freezing | Implemented in `code/build_analysis_cohort.py`. It produces task-valid and ratings-qualified L1/subject-level manifests separately, applies the current missing-event, >25%-missed, and curated task exclusions, and holds zero-count-condition runs out of the common primary model. RF1 `sub-11539` is excluded because the wrong friend photo was displayed in both runs. |
| Target recommendation | Approved: 6 mm total classic FWHM. Rationale: approximately twice the 2.7–2.97 mm voxel dimensions, accommodates cross-age anatomical heterogeneity, and remains the upper acceptable bound for spatial specificity in small regions. |
| Template decisions | Authoritative RF1 activation is 14 EVs/34 contrasts/0-mm FEAT smoothing. Every active task EV, including `C_neu`, has per-EV temporal filtering disabled. The isolated historical `C_neu` setting was normalized to 0 by explicit decision on 2026-09-04. Historical aging vectors and archived templates remain provenance, not active model definitions. |
| Pooled temporal model | Approved and implemented as a deterministic narrow transform of the retained historical FSFs: nine substantive full-trial EVs, convolved optional missed-trial nuisance, 28 activation contrasts, zero FEAT smoothing, and no unsupported decision EVs. PPI uses the same interaction contrasts plus the physiological contrast. |

## Next real-data step

On Linux2, after pulling this repository:

1. catch up target smoothing and analysis-input QC for the two `sub-12032` runs;
2. rebuild event and ratings audits from the current upstream sources;
3. generate and audit the ds003745 FSL nuisance matrices;
4. rebuild the final task/ratings manifests and generate three-column EVs;
5. run the cross-dataset activation-plus-PPI pilot, then the paired full L1 batch;
6. audit L1 and run paired fixed effects for two-run subjects, retaining explicit L1 passthrough for one-run subjects;
7. cross-check final-model residual smoothness before pooled inference and keep pooled L3 out of scope.
