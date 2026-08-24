# Quality-control figures

This directory contains small, reproducible cross-dataset QC figures and the compact numerical summaries used to draw them. Large per-run derivatives remain under ignored `derivatives/qc/`; auditable run-level tables and run records remain under `logs/records/`.

- `smoothness-comparison_mean-sem.png`: measured classic combined FWHM for the unsmoothed analysis input, approved AFNI 6-mm total target, and FEAT-equivalent nominal 6-mm SUSAN control. Bars are run-level means and error bars are run-level standard errors.
- `smoothness-comparison_mean-sem.tsv`: exact values underlying the plotted bars.
- `analysis-input-qc_mean-sem.png`: generated after the full post-smoothing tSNR/motion/coverage audit.
- `tsnr-vs-mean-fd.png`: run-level tSNR-motion relationship, colored by dataset.
- `coverage-mosaics/`: selected low-coverage run masks in translucent red over each final smoothed run's mean-BOLD anatomy. The dashed yellow boundary is the unchanged coverage-eligible mask. Generate these with `code/plot_coverage_mosaics.py`; the compact provenance and slice list belong in `logs/records/coverage-mosaics.tsv`.

Regenerate the smoothness figure with `code/plot_smoothness_comparison.py` from the tracked complete SUSAN audit.
