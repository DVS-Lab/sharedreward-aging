# Shared Reward exclusion policy

This document operationalizes the recurring exclusion scheme in the lab's Shared Reward preregistrations without treating historical scripts as authoritative code.

## Run-level criteria

- High motion: mean framewise displacement above `Q3 + 1.5 × IQR`, calculated separately by dataset.
- Low signal quality: tSNR below `Q1 - 1.5 × IQR`, calculated separately by dataset.
- Low anatomical coverage: fixed-mask overlap below `Q1 - 1.5 × IQR`, calculated separately by dataset.
- Poor task compliance: missed trials strictly greater than 25% of all trials in the run.

The imaging metrics are review flags until the complete cohort distributions have been inspected. Fixed rules such as coverage below 90% or more than 20% of volumes with FD above 0.5 mm are not registered exclusion criteria and are disabled by default. FD-above-0.5-mm counts remain useful descriptive diagnostics.

## Metric implementation

This Phase 0 implementation measures tSNR from the final `desc-smoothToFWHM6_bold` file that will enter FEAT, rather than copying the MRIQC tSNR IQM. That deliberate analysis-input definition must be reported as such. Mean FD comes from the named fMRIPrep `desc-confounds_timeseries.tsv`. The headerless Tedana-plus-confounds matrix remains the RF1 L1 nuisance input and is not parsed positionally for QC.

Coverage preserves the historical Shared Reward exemption for inferior cerebellum and posterior brainstem. The tracked historical `masks/cerebellum-brainstem_mask.nii.gz` is nearest-neighbor resampled to the RF1 grid and subtracted from the full TemplateFlow mask. Coverage is the fraction of this fixed eligible mask covered by the run mask. This is algebraically cleaner than unioning the exemption into every run mask and preserves one common denominator across runs and datasets. The full TemplateFlow mask remains the fixed whole-brain tSNR reference; the coverage exemption is not silently applied to tSNR or to future statistical analysis masks.

## Missed trials and model structure

Missed-trial fractions are calculated from the model-specific harmonized full-trial events, not from a glob over legacy three-column files. Retained runs model each miss as a single full-trial nuisance EV, spanning the recoverable full trial. The nine partner-by-feedback EVs remain the substantive model. Runs with a zero-count substantive condition are surfaced for design review before L1 and are not silently reclassified.

## Run-to-subject aggregation

A run can be removed while another run from the same participant remains usable. A participant is excluded for run-level quality/task-compliance criteria only when no usable runs remain. Dataset-specific L2 fixed-effects models must consume only retained runs and record whether one or two runs contributed.

Additional analysis-specific exclusions—such as missing questionnaire data, impossible rating patterns, zero rating variability, age restrictions, or missing WMH/ADI variables—belong to the corresponding hypothesis-level cohort and must not be baked into the shared imaging preprocessing gate.

The recurring Shared Reward ratings gate is nevertheless audited alongside cohort construction because it is subject-level and applies to both runs: missing/empty ratings, identical ratings across all six partner-by-outcome cells, or aggregate loss ratings strictly greater than aggregate win ratings. Equality is allowed. RF1 ratings remain in the authoritative tracked `rf1-sra/stimuli/Scan-Card_Guessing_Game/logs` source and are referenced rather than copied here. The modern audit reads both the original `Partner`/`Trait`/`Rating` schema and the normalized lowercase schema, never drops rows by position, requires all six expected cells, and preserves source hashes and raw cell means/counts. When a tracked file contains pre- and post-scan blocks separated by a repeated header, the audit recognizes the header boundary, validates the final six-cell block, selects that post-scan block, and records the number and selected index of blocks. Missing/empty sources become explicit exclusions. Genuine ambiguity remains a hard stop unless resolved in `docs/ratings_source_resolutions.tsv`; the sole current resolution selects RF1 sub-10369's post-scan/session-2 file, matching the historical workflow's effective source without its unsafe positional deletion.
