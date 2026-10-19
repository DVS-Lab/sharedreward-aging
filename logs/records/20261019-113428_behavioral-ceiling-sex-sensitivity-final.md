# Run Record: behavioral-ceiling-sex-sensitivity-final

- Timestamp: 20261019-113428
- Branch: main
- Commit: 4d2b928
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-113428_behavioral-ceiling-sex-sensitivity-final.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: ceiling/sex sensitivities completed on the identical primary behavioral sample.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/check_ratings_ceiling.py 
```

## Log

```text
RUN START: 20261019-113428
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 4d2b928
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/check_ratings_ceiling.py 

{
  "n": 318,
  "sample_by_dataset": {
    "ds003745": 33,
    "rf1": 285
  },
  "recorded_sex_counts": {
    "F": 186,
    "M": 129,
    "O": 3
  },
  "task_valid_n": 393,
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "design": "Intercept + centered continuous age per decade + RF1 dataset dummy; with/without recorded sex M/O dummy offsets (F reference).",
  "exclusions": "Same primary behavioral exclusions; no MRI QC, no exclusion of ceiling/floor responses.",
  "bounded_sensitivity": "Fractional logit of (rating+5)/10, endpoints included; average age derivative on original scale. Paired sandwich HC1 and delta method conditional on observed covariates; normal CIs.",
  "endpoint_tests": "Linear-probability HC3 slopes in percentage points/decade. Six tests (win ceilings and loss floors), Holm within each adjustment specification.",
  "multiplicity": "Separate exploratory Holm families of 6 condition slopes, 3 gaps, 3 paired gap differences per model; no experiment-wide claim.",
  "limitations": [
    "Does not identify latent preferences above/below scale boundaries.",
    "Bounded mean sensitivity is not an ordinal or censored-latent model.",
    "Response-based eligibility may affect associations; no causal aging interpretation.",
    "Recorded sex O category has only 3 participants; this is not a test of sex moderation or verified gender identity."
  ],
  "reference": "https://www.nber.org/papers/t0147",
  "sources": [
    {
      "path": "/Users/tug87422/github/sharedreward-aging/logs/records/ratings-qc-subject-level.tsv",
      "sha256": "dc13ec845d927cb66f41139d54b2bce37ee3efbbb3b62466034ee3bd7f6488ed"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/logs/records/analysis-subject-dispositions.tsv",
      "sha256": "e30a4c33fc4adf18fc62bdeaada0360851086b66c9fd24d03f73e67c83ae7616"
    },
    {
      "path": "/Users/tug87422/github/rf1-sra-linux2/bids/participants.tsv",
      "sha256": "10004009f83ae3ffd9977941e6c222ac8f1aabfd70f41968470cfaa70ef35ca4"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/participants-srndna.tsv",
      "sha256": "760730ad4d57f3d5d05ca489620ddead9442380405885b7c84792e413a3dac5e"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/check_ratings_ceiling.py",
      "sha256": "ea5f6e6eec7f5eadb7108d63b01aebce4070b00dc18544b7d578e8a676d6eb96"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_raw_ratings.py",
      "sha256": "20d9e5b53e1da195114b71f5c5cd3b418b89ce4519da93449823dda2614879f7"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/audit_ratings_qc.py",
      "sha256": "49270e365449e66bf4e4375497a4fc574f4946e5481917be3219a235ad3461ef"
    },
    {
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_rating_gaps.py",
      "sha256": "dca61b26005a280c05e3204fdf4e8468c02d2f73d03ea2245c47d0a057bb480b"
    }
  ]
}
                  method  sex_adjusted                       family            comparison   n  points_per_decade       se  ci95_low  ci95_high        p  p_holm_family     chi2  df
                 OLS_HC3          True     six_condition_age_slopes            Friend win 318          -0.026409 0.043327 -0.111658   0.058841 0.542628       1.000000      NaN NaN
                 OLS_HC3          True     six_condition_age_slopes           Friend loss 318           0.190383 0.072302  0.048124   0.332643 0.008879       0.048747      NaN NaN
                 OLS_HC3          True       partner_gap_age_slopes                Friend 318          -0.216792 0.083991 -0.382051  -0.051533 0.010303       0.030908      NaN NaN
                 OLS_HC3          True paired_gap_slope_differences Friend minus Stranger 318          -0.151176 0.090142 -0.328536   0.026184 0.094523       0.283568      NaN NaN
                 OLS_HC3          True     joint_gap_slope_equality  Age x partner on gap 318                NaN      NaN       NaN        NaN 0.201793            NaN 3.201022 2.0
fractional_logit_AME_HC1          True     six_condition_age_slopes            Friend win 318          -0.024770 0.040806 -0.104747   0.055207 0.543833       1.000000      NaN NaN
fractional_logit_AME_HC1          True     six_condition_age_slopes           Friend loss 318           0.185661 0.069346  0.049746   0.321575 0.007421       0.043208      NaN NaN
fractional_logit_AME_HC1          True       partner_gap_age_slopes                Friend 318          -0.210431 0.080153 -0.367528  -0.053333 0.008656       0.025968      NaN NaN
fractional_logit_AME_HC1          True paired_gap_slope_differences Friend minus Stranger 318          -0.145488 0.088287 -0.318527   0.027552 0.099374       0.298123      NaN NaN
fractional_logit_AME_HC1          True     joint_gap_slope_equality  Age x partner on gap 318                NaN      NaN       NaN        NaN 0.212067            NaN 3.101704 2.0
                 OLS_HC3         False     six_condition_age_slopes            Friend win 318          -0.036388 0.042974 -0.120940   0.048163 0.397772       1.000000      NaN NaN
                 OLS_HC3         False     six_condition_age_slopes           Friend loss 318           0.209241 0.071410  0.068741   0.349741 0.003635       0.021813      NaN NaN
                 OLS_HC3         False       partner_gap_age_slopes                Friend 318          -0.245630 0.084065 -0.411030  -0.080230 0.003731       0.011192      NaN NaN
                 OLS_HC3         False paired_gap_slope_differences Friend minus Stranger 318          -0.155080 0.089247 -0.330677   0.020516 0.083251       0.249752      NaN NaN
                 OLS_HC3         False     joint_gap_slope_equality  Age x partner on gap 318                NaN      NaN       NaN        NaN 0.215630            NaN 3.068385 2.0
fractional_logit_AME_HC1         False     six_condition_age_slopes            Friend win 318          -0.035283 0.041255 -0.116142   0.045576 0.392419       1.000000      NaN NaN
fractional_logit_AME_HC1         False     six_condition_age_slopes           Friend loss 318           0.205896 0.068745  0.071159   0.340634 0.002744       0.016463      NaN NaN
fractional_logit_AME_HC1         False       partner_gap_age_slopes                Friend 318          -0.241180 0.080879 -0.399700  -0.082659 0.002864       0.008592      NaN NaN
fractional_logit_AME_HC1         False paired_gap_slope_differences Friend minus Stranger 318          -0.151421 0.087912 -0.323725   0.020882 0.084992       0.254977      NaN NaN
fractional_logit_AME_HC1         False     joint_gap_slope_equality  Age x partner on gap 318                NaN      NaN       NaN        NaN 0.222233            NaN 3.008057 2.0
 sex_adjusted   condition endpoint   n    status  percentage_points_per_decade  ci95_low  ci95_high        p  p_holm_six
         True  Friend win  ceiling 318 estimated                      1.137026 -1.719728   3.993779 0.434149    1.000000
         True Friend loss    floor 318 estimated                     -2.043642 -4.739871   0.652588 0.136878    0.684388
        False  Friend win  ceiling 318 estimated                      0.912804 -1.921884   3.747493 0.526823    1.000000
        False Friend loss    floor 318 estimated                     -2.159418 -4.806636   0.487799 0.109502    0.594898
CHECK PASSED: ceiling/sex sensitivities completed on the identical primary behavioral sample.

COMMAND EXIT: 0
```
