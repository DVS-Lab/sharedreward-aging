# Primary behavioral rule and regeneration verification

Date: 2026-10-01. User decision: “regenerate the plots and the stats” and
“lock that in as the primary behavioral rule until cooper says otherwise.”

Policy: exclude the whole participant if any of Computer, Stranger, or Friend
has Loss > Win. Equality remains allowed. Missing/invalid/empty ratings and
all-six-identical ratings do not become eligible. This supersedes the
aggregate-sum rule and is not a retrospective claim about historical code.
The rule was chosen before computing these updated statistics.

Source tables are unchanged Linux2 audit exports. Behavioral decisions were
re-evaluated from their validated six-cell means; source discovery/audit was
not rerun on the Mac. Of 393 task-valid participants, the previous 347 ratings-
qualified participants lose 29 (28 RF1, one ds003745), leaving 318 (285 + 33).
All 318 have canonical demographics. Participant-level joined demographic
inputs remain ignored; only existing-ID eligibility decisions, aggregate
results, plots, and provenance are tracked.

Execution records:

- `20261001-231616_raw-ratings-primary-within-partner.md`: statistics and bar plot, exit 0.
- `20261001-231837_raw-ratings-primary-within-partner-age-plots.md`: pooled age plots, exit 0.

Both executions used the modified working tree based on `4ed1152`; recorded
code hashes in the generated provenance files identify the exact analysis
and policy code, rather than implying the parent commit alone contains it.

Verification:

- All 318 retained participants satisfy Loss <= Win for each partner.
- Six cell slopes, HC3 standard errors, and p-values match independent
  statsmodels OLS(HC3, use_t=True) calculations.
- All seven exploratory paired age-slope contrasts match independent
  participant-level difference regressions: estimates, HC3 SEs, p-values,
  and 95% confidence intervals (rtol 1e-10, atol 1e-12).
- Twelve old result/figure files in `qc/ratings-raw/archive-aggregate-rule-n347/`
  match their `4ed1152` Git blobs byte-for-byte. Earlier records remain intact.
- All three regenerated PNGs visually reviewed: readable labels, raw rating
  scales, SEM or CI distinguished, correct n=318 and pre-imaging-QC labels.
- Bash/Python syntax and the full 87-test suite passed. An initial test-loader
  import failure after adding the shared policy helper was corrected by
  adding the code directory to the cohort test's import path, then rerunning.
- Whitespace review is scoped to source/docs: generated TSV trailing empty
  cells and Matplotlib SVG path whitespace are intentional, not stripped.

No L1/L2 templates/workers, imaging data, model outputs, or shared task-valid
manifests were changed. Future ratings-qualified manifest construction now
re-evaluates the primary rule even from an older aggregate-rule audit. Existing
frozen ratings manifests are historical until rebuilt and must not supersede
`qc/ratings-raw/behavioral-eligibility.tsv` for the current behavioral analysis.
