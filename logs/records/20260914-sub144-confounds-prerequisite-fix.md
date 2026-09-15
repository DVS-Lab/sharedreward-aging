# Sub-144 preparation: missing nuisance-matrix prerequisite

Reviewed the Linux2 record `20260914-233534_sub144-corrected-events-prepare.md`
from commit `30b9cfa`. All 765 harmonized event derivatives and their audit
passed. Preparation then stopped at the cohort builder's first missing
ds003745 FSL nuisance matrix (sub-104 run-01). This is not an event-recovery
failure and does not establish that the source fMRIPrep confounds are missing.

The recovery orchestrator previously omitted the established ds003745
named-confounds-to-headerless-FSL conversion prerequisite. It now builds that
manifest, generates missing matrix/metadata pairs, and runs the volume-alignment
audit with `--fail-on-incomplete` before freezing the cohort. No `--overwrite`
is passed; existing pairs are retained and audited. RF1 upstream nuisance
matrices and all imaging preprocessing remain unchanged.

The same explicit ds003745 output root is supplied to both the converter
manifest and the cohort builder, including when `FSL_DERIVATIVES_ROOT` is set.
Regression tests cover command order, root consistency, preservation of
existing pairs, and stopping before cohort construction when the audit fails.

Validation is recorded separately in the local test run. Linux2 preparation
must be retried; no Linux2 conversion or model execution is claimed here.
