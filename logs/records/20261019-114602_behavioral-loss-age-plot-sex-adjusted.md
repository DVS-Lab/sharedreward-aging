# Run Record: behavioral-loss-age-plot-sex-adjusted

- Timestamp: 20261019-114602
- Branch: main
- Commit: d26161b
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-114602_behavioral-loss-age-plot-sex-adjusted.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: direct paired loss-slope tests completed with and without recorded sex.

## Command

```bash
/Users/tug87422/fsl/bin/python3 code/analyze_loss_rating_age.py 
```

## Log

```text
RUN START: 20261019-114602
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main d26161b
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: /Users/tug87422/fsl/bin/python3 code/analyze_loss_rating_age.py 

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
  "ratings_policy": "within_partner_loss_gt_win_primary_2026-10-01",
  "design": "Intercept + continuous centered age per decade + dataset dummy, with/without recorded-sex M/O offsets (F reference).",
  "inference": "Wide multivariate OLS with HC3 covariance retaining within-participant covariance; paired slope differences with t CIs/tests. Joint 2-df Wald chi-square test.",
  "multiplicity": "Holm across all three pairwise partner loss-slope comparisons within each specification. Separately Holm across three individual loss slopes. Exploratory follow-up, not experiment-wide control.",
  "interpretation": "Positive loss slope means less negative ratings at older ages. Positive Friend-minus-X slope means a larger age slope for Friend than X.",
  "exclusions": "Unchanged primary behavior-only sample; no imaging QC or extra ceiling/floor exclusions.",
  "figure": "Sex-adjusted model only. Dataset/sex held at empirical sample mix; age varied over observed range. Pointwise HC3 t confidence bands for means, not simultaneous or prediction intervals. Raw units, zoomed y axis; no raw scatter.",
  "limitations": [
    "Cross-sectional, not causal age effects.",
    "Loss floors and response-based eligibility remain interpretive limitations.",
    "Failure to reject slope differences is not evidence of equivalence."
  ],
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/analyze_loss_rating_age.py",
      "sha256": "d98c205e860580b3a0a52905a14069cf09c316a709aa29cb78635590d15e05ef"
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
      "path": "/Users/tug87422/github/sharedreward-aging/code/plot_rating_age.py",
      "sha256": "71580f76a2f4a5cc13c8e1613444933d8a2d82ba047f9a66f79a25ccde2c46ef"
    }
  ]
}
 sex_adjusted                        family               comparison   n  points_per_decade   se_hc3  ci95_low  ci95_high  df_t        p  p_holm_three     chi2  df_chi2
         True    individual_loss_age_slopes                   Friend 318           0.190383 0.072302  0.048124   0.332643 313.0 0.008879      0.024374      NaN      NaN
         True    individual_loss_age_slopes                 Stranger 318           0.103591 0.057072 -0.008702   0.215883 313.0 0.070466      0.070466      NaN      NaN
         True    individual_loss_age_slopes                 Computer 318           0.146143 0.054861  0.038200   0.254086 313.0 0.008125      0.024374      NaN      NaN
         True paired_loss_slope_differences    Friend minus Stranger 318           0.086793 0.063607 -0.038360   0.211945 313.0 0.173389      0.520168      NaN      NaN
         True paired_loss_slope_differences    Friend minus Computer 318           0.044240 0.080752 -0.114645   0.203125 313.0 0.584184      0.955579      NaN      NaN
         True paired_loss_slope_differences  Stranger minus Computer 318          -0.042553 0.059873 -0.160357   0.075252 313.0 0.477790      0.955579      NaN      NaN
         True     joint_loss_slope_equality Age x partner for losses 318                NaN      NaN       NaN        NaN   NaN 0.344799           NaN 2.129587      2.0
        False    individual_loss_age_slopes                   Friend 318           0.209241 0.071410  0.068741   0.349741 315.0 0.003635      0.010906      NaN      NaN
        False    individual_loss_age_slopes                 Stranger 318           0.110580 0.056971 -0.001512   0.222672 315.0 0.053151      0.053151      NaN      NaN
        False    individual_loss_age_slopes                 Computer 318           0.140611 0.054113  0.034142   0.247079 315.0 0.009804      0.019608      NaN      NaN
        False paired_loss_slope_differences    Friend minus Stranger 318           0.098661 0.061943 -0.023213   0.220536 315.0 0.112214      0.336642      NaN      NaN
        False paired_loss_slope_differences    Friend minus Computer 318           0.068630 0.079550 -0.087886   0.225147 315.0 0.388939      0.777879      NaN      NaN
        False paired_loss_slope_differences  Stranger minus Computer 318          -0.030031 0.060103 -0.148284   0.088222 315.0 0.617664      0.777879      NaN      NaN
        False     joint_loss_slope_equality Age x partner for losses 318                NaN      NaN       NaN        NaN   NaN 0.271714           NaN 2.606012      2.0
CHECK PASSED: direct paired loss-slope tests completed with and without recorded sex.

COMMAND EXIT: 0
```
