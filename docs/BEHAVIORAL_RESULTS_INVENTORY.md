# Behavioral results inventory

Reviewed 2026-10-18 against repository state `228a0fb` and the canonical local
copy of RF1 `bids/participants.tsv`. The current primary behavioral analysis
is **raw post-task ratings in 318 people**, not z-scored ratings and not the
290-person imaging-plus-ratings subset. Its results were reproduced from the
source audit tables during this review. Cooper has since completed imaging
exclusions; those do not automatically change the ratings-only population.

## Populations and policy

| Population | RF1 | ds003745 | Total | Purpose |
|---|---:|---:|---:|---|
| Task-valid starting inventory | 346 | 47 | 393 | Before imaging QC |
| Current primary ratings analysis | 285 | 33 | 318 | Ratings-only behavior |
| Cooper retained imaging cohort | 315 | 43 | 358 | 663 retained runs |
| Imaging and ratings eligible | 260 | 30 | 290 | Future brain–behavior analyses |

Primary eligibility excludes the participant if **any partner's loss rating
exceeds that partner's win rating**. Equality is allowed. Missing, invalid,
incomplete and all-six-identical ratings remain excluded. This is the user's
2026-10-01 decision until Cooper revises it; it is not a claim that the old
aggregate rule implemented the same policy. The rule is response-based, which
can affect estimated associations.

Sources: [ratings eligibility](../qc/ratings-raw/behavioral-eligibility.tsv),
[behavioral provenance](../qc/ratings-raw/provenance.json), and
[Cooper cohort summary](../logs/records/exclusion-ledger/summary.tsv).

## Available current results

All primary age estimates below pool datasets, adjust for dataset and recorded
sex, and use continuous age per decade. HC3 covariance accounts for
heteroskedasticity; paired-condition tests use the within-person covariance.
These are cross-sectional associations, not causal aging effects.

### Six ratings and individual age slopes

Raw scale: −5 to +5. SEM describes the mean; the last column is Holm-adjusted
over the six age slopes, not a test of each mean against zero.

| Condition | Mean ± SEM | Rating points per decade | Adjusted p |
|---|---:|---:|---:|
| Computer win | 1.830 ± 0.126 | −0.018 | 1.000 |
| Computer loss | −1.503 ± 0.105 | +0.146 | .0487 |
| Stranger win | 2.660 ± 0.108 | +0.038 | 1.000 |
| Stranger loss | −1.720 ± 0.102 | +0.104 | .2819 |
| Friend win | 4.318 ± 0.075 | −0.026 | 1.000 |
| Friend loss | −2.531 ± 0.142 | +0.190 | .0487 |

Sources: [means and SEM](../qc/ratings-raw/raw-ratings-means-sem.tsv),
[six age slopes and confidence intervals](../qc/ratings-raw/age-slopes.tsv).
Plots: [six-condition bars](../qc/ratings-raw/raw-ratings-six-conditions.png),
[six age panels](../qc/ratings-raw/raw-ratings-by-age-six-panels.png),
[overall age plot](../qc/ratings-raw/raw-ratings-by-age-overall.png).

### Joint age tests

The six-outcome omnibus is χ²(6)=14.284, p=.0266. In the four-term decomposition,
Holm-adjusted p-values are .0613 for the overall mean, .0802 for age×outcome,
.9458 for age×partner, and .4036 for age×partner×outcome. Thus the omnibus is
positive, but none of those four decomposed terms crosses .05 after correction.

Source: [joint tests](../qc/ratings-raw/age-tests.tsv). The same file also
contains pooled dataset-only adjustment and within-dataset sensitivity fits;
the primary result remains pooled, not a comparison of which dataset has a
significant p-value.

### Paired follow-ups

| Age effect on a within-person difference | Points per decade | Adjusted p | Family |
|---|---:|---:|---|
| Computer loss minus win | +0.164 | .1601 | Three partner gaps |
| Stranger loss minus win | +0.066 | .4606 | Three partner gaps |
| Friend loss minus win | +0.217 | .0309 | Three partner gaps |
| Friend minus stranger, wins | −0.064 | .5311 | Four friend–stranger tests |
| Friend minus stranger, losses | +0.087 | .5202 | Four friend–stranger tests |
| Friend minus stranger, mean | +0.011 | .7833 | Four friend–stranger tests |
| Friend minus stranger, win-minus-loss gap | −0.151 | .3781 | Four friend–stranger tests |

The friend loss-minus-win slope has pointwise 95% CI [.052, .382]. It indicates
a smaller win–loss separation at older ages. The friend–stranger results do
not establish equivalence; they simply do not provide convincing evidence of
different age slopes. These follow-up families and the six-cell family are
separate exploratory corrections, not one experiment-wide error guarantee.

Source: [paired follow-up estimates and intervals](../qc/ratings-raw/age-exploratory-contrasts.tsv).

### Ceiling and recorded sex sensitivity

The 2026-10-19 sensitivity check retains the identical 318 people and primary
behavioral exclusions. Friend wins have a substantial ceiling: 223/318 (70.1%)
are +5, compared with 86/318 (27.0%) stranger wins and 65/318 (20.4%) computer
wins. Friend losses also have a floor: 104/318 (32.7%) are −5. Endpoint responses
are retained, not treated as invalid or removed in a selected-subset analysis.

The primary design is an intercept, continuous centered age per decade, an RF1
dataset dummy, and recorded-sex offsets (M and O, reference F). Recorded sex is
186 F, 129 M and 3 O; it is not verified gender identity. There are no age-by-sex
interactions, motion or tSNR covariates in this behavioral-only model.

| Adjustment | Friend win age slope | Friend loss age slope | Friend win minus loss slope (95% CI) | Gap Holm p |
|---|---:|---:|---|---:|
| Dataset and recorded sex | −0.026 | +0.190 | −0.217 [−0.382, −0.052] | .0309 |
| Dataset only | −0.036 | +0.209 | −0.246 [−0.411, −0.080] | .0112 |

Slopes are raw rating points per decade. Gap p-values correct over the three
partner gaps separately within each adjustment model. About 88% of the primary
friend gap point estimate comes algebraically from the loss slope, not the win
slope; this decomposition is not a causal attribution. Friend-win ceiling
membership changes by +1.14 percentage points per decade after dataset/sex
adjustment (HC3 95% CI −1.72 to +3.99; unadjusted p=.434). This does not establish
that latent preferences are age invariant.

A bounded-mean sensitivity uses [fractional logit](https://www.nber.org/papers/t0147)
on (rating+5)/10 with endpoints included. Average age derivatives are returned to
the original rating scale. Paired participant-level sandwich covariance (HC1)
and a delta method conditional on the observed covariates give 95% normal CIs.
The dataset/sex-adjusted friend gap derivative is −0.210 [−0.368, −0.053],
Holm p=.0260. Without sex it is −0.241 [−0.400, −0.083], Holm p=.0086.
This models the observed bounded mean, not latent uncensored ratings.

Interpretation: the observed friend gap narrows mainly because losses are rated
less negatively at older ages, and this result is similar with or without sex
adjustment and in the bounded-mean sensitivity. The ceiling still prevents a
strong interpretation of the flat win slope. Differences among partners' gap
slopes remain uncertain (joint p=.202 in the primary model; .212 in the bounded
sensitivity). These are exploratory sensitivity checks, not independent
replications or an experiment-wide multiplicity correction.

Sources: [endpoint counts](../qc/ratings-raw/ceiling-sensitivity/endpoint-prevalence.tsv),
[endpoint age tests](../qc/ratings-raw/ceiling-sensitivity/endpoint-age-tests.tsv),
[model comparisons](../qc/ratings-raw/ceiling-sensitivity/age-sensitivity-tests.tsv),
[figure](../qc/ratings-raw/ceiling-sensitivity/ceiling-sex-sensitivity.png), and
[methods and source hashes](../qc/ratings-raw/ceiling-sensitivity/provenance.json).
Reproduce with `python code/check_ratings_ceiling.py`; this does not modify the
primary eligibility rule, previous figures or imaging inputs.

## Other available behavioral material

| Material | Current status | Location |
|---|---|---|
| Ratings source/cell audit | Selected files, block choice, cell means and source hashes; eligibility is superseded by the current within-partner rule where necessary | `logs/records/ratings-qc-subject-level.tsv`; `docs/ratings_source_resolutions.tsv` |
| Task performance/event QC | 766 audited runs in this export; 19 exceed 25% misses. RF1 787/35,915 missed trials; ds003745 532/7,200. This is the characterization inventory, **not** the 663-run post-QC cohort | `logs/records/fulltrial-event-qc-run-level.tsv`; subject-level companion |
| Trial-level inputs | Full-trial event derivatives and source provenance are on Linux2; event-QC counts are available locally | `derivatives/harmonized/events/` on Linux2 |
| Historical ratings analyses | Aggregate-rule N=347 and incomplete-demographics N=237 are archived, not current primary results | `qc/ratings-raw/archive-aggregate-rule-n347/`; `preliminary-local-age/` |
| Historical brain–behavior models | R Markdown/HTML analyses of extracted clusters, age, z-scored ratings and other covariates; not regenerated against the current cohort/models | `code/plotting/` |

The historical plotting notebooks include DLPFC NPPI, MTG activation, and an
age×friend-minus-stranger z-rating model with motion, tSNR, study and `flip`
covariates. They must not be presented as current raw-rating or current
post-QC brain results. Their cluster-selected extractions are not independent
ROIs for the new age tests. No current validated inferential output for task
reaction times, closeness, or financial-exploitation questionnaires was found
in this repository review; source availability and a model specification
would need checking before adding those analyses.

## Next imaging analysis

The [preliminary age analysis](PRELIMINARY_AGE_ANALYSIS.md) uses the 358-person
imaging cohort, not the 318-person behavioral cohort or 290-person overlap.
It tests activation and provisional VS-PPI without using ratings as a
covariate. A brain–ratings association would be a separate analysis with its
own hypothesis and sample; it is not implied by a parallel age effect.
