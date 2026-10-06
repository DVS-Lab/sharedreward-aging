# Raw ratings and age analysis

Decision, 2026-10-01: use the original post-scan ratings, not within-person
z-scores, for the updated behavioral analysis. The six cells are Computer,
Stranger, Friend x Win, Loss. Ratings range from -5 (negative) to +5 (positive).
Mapping is verified in the original `SR_postRatings.py`: partner 1/2/3 =
computer/stranger/friend; trait 0/1 = win/loss.

The old `code/archive/exclusions-2026-02/08_zscore_ratings.py` standardized each participant's
six cells jointly. This removes between-person mean differences and divides
each person's condition differences by their own rating SD. That answers a
relative-profile question rather than the present raw-rating age question.
The legacy scripts/notebooks remain historical; do not use their z-score
columns as the updated behavioral results or automatically propagate them
into new L3 models. This change does not modify or invalidate the completed
categorical L1/PPI/L2 analyses.

Lebreton et al. (2019), *Assessing inter-individual differences with task-related
functional neuroimaging*, Nature Human Behaviour 3, 897-905,
https://doi.org/10.1038/s41562-019-0681-8, Fig. 2 and pp. 901-903, explains why
scaling changes the meaning of individual-difference analyses under different
neural coding assumptions. It is not a blanket recommendation against all
standardization. Our behavioral rationale is to retain observable differences
in rating level and range on their common original scale.

## Current analysis

Primary eligibility decision, 2026-10-01: exclude the **whole participant**
if Loss > Win for **any** partner (Computer, Stranger, or Friend). Equality
is allowed; all-six-identical and missing/invalid ratings remain ineligible.
This rule is primary until Cooper says otherwise, not a sensitivity analysis.
The user chose it before the revised statistics were calculated. It supersedes
the aggregate-sum implementation; this is not a claim that historical code
already applied the within-partner rule.

`code/analyze_raw_ratings.py` reads the current source-validated raw cell means
from `logs/records/ratings-qc-subject-level.tsv`. It uses one row per participant
in the current task-valid, ratings-qualified cohort: **318 people (285 RF1,
33 ds003745)**, before Cooper's imaging-QC exclusions. The new rule removes
29 additional people (28 RF1, one ds003745) from the previous 347. A participant
with two usable fMRI runs does not contribute their ratings twice. This
is an imaging-aligned behavioral sample, not every person with any ratings.

`qc/ratings-raw/behavioral-eligibility.tsv` records decisions for all 393
task-valid participants; `additional-ratings-exclusions.tsv` identifies the
29 additional exclusions. The original Linux2 source audit and frozen imaging
manifests were not overwritten. Both the behavioral loader and future cohort
construction enforce the new rule from validated cell means, so stale ratings
eligibility flags cannot restore participants. No FEAT models or shared
task-valid imaging membership changed.

The six-bar displays show means +/- between-person SEM for the combined
sample and each dataset separately. The full -5 to +5 scale and zero baseline
are shown. These descriptive error bars are not within-person contrast CIs.

Age is continuous, expressed per decade without z-scoring ratings. The primary
exploratory model fits the six responses jointly with an intercept, centered
age/10, dataset, and recorded sex (categorical F/M/O, retaining O as recorded).
Each condition has its own
dataset and sex coefficients. It is a wide multivariate linear regression,
not six independent observations per person or a random-intercept-only model.
The covariance of the six age slopes retains within-person residual
cross-products and uses HC3 leverage correction. The omnibus test asks whether
any of the six age slopes differs from zero (Wald chi-square, 6 df).

Secondary tests decompose age into the mean across cells, age x outcome,
age x partner, and age x partner x outcome; their four p-values receive Holm
correction. Six condition-specific age slopes have pointwise 95% t intervals
and a separate six-test Holm correction. Dataset-adjusted/no-sex and
within-dataset fits are sensitivity analyses, not alternative primary tests
selected for significance. Wald tests use an asymptotic reference distribution.
The six slopes and their HC3 standard errors, plus three subject-level
contrasts, were independently checked against statsmodels on the observed data:
https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html.

Interpret age associations as cross-sectional and exploratory. Bounded ratings,
ceiling effects, nonlinear age patterns, and selection on rating responses
remain considerations for a publication analysis. Missing age/sex is reported,
never imputed; participant-level joined inputs/missingness remain under ignored
`derivatives/behavioral/`, not added to Git. Aggregate outputs and source hashes
are recorded under `qc/ratings-raw/`.

## Primary within-partner-rule results, 2026-10-01

All 318 retained participants have age and recorded sex. The pooled dataset-
and sex-adjusted omnibus age test gives chi-square(6)=14.2843, p=0.026617.
The overall mean slope is +0.07228 raw points/decade (pointwise 95% CI
0.01363 to 0.13092), but does not survive the established four-term Holm
correction (p=0.061275). Corrected interaction p-values are outcome 0.080187,
partner 0.945756, and partner x outcome 0.403587. Thus the global six-response
age association is detectable; none of the four decomposition tests crosses
0.05 after correction. The pooled model remains primary regardless of the
significance of separate-dataset sensitivity fits.

Previously requested direct comparisons are exploratory, stored in
`age-exploratory-contrasts.tsv`. The Friend Loss-minus-Win age slope is
+0.21679 points/decade (95% CI 0.05153 to 0.38205; raw p=0.010303;
Holm across three partners p=0.030908): Friend loss ratings become less
negative with age relative to Friend win ratings. The direct Friend-minus-
Stranger age slopes are -0.06438 for wins and +0.08679 for losses; their
Holm p-values are 0.531114 and 0.520168. Neither their mean nor their
Win-minus-Loss differential is significant (four-comparison Holm p=0.783343
and 0.378090). These follow-ups do not establish a general partner-by-age
interaction, and were not promoted to primary tests based on their results.

Selection uses the same ratings being analyzed and can influence their age
associations. This user-selected primary cohort is not yet Cooper's final
imaging-QC cohort. Raw cell means, the linear model, confidence intervals,
and previously used correction families are otherwise unchanged.

## Superseded aggregate-rule results (n=347), 2026-10-01

The following is retained as historical provenance, not the current primary
analysis. Its twelve result/figure files were moved intact to
`qc/ratings-raw/archive-aggregate-rule-n347/`; historical run records still
describe their original paths. Current top-level results use 318 participants.

The canonical RF1 BIDS participant table was copied from Linux2 and its SHA256
matched the verified September 27 export:
`10004009f83ae3ffd9977941e6c222ac8f1aabfd70f41968470cfaa70ef35ca4`.
All **347** ratings-qualified participants now have age and recorded sex:
313 RF1 and 34 ds003745, with zero missing demographics. Current aggregate
results live directly in `qc/ratings-raw/`; `preliminary-local-age/` preserves
the earlier, superseded incomplete-demographics analysis for provenance.

The primary dataset- and sex-adjusted model gives a six-slope age omnibus
Wald chi-square(6)=15.8429, p=0.014622. The mean across six conditions increases
by **0.09310 raw points per decade** (pointwise 95% CI 0.03644 to 0.14975;
four-component Holm-adjusted p=0.004920). Age interactions do not survive that
correction: outcome p=0.290361, partner p=0.772361, and partner x outcome
p=0.324190. This is an association with chronological age, not longitudinal
evidence of a change within people.

The raw-rating bar plot is unchanged: it already included all 347 participants.
The age result supersedes the earlier estimate of 0.13652 points per decade
from only 237 people using historical RF1 demographics. Both the expanded sample
and the authoritative demographic source changed; do not attribute the numerical
change solely to adding participants.

Within-dataset sensitivity matters: the RF1-only mean slope is 0.06056 points
per decade (Holm p=0.134692), versus 0.27628 in ds003745 (Holm p=0.015597,
n=34). A difference in significance is not a test of slope heterogeneity.
Do not describe the pooled association as independently established in both
datasets. Dataset-by-age interactions, nonlinear age, and ceiling effects
remain useful sensitivity questions before publication; they are not tested
by changing the primary result after seeing its p-value.

The execution record is
`logs/records/20261001-224447_raw-ratings-full-demographics.md`.
Participant demographics remain ignored and are not committed to Git.

Full-cohort verification: all six slopes/HC3 standard errors and three
within-person contrasts matched independent statsmodels calculations
(relative tolerance 1e-11, absolute tolerance 1e-12). An initial relative-only
check flagged a 3.3e-15 numerical difference for a near-zero slope; no estimates
or analysis code were changed. All four behavioral unit tests passed. The
raw-rating summary table and rendered PNG are identical to the earlier plot.

## Demographic coverage history and rerun

### Preliminary age figures

`code/plot_rating_age.py` produces pooled six-condition age panels and a
companion plot of each participant's mean across six ratings. Both explicitly
precede Cooper's imaging-QC exclusions. Points are unadjusted raw ratings with
horizontal-only display jitter (+/-0.35 years, fixed seed); actual ages are
used for fitting. No IDs are embedded in the figures. No new exclusions,
separate-dataset trend lines, or new hypothesis tests are introduced by the
plotting script. It uses the same primary within-partner eligibility as the
statistics script.

The fitted lines use the same pooled additive age/dataset/recorded-sex design
as the primary analysis, averaged over the observed dataset/sex proportions
at each age. Shading is a pointwise 95% HC3 t confidence interval for the
adjusted mean, not an interval covering individual observations. The mean
panel is fit to participant-level means, retaining within-person covariance.
All six condition panels share the original -5 to +5 rating scale; the overall
mean panel has a separately labeled scale covering every observed mean.
The linear trends span the observed age range and do not imply uniform age
coverage or establish longitudinal change. Aggregate prediction curves and
source hashes accompany the PNG/SVG files in `qc/ratings-raw/`.

```bash
bash code/run_logged.sh --label raw-ratings-age-plots --include-full-log -- \
  "$IMAGING_PYTHON" code/plot_rating_age.py
```

### Historical demographic subset

The local historical `participants-rf1.tsv` has only 245 rows and lacks 110
of the 313 current RF1 ratings-qualified participants. It is not an adequate
full-cohort demographic source. Explicitly labeled local preliminary results
may use 237 participants (203 RF1 + 34 ds003745); the raw descriptive plot still
uses all 347. Do not present those age results as the full cohort's findings.
The canonical RF1 baseline participants file generated and verified on
Linux2 is now available locally and was used for the full-cohort rerun above.
The current pipeline refuses partial demographic coverage unless
`--allow-partial-age` is explicitly supplied.

Linux2 (activate `sharedreward-phase0` first):

```bash
bash code/run_logged.sh --label raw-ratings-age --include-full-log -- \
  "$IMAGING_PYTHON" code/analyze_raw_ratings.py \
  --rf1-participants /ZPOOL/data/projects/rf1-sra-linux2/bids/participants.tsv \
  --output-dir qc/ratings-raw
```

Commit aggregate QC results and the run record, not the participant-level
demographic input/derivative. Do not rerun FEAT for this behavioral update.
