# Raw ratings: local descriptive plot and preliminary age analysis

Date: 2026-10-01. Source checkout: main, 6ffef27, with the new behavioral
analysis script in this commit. No FEAT worker, model, template, or cohort
exclusion was changed.

## Executed command

```bash
MPLCONFIGDIR=/tmp/sharedreward-ratings-mpl PYTHONDONTWRITEBYTECODE=1 \
  /Users/tug87422/fsl/bin/python3 code/analyze_raw_ratings.py \
  --rf1-participants participants-rf1.tsv \
  --allow-partial-age \
  --age-source-label 'Historical repository RF1 table; incomplete, pending canonical Linux2 demographics' \
  --output-dir qc/ratings-raw/preliminary-local-age
```

Exit: 0. Script/input SHA256 hashes are in the output provenance.json.
The bundled workspace Python lacks plotting dependencies; the existing local
FSL Python provided numpy, pandas, scipy, matplotlib, and statsmodels.

## Results and limitation

- Raw mean +/- SEM plots: 347 distinct ratings-qualified, task-valid participants,
  313 RF1 and 34 ds003745; no within-person z-scoring and no new imaging-QC exclusion.
- Age analysis: **preliminary subset only**, 237 participants (203 RF1, 34 ds003745).
  The historical RF1 demographic table lacks 110 eligible participants. The four
  RF1 participants with recorded sex O are retained as their own category.
- Primary continuous-age, dataset- and sex-adjusted multivariate model: six-slope
  omnibus Wald chi-square(6)=19.7220, p=0.003103.
- Mean across six conditions: +0.13652 rating points per decade, pointwise 95% CI
  0.06977 to 0.20327; four-component Holm-adjusted p=0.000223.
- No age interaction survives the four-component correction: outcome p=0.833797,
  partner p=0.833797, partner x outcome p=0.187675 (adjusted values).
- These are cross-sectional exploratory associations in a response-selected,
  incomplete-demographics sample, not a definitive full-cohort age result.
- Full-cohort rerun requires the current Linux2 RF1 BIDS participants.tsv.
  The default command refuses incomplete demographic coverage.

## Verification

- Visually inspected the three-panel PNG: raw -5 to +5 scale, six cell means,
  between-participant SEM, correct dataset counts, one contribution per person.
- All six slopes and HC3 standard errors agree with statsmodels OLS HC3 to
  relative tolerance 1e-11. Three within-person contrast slopes and standard
  errors also agree, checking the cross-outcome covariance.
- `code/validate_workflow.sh`: bash syntax PASS, Python syntax PASS,
  **84 tests passed**, including four new raw-ratings tests.
- Participant-level joined demographic inputs and missingness stay in ignored
  derivatives/behavioral/raw-ratings; only aggregate figures, results, and
  provenance are committed.

See docs/RAW_RATINGS_ANALYSIS.md for the rationale, paper citation, assumptions,
and Linux2 full-demographics rerun command. No FEAT rerun is needed.
