# Raw ratings and age analysis

Decision, 2026-10-01: use the original post-scan ratings, not within-person
z-scores, for the updated behavioral analysis. The six cells are Computer,
Stranger, Friend x Win, Loss. Ratings range from -5 (negative) to +5 (positive).
Mapping is verified in the original `SR_postRatings.py`: partner 1/2/3 =
computer/stranger/friend; trait 0/1 = win/loss.

The old `code/exclusions/08_zscore_ratings.py` standardized each participant's
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

`code/analyze_raw_ratings.py` reads the current source-validated raw cell means
from `logs/records/ratings-qc-subject-level.tsv`. It uses one row per participant
in the current task-valid, ratings-qualified cohort: 347 people (313 RF1,
34 ds003745), before Cooper's imaging-QC exclusions. A participant with two
usable fMRI runs does not contribute their ratings twice. Existing ratings
exclusions are unchanged (including strict loss > win, not equality). This
is an imaging-aligned behavioral sample, not every person with any ratings.

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

## Demographic coverage and rerun

The local historical `participants-rf1.tsv` has only 245 rows and lacks 110
of the 313 current RF1 ratings-qualified participants. It is not an adequate
full-cohort demographic source. Explicitly labeled local preliminary results
may use 237 participants (203 RF1 + 34 ds003745); the raw descriptive plot still
uses all 347. Do not present those age results as the full cohort's findings.
Use the canonical RF1 baseline participants file generated and verified on
Linux2. The current pipeline refuses partial demographic coverage unless
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
